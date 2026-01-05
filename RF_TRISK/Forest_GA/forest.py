# coding=utf-8
import pickle
from warnings import warn
import os

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble.forest import MAX_INT, _parallel_build_trees
from sklearn.exceptions import DataConversionWarning
from sklearn.externals.joblib import Parallel, delayed
from sklearn.tree._tree import issparse, DOUBLE, DTYPE
from sklearn.utils import check_array, check_random_state

from Forest_GA.PIBIC.ga import GeneticAlgorithm, Consultas, PrintExcelGA, Arquive
from Forest_GA.PIBIC.h_l2rMeasures import modelEvaluation, getGeoRisk, getRisk, getTRisk, getQueries


class Forest(RandomForestRegressor):
    rota = ""   ## Rota de Qual fold esta rodando

    size = 1000
    nameFile = "forest"
    treesName = ".All.Trees.pickle"
    Fold = 1        ## Somente para impressaao

    def fit_forest(self, geracao, VetorTrain, VetorVali, mode="ndcg"):
        ''' ENTRADA: Geração de N individuos,
                TESTA: para cada se ele ja possui fitness,
                RETURN: se não possuir atribui o fitness para cada individuo
                
        Carregando para memória todas as arvores criadas pelo fit '''
        all_trees = self.get_Trees("all")

        if all_trees == 0:
            self.fit(VetorTrain.x, VetorTrain.y)  ## Para criar as arvores iniciais de cada fold
            all_trees = self.get_Trees("all")

        forest = np.ones(self.size)

        self.fitLoadTrees(VetorTrain.x, VetorTrain.y, forest, all_trees)  ## Carregar as asvores de cada fold
        base_pred = self.predict(VetorVali.x)

        base_ndcg, base_map = modelEvaluation(VetorVali, base_pred, 64)

        g_temp = []
        for ind in geracao:

            if ind.bool_fit != 1:

                self.fitLoadTrees(VetorTrain.x, VetorTrain.y, ind.get_fita(), all_trees)        ## Carregar as asvores de cada fold
                scores = self.predict(VetorVali.x)

                valor_ndgc, map = modelEvaluation(VetorVali, scores, 64)

                if mode == "ndcg":
                    ind.set_fitness(np.mean(valor_ndgc))
                    ind.set_map(np.mean(map))
                elif mode == "tRisk":
                    trisk = getTRisk(valor_ndgc, base_ndcg, 5)
                    ind.set_fitness(trisk)

                ind.bool_fit = 1
            g_temp.append(ind)

        return g_temp

    def ga(self, Vet_Train_Vali, max_num_geracoes=30, n_treesForest=75, selecaoTorneio=1, crossoverUniforme=1, elitist=1, numero_genes=1000, mode="ndcg"):
        ''' Função GA Principal, chamada Pela função Externa
            ENTRADA: n_forest= Numero de Individuos na Floresta,
                     max_num_geracoes= Quantidade de Gerações,
                     elitist= Controle se Há ou não (1,0) presença de Elitismo,
                     selecaoTorneio= Controle se a Seleção e por Torneio ou Roleta (1,0),
                     crossoverUniforme= Controle se e por Crossover Uniforme ou Pontual (1,0),
                     numero_genes= Numero de Genes / Numero de Arvores total

            SAIDA:

            PRINT:

        '''

        [VetorTrain, VetorVali] = Vet_Train_Vali

        GA = GeneticAlgorithm([], 1)
        GA.num_caracteristicas = numero_genes
        GA.tamanho_populacao = n_treesForest

        ''' Elitismo'''
        GA.elitist = elitist
        ''' Crossover'''
        GA.bool_crossoverUniforme_Ponto = crossoverUniforme
        ''' Selecao'''
        GA.bool_selecaoTorneio_Roleta = selecaoTorneio

        ''' Geração Inicial'''
        geracao_temp = GA.GenerateInicial()
        geracao_inicial = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)  ## Geração com Fitness


        ''' Bagging'''

        bag = Arquive(n_treesForest * 2)
        bag.type = geracao_inicial[0].__class__
        bag.appendBag(geracao_inicial)

        ''' Iteracao + 1 para fitar a ultima geracao'''
        for numero_da_geracao in range(1, max_num_geracoes + 1):

            if numero_da_geracao < max_num_geracoes:
                ''' função GA, externa, recebe geracao com fitness, numero da geracao'''
                geracao_temp = GA.GA(geracao_inicial, numero_da_geracao + 1)
            if numero_da_geracao >= max_num_geracoes:
                geracao_temp = geracao_inicial

            geracao_nova_com_fit = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)  ## Geração com Fitness
            geracao_temp = []

            ''' Agrupamento de Geracao com ou sem Elistia'''
            populacao = []
            if GA.elitist == 1:
                populacao = GA.ElitistGroup(geracao_inicial, geracao_nova_com_fit)
            else:
                populacao = geracao_nova_com_fit
            geracao_inicial = []
            geracao_inicial = populacao
            geracao_nova_com_fit = []

            bag.appendBag(populacao)


            vetorGA = str(selecaoTorneio)+str(crossoverUniforme)+'1'+str(elitist)

            PrintExcelGA(self.Fold, numero_da_geracao, populacao, vetorGA)

        ''' Fim do GA, temos a Geração Final, com todos os melhores Candidatos'''
        ''' Loop somente para garantir estar retornando o melhor do bagging'''

        The_Best = bag.getBag(1)
        The_Best.bool_fit = 0

        # The_Best = self.fit_forest([The_Best], VetorTrain, VetorTest, mode="ndcg")

        return The_Best

    def get_Trees(self, maskList="all"):

        self.rota = 'Fold' + str(self.size)  + '/'
        try:
            os.mkdir(self.rota)
        except OSError:
            n = 0

        fileCache = self.rota + self.nameFile + '_Fold' + str(self.Fold) + self.treesName
        trees = []

        if not(os.path.isfile(fileCache)):
            return 0

        with open(fileCache, 'rb') as handle:
            trees = pickle.load(handle)

        n_forest = []

        if maskList == "all":
            maskList = np.ones(self.n_estimators)
            return trees
        elif maskList == "chess":
            maskList = np.zeros(self.n_estimators)
            for i in range(self.n_estimators):
                if not (i % 2):
                    maskList[i] = 1

        colAllFeat = 0
        for aTree in trees:
            if maskList[colAllFeat] == 1:
                n_forest.append(aTree)
            colAllFeat = colAllFeat + 1

        return n_forest

    def fitLoadTrees(self, X, y, forest, all_trees, sample_weight=None):

        ''' Montando floresta (individuo) apartir das arvores ja criadas'''
        trees = []
        for t in range(len(forest)):
            if forest[t] == 1:
                trees.append(all_trees[t])

        self.n_estimators = len(trees)
        self.estimators_ = trees

        # Validate or convert input data
        X = check_array(X, accept_sparse="csc", dtype=DTYPE)
        y = check_array(y, accept_sparse='csc', ensure_2d=False, dtype=None)
        if sample_weight is not None:
            sample_weight = check_array(sample_weight, ensure_2d=False)
        if issparse(X):
            # Pre-sort indices to avoid that each individual tree of the
            # ensemble sorts the indices.
            X.sort_indices()

        # Remap output
        n_samples, self.n_features_ = X.shape

        y = np.atleast_1d(y)
        if y.ndim == 2 and y.shape[1] == 1:
            warn("A column-vector y was passed when a 1d array was"
                 " expected. Please change the shape of y to "
                 "(n_samples,), for example using ravel().",
                 DataConversionWarning, stacklevel=2)

        if y.ndim == 1:
            # reshape is necessary to preserve the data contiguity against vs
            # [:, np.newaxis] that does not.
            y = np.reshape(y, (-1, 1))

        self.n_outputs_ = y.shape[1]

        y, expanded_class_weight = self._validate_y_class_weight(y)

        if getattr(y, "dtype", None) != DOUBLE or not y.flags.contiguous:
            y = np.ascontiguousarray(y, dtype=DOUBLE)

        if expanded_class_weight is not None:
            if sample_weight is not None:
                sample_weight = sample_weight * expanded_class_weight
            else:
                sample_weight = expanded_class_weight

        # Check parameters
        self._validate_estimator()

        if not self.bootstrap and self.oob_score:
            raise ValueError("Out of bag estimation only available"
                             " if bootstrap=True")

        self.estimators_ = trees
        self.n_estimators = len(trees)

        if self.oob_score:
            self._set_oob_score(X, y)

        # Decapsulate classes_ attributes
        if hasattr(self, "classes_") and self.n_outputs_ == 1:
            self.n_classes_ = self.n_classes_[0]
            self.classes_ = self.classes_[0]

        return self

    def fit(self, X, y, sample_weight=None):
        """Build a forest of trees from the training set (X, y).
                Parameters
                ----------
                X : array-like or sparse matrix of shape = [n_samples, n_features]
                    The training input samples. Internally, its dtype will be converted to
                    ``dtype=np.float32``. If a sparse matrix is provided, it will be
                    converted into a sparse ``csc_matrix``.
                y : array-like, shape = [n_samples] or [n_samples, n_outputs]
                    The target values (class labels in classification, real numbers in
                    regression).
                sample_weight : array-like, shape = [n_samples] or None
                    Sample weights. If None, then samples are equally weighted. Splits
                    that would create child nodes with net zero or negative weight are
                    ignored while searching for a split in each node. In the case of
                    classification, splits are also ignored if they would result in any
                    single class carrying a negative weight in either child node.
                Returns
                -------
                self : object
                    Returns self.
                """

        # Picke variable to control

        self.MAX_FOLD = self.n_estimators
        self.rota = "Fold" + str(self.size) + "/"

        try:
            os.mkdir(self.rota)
        except OSError:
            print('.')

        self.nameFile = "forest"

        # Validate or convert input data
        X = check_array(X, accept_sparse="csc", dtype=DTYPE)
        y = check_array(y, accept_sparse='csc', ensure_2d=False, dtype=None)
        if sample_weight is not None:
            sample_weight = check_array(sample_weight, ensure_2d=False)
        if issparse(X):
            # Pre-sort indices to avoid that each individual tree of the
            # ensemble sorts the indices.
            X.sort_indices()

        # Remap output
        n_samples, self.n_features_ = X.shape

        y = np.atleast_1d(y)
        if y.ndim == 2 and y.shape[1] == 1:
            warn("A column-vector y was passed when a 1d array was"
                 " expected. Please change the shape of y to "
                 "(n_samples,), for example using ravel().",
                 DataConversionWarning, stacklevel=2)

        if y.ndim == 1:
            # reshape is necessary to preserve the data contiguity against vs
            # [:, np.newaxis] that does not.
            y = np.reshape(y, (-1, 1))

        self.n_outputs_ = y.shape[1]

        y, expanded_class_weight = self._validate_y_class_weight(y)

        if getattr(y, "dtype", None) != DOUBLE or not y.flags.contiguous:
            y = np.ascontiguousarray(y, dtype=DOUBLE)

        if expanded_class_weight is not None:
            if sample_weight is not None:
                sample_weight = sample_weight * expanded_class_weight
            else:
                sample_weight = expanded_class_weight

        # Check parameters
        self._validate_estimator()

        if not self.bootstrap and self.oob_score:
            raise ValueError("Out of bag estimation only available"
                             " if bootstrap=True")

        random_state = check_random_state(self.random_state)

        if not self.warm_start or not hasattr(self, "estimators_"):
            # Free allocated memory, if any
            self.estimators_ = []

        n_more_estimators = self.n_estimators - len(self.estimators_)

        if n_more_estimators < 0:
            raise ValueError('n_estimators=%d must be larger or equal to '
                             'len(estimators_)=%d when warm_start==True'
                             % (self.n_estimators, len(self.estimators_)))

        elif n_more_estimators == 0:
            warn("Warm-start fitting without increasing n_estimators does not "
                 "fit new trees.")
        else:
            if self.warm_start and len(self.estimators_) > 0:
                # We draw from the random state to get the random state we
                # would have got if we hadn't used a warm_start.
                random_state.randint(MAX_INT, size=len(self.estimators_))

            trees = []
            for i in range(n_more_estimators):
                tree = self._make_estimator(append=False,
                                            random_state=random_state)
                trees.append(tree)

            # Parallel loop: we use the threading backend as the Cython code
            # for fitting the trees is internally releasing the Python GIL
            # making threading always more efficient than multiprocessing in
            # that case.
            trees = Parallel(n_jobs=self.n_jobs, verbose=self.verbose,
                             backend="threading")(
                delayed(_parallel_build_trees)(
                    t, self, X, y, sample_weight, i, len(trees),
                    verbose=self.verbose, class_weight=self.class_weight)
                for i, t in enumerate(trees))

            ##            for fold in range(0, MAX_FOLD):
            ##                fileCache = nameFile + str(fold) + " .Objectives.test.pickle"
            fileCache = self.rota + self.nameFile + '_Fold' + str(self.Fold) + self.treesName

            with open(fileCache, 'wb') as pFile:
                pickle.dump(trees, pFile)

            # Collect newly grown trees
            self.estimators_.extend(trees)

        if self.oob_score:
            self._set_oob_score(X, y)

        # Decapsulate classes_ attributes
        if hasattr(self, "classes_") and self.n_outputs_ == 1:
            self.n_classes_ = self.n_classes_[0]
            self.classes_ = self.classes_[0]

        return self