# coding=utf-8
# RF_TRISK - Random Forest com Algoritmo Genético otimizado por métrica TRISK
# Arquivo principal: coordena execução de GA para cada fold

import time                                       # Para medir tempo de execução
import numpy as np                                # Computação numérica
import os                                         # Operações do sistema

from sklearn.externals.joblib._multiprocessing_helpers import mp  # Multiprocessing

# Importações locais - Classes GA
from Forest_GA.PIBIC.ga import Individuo, Consultas  # Indivíduo e Consultas (dados)
# Importações locais - Utilitários
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file  # Carrega dados LETOR
# Importações locais - Floresta Aleatória
from Forest_GA.forest import Forest              # Wrapper RandomForest + GA


def main():
    # Ponto de entrada do programa - coordena execução
    comparar = 0                              # Flag: 1=testar RF individual sem GA, 0=desativar
    executar_por_fold = 1                     # Flag: 1=ATIVAR execução GA por fold, 0=desativar
    executar_threads = 0                      # Flag: 1=execução paralela, 0=execução sequencial

    rota_pasta_letor = "../Colecoes/2003_td_dataset/"  # Caminho para dataset LETOR
    numero_de_estimadores = 1000              # Número total de árvores na floresta inicial

    ################################################ Aplicar MultThread GA #######################################

    # Bloco 1: Executa GA para cada fold (principal)
    if executar_por_fold:
        # Chama folds_works com parâmetros GA: [selecao, crossover, elitismo]
        check = folds_works([1, 1, 1], rota_pasta_letor,30, 75 , 10000, "tRisk")  # [torneio=1, uniforme=1, elitismo=1]
        if(check == 1):
            print("finished")                 # Mensagem sucesso se tudo correr bem

    ################################################ Testar o GA ################################################

    # Bloco 2: Teste individual - compara RF original vs otimizado (desativado por padrão)
    # Bloco 2: Teste individual - compara RF original vs otimizado (desativado por padrão)
    if comparar:
        # Inicializa Floresta Aleatória com 1000 árvores
        RandomForest = Forest(n_estimators=numero_de_estimadores, n_jobs=4)  # n_jobs=4 para paralelismo

        # Comentário: Parâmetros da classe Forest (estendida de RandomForestRegressor)
        # bootstrap=True: amostras com reposição
        # criterion='mse': erro quadrado médio como critério split
        # max_depth=2: profundidade máxima 2
        # max_features='auto': raiz(n_features) como max features
        # n_estimators=1000: número de árvores
        # n_jobs=4: usar 4 processadores em paralelo

        fold = "1"                                        # Fold específico para teste (1-5)
        # Máscara: vetor binário pré-definido [0,1,...,1] onde 1=usar árvore, 0=descartar
        # Para teste, usar máscara customizada ao invés de aleatória
        forest = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0]

        # Caminhos dos arquivos de dados para o fold
        nomeArquivoTrain = rota_pasta_letor + "Fold" + fold + "/Norm.train.txt"  # Treino
        nomeArquivoVali = rota_pasta_letor + "Fold" + fold + "/Norm.vali.txt"    # Validação
        nomeArquivoTest = rota_pasta_letor + "Fold" + fold + "/Norm.test.txt"    # Teste

        MASK = [1] * 64                       # Máscara: usar todos os 64 atributos

        print("Lendo Arquivos ...")
        # load_L2R_file(): carrega arquivo LETOR, retorna (features, targets, query_groups)
        X, y, z = load_L2R_file(nomeArquivoTrain, MASK)   # Features, targets, groups treino
        X2, y2, z2 = load_L2R_file(nomeArquivoVali, MASK) # Features, targets, groups validação
        X3, y3, z3 = load_L2R_file(nomeArquivoTest, MASK) # Features, targets, groups teste

        # Cria objetos Consultas com dados e informação de grupos (queries)
        Vetores_Train = Consultas(X, y, z)                # Dados de treino
        Vetores_Vali = Consultas(X2, y2, z2)              # Dados de validação
        Vetores_Test = Consultas(X3, y3, z3)              # Dados de teste

        # Cria indivíduo com máscara pré-definida para teste
        ind = Individuo(forest, 1)                        # Individuo(máscara, fitness_calculado)
        RandomForest.Fold = int(fold)                     # Define fold atual na floresta
        RandomForest.size = numero_de_estimadores         # Define tamanho total

        # Mede tempo de execução
        start = time.clock()                              # Tempo inicial

        # Treina floresta e calcula fitness do indivíduo
        ger = RandomForest.fit_forest([ind], Vetores_Train, Vetores_Test)  # Retorna [ind_com_fitness]

        final = time.clock() - start                      # Tempo decorrido

        # Salva resultado (fitness = tempo decorrido em segundos)
        imprimir_individuo(ger[0], numero_de_estimadores, 1, 1, fold, [0, 0, 0], final)

    # Bloco 3: Execução paralela com múltiplas configurações (desativado por padrão)
    if executar_threads:
        # Vetores de parâmetros para testar múltiplas configurações
        ex_vetor_n_arvores = [1000]           # [1000,2000,3000] para teste maior
        ex_geracoes = [30]                    # [30, 50, 100] gerações por teste
        ex_n_individuos = [75]                # [50, 75, 100] indivíduos por geração

        # Testa todas as combinações em paralelo
        for gg in ex_geracoes:                # Para cada número de gerações
            for ii in ex_n_individuos:        # Para cada tamanho população
                # Cria lista de processos (um por n_arvores testado)
                processes = [
                    mp.Process(
                        target=folds_works,   # Função executar
                        args=([1, 1, 1], rota_pasta_letor, gg, ii, nn, "tRisk")
                    ) for nn in ex_vetor_n_arvores
                ]

                for p in processes:           # Inicia todos os processos
                    p.start()

                for p in processes:           # Aguarda finalização
                    p.join()


def folds_works(ga, rota_pasta_letor, n_geracoes, n_individuos, n_arvores, mode="ndcg"):
    """
    Processa todos os folds (1-5) com Algoritmo Genético
    
    Args:
        ga: [selecaoTorneio, crossoverUniforme, elitismo] - operadores GA booleanos
        rota_pasta_letor: caminho para dataset LETOR
        n_geracoes: número de gerações do GA
        n_individuos: tamanho população por geração
        n_arvores: número total de árvores (genes)
        mode: modo métrica ("ndcg" ou "tRisk")
    
    Returns:
        1 se sucesso, 0 se erro
    """
    MASK = [1] * 64                          # Máscara: usar todos os 64 atributos

    forest = Forest(n_estimators=n_arvores, n_jobs=4)  # Inicializa floresta
    
    # Desempacota parâmetros GA do vetor
    selecaoTorneio = ga[0]                   # 1=torneio, 0=roleta
    crossoverUniforme = ga[1]                # 1=uniforme, 0=ponto
    elitist = ga[2]                          # 1=com elitismo, 0=sem

    # Loop para cada fold (5 folds x-validation)
    for fold in range(1, 6):                 # Fold 1 a 5
        # Constrói caminhos para os arquivos de cada fold
        name_train = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.train.txt"  # Treino
        name_vali = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.vali.txt"    # Validação
        name_test = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.test.txt"    # Teste

        # Carrega dados LETOR de treino, validação e teste
        X, y, z = load_L2R_file(name_train, MASK)       # Features, targets, groups treino
        X2, y2, z2 = load_L2R_file(name_vali, MASK)     # Features, targets, groups validação
        X3, y3, z3 = load_L2R_file(name_test, MASK)     # Features, targets, groups teste

        # Cria estruturas Consultas para cada conjunto
        Vetores_train = Consultas(X, y, z)              # Dados treino + grupos
        Vetores_Vali = Consultas(X2, y2, z2)            # Dados validação + grupos
        Vetores_Test = Consultas(X3, y3, z3)            # Dados teste + grupos

        # Configura propriedades da floresta para este fold
        forest.Fold = fold                               # Define fold atual
        forest.n_estimators = n_arvores                  # Reconfirma número árvores
        forest.size = n_arvores                          # Reconfirma tamanho

        # Trata dois casos: GA (n_geracoes > 1) ou RF original (n_geracoes == 1)
        if n_geracoes == 1:
            # Caso especial: usar todas as árvores (sem GA)
            geracao = np.ones(n_arvores)                 # Máscara [1,1,1,...,1]
            IndNatural = Individuo(geracao, 1)           # Cria indivíduo natural
            individuo = forest.fit_forest([IndNatural], Vetores_train, Vetores_Test, mode="ndcg")  # Avalia
            imprimir_individuo(individuo[0], n_arvores, n_geracoes, n_individuos, fold, ga)  # Salva

        else:
            # Caso padrão: executar Algoritmo Genético completo
            # forest.ga() retorna melhor indivíduo após n_geracoes
            IndTheBest = forest.ga(
                [Vetores_train, Vetores_Vali],           # Dados treino + validação
                n_geracoes,                              # Gerações
                n_individuos,                            # Indivíduos por geração
                selecaoTorneio,                          # Operador seleção
                crossoverUniforme,                       # Operador crossover
                elitist,                                 # Operador elitismo
                n_arvores,                               # Número genes
                mode                                     # Métrica (tRisk ou ndcg)
            )
            # Avalia melhor indivíduo GA no conjunto teste
            individuo = forest.fit_forest([IndTheBest], Vetores_train, Vetores_Test, mode="ndcg")  # Retorna [ind]
            imprimir_individuo(individuo[0], n_arvores, n_geracoes, n_individuos, fold, ga)  # Salva

    return 1                                 # Sucesso


def imprimir_individuo(individuo, num_arvores, num_geracao, total_geracao, fold, ga, time=0):
    """
    Salva resultado de um indivíduo em arquivo CSV
    
    Args:
        individuo: instância Individuo com fitness e máscara
        num_arvores: número total de árvores
        num_geracao: número de gerações (1=RF original, >1=GA)
        total_geracao: tamanho população
        fold: número do fold (1-5)
        ga: [selecao, crossover, elitismo]
        time: tempo decorrido (para teste com comparação)
    """
    
    try:
        os.mkdir('FinalResultados')          # Cria diretório se não existir
    except OSError:
        pass                                 # Diretório já existe, continua

    map = individuo.map                      # Obtém MAP do indivíduo

    # Determina nome arquivo baseado tipo teste
    if time != 0:
        # Teste com comparação de tempo (original sem GA)
        arquivo_name = 'FinalResultados/Compare_' + str(num_arvores) + '.csv'
        map = time                           # Substitui MAP por tempo
    elif num_geracao == 1:
        # RF original sem GA
        arquivo_name = 'FinalResultados/Original_' + str(num_arvores) + '.csv'
    else:
        # Resultado GA otimizado
        arquivo_name = 'FinalResultados/TheBests_' + str(num_arvores) + '.csv'
    
    arquivo = open(arquivo_name, 'a+')      # Abre arquivo em modo append

    # Escreve linha CSV com todos os parâmetros
    arquivo.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};'.format(
        str(fold),                           # Fold (1-5)
        str(num_arvores),                    # Num árvores
        str(individuo.fitness),              # Fitness (TRISK)
        str(map),                            # MAP
        str(num_geracao),                    # Gerações
        str(total_geracao),                  # Indivíduos por geração
        str(individuo.geracao),              # Geração onde foi criado
        str(ga[0]),                          # Seleção (1=torneio)
        str(ga[1]),                          # Crossover (1=uniforme)
        str(ga[2])                           # Elitismo (1=sim)
    ))
    
    # Escreve máscara binária (1000 bits: 1=usar árvore, 0=descartar)
    for i in individuo.mascara:
        arquivo.write(str(int(i)))
    
    arquivo.write("\n")                      # Fim da linha
    arquivo.close()                          # Fecha arquivo


# Documentação dos parâmetros GA (para referência)
'''
    VETORES DE PARÂMETROS:
    
    Parâmetro 1 - Seleção (ga[0]):
        1 = Seleção por Torneio (competição entre indivíduos)
        0 = Seleção por Roleta (proporcional ao fitness)
    
    Parâmetro 2 - Crossover (ga[1]):
        1 = Crossover Uniforme (cada gene 50% de cada pai)
        0 = Crossover Ponto (corte único, herda antes/depois)
    
    Parâmetro 3 - Elitismo (ga[2]):
        1 = Com Elitismo (preserva melhores indivíduos)
        0 = Sem Elitismo (todos podem ser substituídos)
    
    Exemplos:
        [1,1,1] = Torneio + Uniforme + Elitismo (padrão recomendado)
        [0,0,0] = Roleta + Ponto + Sem Elitismo (rápida convergência)
        [1,0,1] = Torneio + Ponto + Elitismo (menos exploração)
'''

if __name__ == '__main__':
    main()
