# coding=utf-8
"""
MÓDULO: forest.py
RESPONSABILIDADE: Gerenciar Random Forest otimizada para seleção de árvores via GA
CLASSE PRINCIPAL: Forest (herança de RandomForestRegressor)
"""

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

from Forest_GA.PIBIC import getParetoFrontierSet, getBestNDCG
from Forest_GA.PIBIC.ga import GeneticAlgorithm, Consultas, PrintExcelGA, Arquive, Individuo
from Forest_GA.PIBIC.h_functionsFilter import obtainDominace, basicStructure
from Forest_GA.PIBIC.h_l2rMeasures import modelEvaluation, getGeoRisk, getRisk, getTRisk, getQueries


class Forest(RandomForestRegressor):
    """
    Extensão da Random Forest para otimização via Algoritmo Genético.
    
    Atributos de classe:
        - rota: Diretório para armazenar cache de árvores (ex: 'Fold1000/')
        - size: Número total de árvores a treinar (ex: 1000)
        - nameFile: Nome base para salvar árvores ('forest')
        - treesName: Sufixo do arquivo pickle ('.All.Trees.pickle')
        - Fold: Número do fold atual em processamento (para logging)
    """
    
    rota = ""   # Diretório onde armazenar/carregar árvores por fold

    size = 1000
    nameFile = "forest"
    treesName = ".All.Trees.pickle"
    Fold = 1    # Número do fold em processamento (usado para criar nomes de arquivo)

    def fit_forest(self, geracao, VetorTrain, VetorVali, mode="ndcg"):
        """
        Avalia fitness de uma geração de indivíduos (GA).
        
        Cada indivíduo é representado por uma máscara binária que seleciona um subset de árvores.
        Para indivíduos sem fitness calculado:
        1. Seleciona árvores conforme máscara
        2. Faz previsão no conjunto de validação
        3. Calcula NDCG (qualidade do ranking)
        4. Calcula TRISK (risco relativo ao baseline)
        
        Se mode="spea2": Calcula dominância Pareto multobjetivo
        
        ENTRADA: 
            - geracao: Lista de Individuo a avaliar
            - VetorTrain: Consultas com dados de treinamento (x, y, q)
            - VetorVali: Consultas com dados de validação (x, y, q)
            - mode: Tipo de fitness ("ndcg", "trisk" ou "spea2")
            
        SAÍDA: geracao com fitness calculado
        """
        all_trees = self.get_Trees("all")

        # Se não existem árvores salvas, treinar Forest com dados de treinamento
        if all_trees == 0:
            self.fit(VetorTrain.x, VetorTrain.y)  # Treina 'size' árvores
            all_trees = self.get_Trees("all")

        # Baseline: usar TODAS as árvores
        forest = np.ones(self.size)

        self.fitLoadTrees(VetorTrain.x, VetorTrain.y, forest, all_trees)
        base_pred = self.predict(VetorVali.x)

        # NDCG do baseline (todas as árvores)
        base_ndcg, _ = modelEvaluation(VetorVali, base_pred, 64)

        g_temp = []
        for ind in geracao:

            # Só avalia se não foi avaliado antes (flag bool_fit == 0)
            if ind.bool_fit != 1:

                # Seleciona subset de árvores conforme máscara do indivíduo
                self.fitLoadTrees(VetorTrain.x, VetorTrain.y, ind.get_fita(), all_trees)
                scores = self.predict(VetorVali.x)

                # Calcula NDCG para este subset
                valor_ndgc, _ = modelEvaluation(VetorVali, scores, 64)

                # Armazena NDCG agregado (média) e por query
                ind.fitnessNDCG = np.mean(valor_ndgc)
                ind.vetFitnessNDCG = valor_ndgc

                # Calcula TRISK (risco relativo ao baseline)
                # Parâmetro 5 = fator de penalidade para degradação
                trisk, vectrisk = getTRisk(valor_ndgc, base_ndcg, 5)

                ind.vetFitnessTrisk = vectrisk
                ind.fitnessTrisk = trisk

                # Marca como avaliado
                ind.bool_fit = 1
            g_temp.append(ind)

        # SPEA2: Cálculo de dominância Pareto multobjetivo
        if mode == "spea2":
            predictionListMean = []      # NDCG agregado de cada indivíduo
            predictionListNoMean = []    # NDCG por query de cada indivíduo

            riskListNoMean = []          # TRISK por query
            riskList = []                # TRISK agregado

            # Coleta métricas de todos os indivíduos
            for i in g_temp:
                ndcg, vetndcg = i.get_fitness(1)
                predictionListMean.append(ndcg)
                predictionListNoMean.append(vetndcg)

                trisk, vettrisk = i.get_fitness(2)
                riskList.append(trisk)
                riskListNoMean.append(vettrisk)

            # Estrutura basicStructure para armazenar métricas de forma padronizada
            prediction = basicStructure()
            prediction.marginal = predictionListMean        # Valores agregados (média)
            prediction.mat = predictionListNoMean           # Matriz (indiv × queries)
            prediction.greaterIsBetter = 1                  # Maior NDCG é melhor
            prediction.pvalue = 1
            prediction.variance = 1

            risk = basicStructure()
            risk.marginal = riskList
            risk.mat = riskListNoMean
            risk.greaterIsBetter = 1                        # Nota: Menor TRISK é melhor
            risk.pvalue = 1
            risk.variance = 1

            # Calcula dominância Pareto: qual indivíduo domina qual
            # Retorna array com fitness SPEA2 para cada indivíduo
            retorno = obtainDominace("prediction", "trisk", "null", prediction, None, risk, None, range(geracao.__len__()), geracao.__len__())
            
            cont = 0
            for i in geracao:
                # fitness SPEA2 = 1 / (número de dominadores + 1)
                if retorno[cont] == 0:
                    i.fitnessSpea2 = 2       # Não é dominado por ninguém
                else:
                    i.fitnessSpea2 = 1 / retorno[cont]
                cont += 1

        return g_temp

    def ga(self, Vet_Train_Vali, max_num_geracoes=30, n_treesForest=75, selecaoTorneio=1, crossoverUniforme=1, elitist=1, numero_genes=1000, mode="ndcg"):
        """
        ALGORITMO GENÉTICO - Função Principal
        
        Executa o processo completo de evolução:
        1. Gera população inicial aleatória
        2. Avalia fitness
        3. Para cada geração: Aplicar operadores genéticos, avaliar, selecionar
        4. Retorna melhor solução encontrada
        
        ENTRADA:
            - Vet_Train_Vali: [VetorTreinamento, VetorValidacao]
            - max_num_geracoes: Quantas gerações evoluir (ex: 30)
            - n_treesForest: Tamanho da população (ex: 75 indivíduos)
            - selecaoTorneio: 1=Torneio, 0=Roleta
            - crossoverUniforme: 1=Uniforme, 0=Um ponto
            - elitist: 1=Usar elitismo, 0=Sem
            - numero_genes: Número de genes/árvores (ex: 1000)
            - mode: Tipo de fitness ("ndcg", "trisk", "spea2")
            
        SAÍDA: Melhor indivíduo encontrado
        """

        [VetorTrain, VetorVali] = Vet_Train_Vali

        # Instancia o GA com população vazia
        GA = GeneticAlgorithm([], 1)

        # Configura parâmetros do GA
        GA.num_caracteristicas = numero_genes
        GA.tamanho_populacao = n_treesForest

        # Operador: Elitismo (preservar melhores da geração anterior)
        GA.elitist = elitist
        # Operador: Tipo de Crossover
        GA.bool_crossoverUniforme_Ponto = crossoverUniforme
        # Operador: Tipo de Seleção
        GA.bool_selecaoTorneio_Roleta = selecaoTorneio

        # === GERAÇÃO INICIAL ===
        geracao_temp = GA.GenerateInicial()
        geracao_inicial = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)

        # === ARQUIVO (Bagging) ===
        # Mantém histórico das melhores soluções encontradas
        tipos = ["ndcg", "trisk", "spea2", "ndcg/ts", "trisk/ts", "spea2/ts"]
        cont = 0
        m = 1
        for t in tipos:
            if t == mode:
                m = cont
            cont += 1

        bag = Arquive(n_treesForest * 2, m)  # Arquivo com máximo 2×população
        bag.type = geracao_inicial[0].__class__
        bag.appendBag(geracao_inicial)

        # === LOOP PRINCIPAL: EVOLUIR ===
        # Iteração +1 para garantir última geração ser avaliada
        for numero_da_geracao in range(1, max_num_geracoes + 1):

            if numero_da_geracao < max_num_geracoes:
                # Aplicar operadores genéticos para gerar nova geração
                geracao_temp = GA.GA(geracao_inicial, numero_da_geracao + 1, mode)
            if numero_da_geracao >= max_num_geracoes:
                # Última geração: não gerar nova, manter a atual
                geracao_temp = geracao_inicial

            # Avaliar fitness da nova geração
            geracao_nova_com_fit = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)
            geracao_temp = []

            # Seleção para próxima geração (com ou sem elitismo)
            populacao = []
            if GA.elitist == 1:
                # Elitismo: combinar gerações anterior e nova, retornar melhores
                populacao = GA.ElitistGroup(geracao_inicial, geracao_nova_com_fit)
            else:
                # Sem elitismo: usar apenas a nova geração
                populacao = geracao_nova_com_fit
            
            geracao_inicial = []
            geracao_inicial = populacao
            geracao_nova_com_fit = []

            # Armazenar população no arquivo histórico
            bag.appendBag(populacao)

            # Registrar resultados da geração
            vetorGA = str(selecaoTorneio)+str(crossoverUniforme)+'1'+str(elitist)
            PrintExcelGA(self.Fold, numero_da_geracao, populacao, vetorGA, m)

        # === FIM DO GA ===
        # Retornar o MELHOR indivíduo encontrado em toda a evolução
        The_Best = bag.getBag(1)
        The_Best.bool_fit = 0

        return The_Best

    def get_Trees(self, maskList="all"):
        """
        Carrega ou retorna subset de árvores do cache.
        
        As árvores são salvas em arquivo pickle para reutilização eficiente.
        
        ENTRADA:
            - maskList: "all" (todas), "chess" (padrão xadrez), ou array 0/1
            
        SAÍDA: Lista de árvores conforme seleção
        """

        # Criar diretório se não existir
        self.rota = 'Fold' + str(self.size) + '/'
        try:
            os.mkdir(self.rota)
        except OSError:
            n = 0

        # Caminho do arquivo de cache
        fileCache = self.rota + self.nameFile + '_Fold' + str(self.Fold) + self.treesName
        trees = []

        # Se arquivo não existe, retornar 0 para sinal de treinar
        if not(os.path.isfile(fileCache)):
            return 0

        # Carregar árvores do arquivo pickle
        with open(fileCache, 'rb') as handle:
            trees = pickle.load(handle)

        n_forest = []

        # Retornar todas as árvores se maskList="all"
        if maskList == "all":
            maskList = np.ones(self.n_estimators)
            return trees
        # Padrão "xadrez": retornar árvores em índices pares
        elif maskList == "chess":
            maskList = np.zeros(self.n_estimators)
            for i in range(self.n_estimators):
                if not (i % 2):
                    maskList[i] = 1

        # Selecionar árvores conforme máscara
        colAllFeat = 0
        for aTree in trees:
            if maskList[colAllFeat] == 1:
                n_forest.append(aTree)
            colAllFeat = colAllFeat + 1

        return n_forest

    def fitLoadTrees(self, X, y, forest, all_trees, sample_weight=None):
        """
        Configura a Forest com um subset de árvores pré-treinadas.
        
        Ao invés de retreinar, apenas seleciona as árvores conforme a máscara
        e as usa para predição. Isto é crucial para eficiência do GA.
        
        ENTRADA:
            - X: Dados de entrada
            - y: Rótulos
            - forest: Array binário [0,1,...,1] indicando quais árvores usar
            - all_trees: Todas as árvores já treinadas
        """

        # Selecionar apenas as árvores indicadas pela máscara
        trees = []
        for t in range(len(forest)):
            if forest[t] == 1:
                trees.append(all_trees[t])

        # Configurar este Forest com o subset selecionado
        self.n_estimators = len(trees)
        self.estimators_ = trees

        # === Validação de dados (código scikit-learn) ===
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
