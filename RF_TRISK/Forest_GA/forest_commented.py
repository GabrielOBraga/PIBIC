# coding=utf-8
# RF_TRISK Forest - Classe Forest com suporte a Algoritmo Genético
# Estende RandomForestRegressor com GA para otimizar seleção de árvores

import pickle                                 # Serialização de objetos (cache árvores)
from warnings import warn                     # Avisos de conversão
import os                                     # Operações sistema

import numpy as np                            # Computação numérica
from sklearn.ensemble import RandomForestRegressor  # Classe base
from sklearn.ensemble.forest import MAX_INT, _parallel_build_trees  # Constantes/funções paralelas
from sklearn.exceptions import DataConversionWarning  # Exceção conversão dados
from sklearn.externals.joblib import Parallel, delayed  # Paralelismo
from sklearn.tree._tree import issparse, DOUBLE, DTYPE  # Tipos dados árvores
from sklearn.utils import check_array, check_random_state  # Validação

# Importações locais - Algoritmo Genético
from Forest_GA.PIBIC.ga import GeneticAlgorithm, Consultas, PrintExcelGA, Arquive
# Importações locais - Métricas
from Forest_GA.PIBIC.h_l2rMeasures import modelEvaluation, getGeoRisk, getRisk, getTRisk, getQueries


class Forest(RandomForestRegressor):
    """
    Wrapper de RandomForestRegressor com suporte a Algoritmo Genético (GA)
    
    Responsabilidades:
    1. Treinar floresta aleatória inicial (fit)
    2. Cachear árvores em pickle para reutilização (get_Trees)
    3. Selecionar subconjuntos árvores (fitLoadTrees)
    4. Avaliar fitness de indivíduos (fit_forest)
    5. Executar loop GA (ga)
    """
    
    rota = ""                                 # Rota para armazenar cache de árvores
    size = 1000                               # Número total de árvores (tamanho genes)
    nameFile = "forest"                       # Nome base arquivos cache
    treesName = ".All.Trees.pickle"           # Sufixo arquivos cache
    Fold = 1                                  # Fold atual (apenas para impressão)

    def fit_forest(self, geracao, VetorTrain, VetorVali, mode="ndcg"):
        """
        Avalia fitness de geração de indivíduos usando dados validação
        
        Args:
            geracao: lista de Individuo com ou sem fitness calculado
            VetorTrain: Consultas com dados treino
            VetorVali: Consultas com dados validação (para avaliação)
            mode: "ndcg"=otimizar NDCG, "tRisk"=otimizar TRISK
        
        Returns:
            lista de Individuo com fitness preenchido
        """
        
        # Carrega todas as árvores do cache (criadas em fit() anterior)
        all_trees = self.get_Trees("all")  # Retorna lista de todas árvores

        # Se não existem árvores em cache, treina floresta inicial
        if all_trees == 0:
            # Treina RandomForest com dataset treino (cria árvores iniciais)
            self.fit(VetorTrain.x, VetorTrain.y)  # VetorTrain.x=features, VetorTrain.y=targets
            all_trees = self.get_Trees("all")     # Recarrega árvores do cache

        # Cria máscara com todas as árvores para baseline
        forest = np.ones(self.size)               # [1,1,1,...,1] usar todas

        # Treina floresta baseline com TODAS as árvores
        self.fitLoadTrees(VetorTrain.x, VetorTrain.y, forest, all_trees)  # Carrega todas
        base_pred = self.predict(VetorVali.x)  # Predição baseline

        # Avalia baseline (NDCG e MAP)
        base_ndcg, base_map = modelEvaluation(VetorVali, base_pred, 64)  # metrics LETOR

        # Loop avaliação de cada indivíduo da geração
        g_temp = []
        for ind in geracao:
            # Pula avaliação se já foi calculada
            if ind.bool_fit != 1:                 # bool_fit=1 significa já avaliado

                # Carrega subconjunto de árvores do indivíduo (máscara GA)
                self.fitLoadTrees(VetorTrain.x, VetorTrain.y, ind.get_fita(), all_trees)  # Carrega subset
                
                # Predição com subconjunto
                scores = self.predict(VetorVali.x)  # Scores validação

                # Avalia métrica NDCG e MAP
                valor_ndgc, map = modelEvaluation(VetorVali, scores, 64)  # Calcula métricas

                # Atribui fitness baseado em modo
                if mode == "ndcg":
                    # Modo NDCG: maximizar NDCG diretamente
                    ind.set_fitness(np.mean(valor_ndgc))  # Mean NDCG
                    ind.set_map(np.mean(map))             # Mean MAP
                elif mode == "tRisk":
                    # Modo TRISK: calcular Trade-off Risk
                    # TRISK = (base - otimizado) / n_folds
                    # Negativo = melhoria, Positivo = degradação
                    trisk = getTRisk(valor_ndgc, base_ndcg, 5)  # 5 folds
                    ind.set_fitness(trisk)                # Set TRISK como fitness

                ind.bool_fit = 1                  # Marca como avaliado
            
            g_temp.append(ind)                  # Adiciona à geração temporária

        return g_temp                           # Retorna geração com fitness

    def ga(self, Vet_Train_Vali, max_num_geracoes=30, n_treesForest=75, selecaoTorneio=1, crossoverUniforme=1, elitist=1, numero_genes=1000, mode="ndcg"):
        """
        Executa Algoritmo Genético completo para otimizar seleção de árvores
        
        Args:
            Vet_Train_Vali: [VetorTrain, VetorVali] - dados treino e validação
            max_num_geracoes: número de gerações (iterações)
            n_treesForest: tamanho população (indivíduos por geração)
            selecaoTorneio: 1=torneio, 0=roleta
            crossoverUniforme: 1=uniforme, 0=ponto
            elitist: 1=com elitismo, 0=sem
            numero_genes: número total de árvores (tamanho máscara)
            mode: "ndcg" ou "tRisk"
        
        Returns:
            melhor Individuo após todas as gerações
        """

        [VetorTrain, VetorVali] = Vet_Train_Vali  # Desempacota dados

        # Inicializa objeto Algoritmo Genético
        GA = GeneticAlgorithm([], 1)  # [], 1 = população vazia, tipo Individuo
        GA.num_caracteristicas = numero_genes     # Número de genes (árvores)
        GA.tamanho_populacao = n_treesForest      # Tamanho população

        # Configura operadores GA
        GA.elitist = elitist                      # Elitismo ativo?
        GA.bool_crossoverUniforme_Ponto = crossoverUniforme  # Tipo crossover
        GA.bool_selecaoTorneio_Roleta = selecaoTorneio      # Tipo seleção

        # Gera população inicial aleatória
        geracao_temp = GA.GenerateInicial()       # Cria n_treesForest indivíduos aleatórios
        
        # Avalia população inicial
        geracao_inicial = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)  # Calcula fitness

        # Bagging: arquivo para rastrear melhor indivíduo de cada geração
        bag = Arquive(n_treesForest * 2)          # Arquivo com capacidade 2x população
        bag.type = geracao_inicial[0].__class__   # Tipo Individuo
        bag.appendBag(geracao_inicial)            # Adiciona população inicial

        # Loop gerações
        for numero_da_geracao in range(1, max_num_geracoes + 1):  # Geração 1 a max_num_geracoes

            # Cria nova geração (exceto na última)
            if numero_da_geracao < max_num_geracoes:
                # Executa operadores GA: seleção, crossover, mutação
                geracao_temp = GA.GA(geracao_inicial, numero_da_geracao + 1)  # Próxima geração
            if numero_da_geracao >= max_num_geracoes:
                # Última geração: mantém a população atual
                geracao_temp = geracao_inicial

            # Avalia nova geração
            geracao_nova_com_fit = self.fit_forest(geracao_temp, VetorTrain, VetorVali, mode)  # Fitness

            geracao_temp = []                     # Limpa temporária

            # Agrupamento de gerações (seleção com/sem elitismo)
            populacao = []
            if GA.elitist == 1:
                # Com elitismo: combina melhores de ambas as gerações
                populacao = GA.ElitistGroup(geracao_inicial, geracao_nova_com_fit)  # Merge + sort
            else:
                # Sem elitismo: apenas nova geração (antiga é descartada)
                populacao = geracao_nova_com_fit

            geracao_inicial = []                  # Limpa geração anterior
            geracao_inicial = populacao           # Nova geração vira atual
            geracao_nova_com_fit = []             # Limpa temporária

            # Adiciona população atual ao bagging (histórico)
            bag.appendBag(populacao)              # Rastreia melhor de cada geração

            # Imprime resultado desta geração em arquivo Excel
            vetorGA = str(selecaoTorneio) + str(crossoverUniforme) + '1' + str(elitist)
            PrintExcelGA(self.Fold, numero_da_geracao, populacao, vetorGA)

        # Fim GA: seleciona melhor indivíduo do bagging
        The_Best = bag.getBag(1)                  # Retorna top 1 do arquivo
        The_Best.bool_fit = 0                     # Reset para re-avaliação se necessário

        return The_Best                           # Retorna melhor indivíduo encontrado

    def get_Trees(self, maskList="all"):
        """
        Carrega árvores do cache (pickle) ou retorna subset
        
        Args:
            maskList: "all"=todas, "chess"=padrão, ou máscara customizada
        
        Returns:
            lista de árvores (ou 0 se não existem no cache)
        """

        # Define caminho para arquivo cache
        self.rota = 'Fold' + str(self.size) + '/'  # Pasta por tamanho floresta
        try:
            os.mkdir(self.rota)                    # Cria pasta se não existir
        except OSError:
            pass                                 # Pasta já existe

        # Nome arquivo: forest_Fold{N}.All.Trees.pickle
        fileCache = self.rota + self.nameFile + '_Fold' + str(self.Fold) + self.treesName
        trees = []

        # Verifica se arquivo existe
        if not(os.path.isfile(fileCache)):
            return 0                              # Não encontrado

        # Carrega árvores do arquivo pickle
        with open(fileCache, 'rb') as handle:
            trees = pickle.load(handle)           # Desserializa árvores

        n_forest = []

        # Filtra árvores baseado em máscara
        if maskList == "all":
            maskList = np.ones(self.n_estimators) # Usa todas
            return trees                          # Retorna todas diretamente
        elif maskList == "chess":
            # Padrão chess: alterna árvores pares e ímpares
            maskList = np.zeros(self.n_estimators)
            for i in range(self.n_estimators):
                if not (i % 2):                   # Se índice par
                    maskList[i] = 1               # Inclui

        # Aplica máscara: seleciona árvores onde mask=1
        colAllFeat = 0
        for aTree in trees:                       # Para cada árvore
            if maskList[colAllFeat] == 1:         # Se máscara permite
                n_forest.append(aTree)            # Adiciona ao subset
            colAllFeat = colAllFeat + 1

        return n_forest                           # Retorna subset

    def fitLoadTrees(self, X, y, forest, all_trees, sample_weight=None):
        """
        Carrega subconjunto de árvores para forest e executa validação
        
        Monta uma floresta a partir de árvores pré-criadas usando máscara binária
        
        Args:
            X: features treino
            y: targets treino
            forest: máscara binária [1,0,1,...] (1=usar árvore)
            all_trees: lista com todas as árvores criadas
            sample_weight: pesos das amostras (opcional)
        """

        # Seleciona árvores baseado em máscara
        trees = []
        for t in range(len(forest)):          # Para cada gene/árvore
            if forest[t] == 1:                # Se máscara permite
                trees.append(all_trees[t])    # Inclui árvore

        # Configura número estimadores para o subconjunto
        self.n_estimators = len(trees)        # Atualiza com novo tamanho
        self.estimators_ = trees              # Define lista de árvores

        # Validação e processamento de input (padrão scikit-learn)
        X = check_array(X, accept_sparse="csc", dtype=DTYPE)  # Valida features
        y = check_array(y, accept_sparse='csc', ensure_2d=False, dtype=None)  # Valida targets
        if sample_weight is not None:
            sample_weight = check_array(sample_weight, ensure_2d=False)  # Valida pesos
        if issparse(X):
            # Pré-ordena índices para eficiência
            X.sort_indices()

        # Extrai dimensões e ajusta formatos
        n_samples, self.n_features_ = X.shape  # Número amostras, features

        y = np.atleast_1d(y)                  # Garante y é array 1D
        if y.ndim == 2 and y.shape[1] == 1:   # Se y é coluna (n, 1)
            warn("A column-vector y was passed when a 1d array was"
                 " expected. Please change the shape of y to "
                 "(n_samples,), for example using ravel().",
                 DataConversionWarning, stacklevel=2)  # Aviso

        if y.ndim == 1:
            # Reshape para garantir contiguidade de memória
            y = np.reshape(y, (-1, 1))

        self.n_outputs_ = y.shape[1]          # Número outputs

        # Validação classe weight
        y, expanded_class_weight = self._validate_y_class_weight(y)

        # Garante tipo DOUBLE para precisão
        if getattr(y, "dtype", None) != DOUBLE or not y.flags.contiguous:
            y = np.ascontiguousarray(y, dtype=DOUBLE)

        # Aplica pesos classe se necessário
        if expanded_class_weight is not None:
            if sample_weight is not None:
                sample_weight = sample_weight * expanded_class_weight
            else:
                sample_weight = expanded_class_weight

        # Validação parâmetros
        self._validate_estimator()            # Verifica parâmetros válidos

        # Verifica combinação OOB score
        if not self.bootstrap and self.oob_score:
            raise ValueError("Out of bag estimation only available"
                             " if bootstrap=True")

        # Define as árvores selecionadas
        self.estimators_ = trees              # Use only selected trees
        self.n_estimators = len(trees)        # Update count

        # Calcula OOB score se solicitado
        if self.oob_score:
            self._set_oob_score(X, y)         # Out-of-bag evaluation

        # Desencapsula atributos classes_ se necessário
        if hasattr(self, "classes_") and self.n_outputs_ == 1:
            self.n_classes_ = self.n_classes_[0]
            self.classes_ = self.classes_[0]

        return self                           # Retorna self

    def fit(self, X, y, sample_weight=None):
        """
        Treina floresta aleatória e cacheia árvores em pickle
        
        Args:
            X: features treino (n_samples, n_features)
            y: targets treino (n_samples,)
            sample_weight: pesos amostra (opcional)
        
        Returns:
            self para chaining
        """

        # Configura propriedades internas
        self.MAX_FOLD = self.n_estimators     # Copia número estimadores
        self.rota = "Fold" + str(self.size) + "/"  # Define pasta

        try:
            os.mkdir(self.rota)               # Cria pasta se não existir
        except OSError:
            pass                              # Pasta já existe

        self.nameFile = "forest"              # Nome base arquivo cache

        # Validação e processamento de input (padrão scikit-learn)
        X = check_array(X, accept_sparse="csc", dtype=DTYPE)  # Features validation
        y = check_array(y, accept_sparse='csc', ensure_2d=False, dtype=None)  # Targets validation
        if sample_weight is not None:
            sample_weight = check_array(sample_weight, ensure_2d=False)
        if issparse(X):
            X.sort_indices()                  # Otimização para sparse

        # Dimensões
        n_samples, self.n_features_ = X.shape

        y = np.atleast_1d(y)
        if y.ndim == 2 and y.shape[1] == 1:
            warn("A column-vector y was passed when a 1d array was"
                 " expected. Please change the shape of y to "
                 "(n_samples,), for example using ravel().",
                 DataConversionWarning, stacklevel=2)

        if y.ndim == 1:
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

        self._validate_estimator()

        if not self.bootstrap and self.oob_score:
            raise ValueError("Out of bag estimation only available"
                             " if bootstrap=True")

        # Random state para reprodutibilidade
        random_state = check_random_state(self.random_state)

        # Inicializa ou resetează estimadores
        if not self.warm_start or not hasattr(self, "estimators_"):
            self.estimators_ = []             # Floresta vazia

        n_more_estimators = self.n_estimators - len(self.estimators_)

        if n_more_estimators < 0:
            raise ValueError('n_estimators=%d must be larger or equal to '
                             'len(estimators_)=%d when warm_start==True'
                             % (self.n_estimators, len(self.estimators_)))

        elif n_more_estimators == 0:
            warn("Warm-start fitting without increasing n_estimators does not "
                 "fit new trees.")
        else:
            # Ajusta random state para warm start
            if self.warm_start and len(self.estimators_) > 0:
                random_state.randint(MAX_INT, size=len(self.estimators_))

            # Cria n_estimators árvores novas
            trees = []
            for i in range(n_more_estimators):
                # Cria estimador (árvore) vazio
                tree = self._make_estimator(append=False,
                                            random_state=random_state)
                trees.append(tree)

            # Paralelismo: treina árvores em paralelo (backend threading)
            # Threading: libera GIL em código Cython → mais eficiente que multiprocessing
            trees = Parallel(n_jobs=self.n_jobs, verbose=self.verbose,
                             backend="threading")(
                delayed(_parallel_build_trees)(
                    t, self, X, y, sample_weight, i, len(trees),
                    verbose=self.verbose, class_weight=self.class_weight)
                for i, t in enumerate(trees))

            # Cacheia árvores em arquivo pickle para reutilização
            fileCache = self.rota + self.nameFile + '_Fold' + str(self.Fold) + self.treesName

            with open(fileCache, 'wb') as pFile:
                pickle.dump(trees, pFile)     # Serializa árvores

            # Adiciona árvores novas ao conjunto
            self.estimators_.extend(trees)

        # Calcula OOB score se solicitado
        if self.oob_score:
            self._set_oob_score(X, y)

        # Desencapsula atributos de classes se necessário
        if hasattr(self, "classes_") and self.n_outputs_ == 1:
            self.n_classes_ = self.n_classes_[0]
            self.classes_ = self.classes_[0]

        return self                           # Retorna self para chaining
