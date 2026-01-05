# coding=utf-8
import time

import numpy as np
import os

from sklearn.externals.joblib._multiprocessing_helpers import mp

from Forest_GA.PIBIC.ga import Individuo, Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
from Forest_GA.forest import Forest

# colecao = "2003_td_dataset"
# colecao = "2004_td_dataset"
colecao = "web10k"

if colecao == "web10k":
    MASK = [1] * 136
if colecao == "2003_td_dataset":
    MASK = [1] * 64

def main():
    comparar = 0
    executar_por_fold = 0
    executar_threads = 1


    rota_pasta_letor = "../Colecoes/" + colecao + "/"
    numero_de_estimadores = 1000

    ################################################ Aplicar MultThread GA #######################################

    if executar_por_fold:
        check = folds_works([1, 1, 1], rota_pasta_letor,30, 75 , 1000, "spea2")  ## terceiro parametro 1, para pegar Base de Teste
        if(check == 1):
            print("finished")

    ################################################ Testar o GA ################################################

    if comparar:
        RandomForest = Forest(n_estimators=numero_de_estimadores, n_jobs=4)

        """
            Forest(bootstrap=True, criterion='mse', max_depth=2,
                   max_features='auto', max_leaf_nodes=None,
                   min_impurity_decrease=0.0, min_impurity_split=None,
                   min_samples_leaf=1, min_samples_split=2,
                   min_weight_fraction_leaf=0.0, n_estimators=1000, n_jobs=1,
                   oob_score=False, random_state=0, verbose=0, warm_start=False)
        """

        fold = "1"
        forest = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0]

        nomeArquivoTrain = rota_pasta_letor + "Fold" + fold + "/Norm.train.txt"
        nomeArquivoVali = rota_pasta_letor + "Fold" + fold + "/Norm.vali.txt"
        nomeArquivoTest = rota_pasta_letor + "Fold" + fold + "/Norm.test.txt"


        print("Lendo Arquivos ...")
        X, y, z = load_L2R_file(nomeArquivoTrain, MASK)
        X2, y2, z2 = load_L2R_file(nomeArquivoVali, MASK)
        X3, y3, z3 = load_L2R_file(nomeArquivoTest, MASK)

        Vetores_Train = Consultas(X, y, z)
        Vetores_Vali = Consultas(X2, y2, z2)
        Vetores_Test = Consultas(X3, y3, z3)

        '''##############################################################################################################'''
        '''##############################################################################################################'''

        # forest = np.ones(numero_de_estimadores)

        ind = Individuo(forest, 1)
        RandomForest.Fold = int(fold)
        RandomForest.size = numero_de_estimadores

        start = time.clock()

        ger = RandomForest.fit_forest([ind], Vetores_Train, Vetores_Test)

        final = time.clock() - start

        imprimir_individuo(ger[0], numero_de_estimadores, 1, 1, fold, [0, 0, 0], final)

    if executar_threads:

        ex_vetor_n_arvores = [300,500,750]  ##[1000,2000,3000]
        ex_geracoes = [30]  ##[1]           1  e 1 para gerar os resultados de RF
        ex_n_individuos = [75]  ##[1]      75

        ##folds_works(ga, rota_pasta_letor, n_individuos, n_geracoes, n_arvores)
        ##for nn in ex_vetor_n_arvores:
        for gg in ex_geracoes:
            for ii in ex_n_individuos:
                processes = [mp.Process(target=folds_works, args=([1, 1, 1], rota_pasta_letor,gg ,ii , nn, "ndcg")) for
                             nn in ex_vetor_n_arvores]

                # Run processes
                for p in processes:
                    p.start()

                # Exit the completed processes
                for p in processes:
                    p.join()


def folds_works(ga, rota_pasta_letor, n_geracoes, n_individuos, n_arvores, mode="ndcg"):

    forest = Forest(n_estimators=n_arvores, n_jobs=4)

    selecaoTorneio = ga[0]
    crossoverUniforme = ga[1]
    elitist = ga[2]

    for fold in range(1, 6):
        name_train = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.train.txt"
        name_vali = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.vali.txt"
        name_test = rota_pasta_letor + "Fold" + str(fold) + "/" + "Norm.test.txt"

        X, y, z    = load_L2R_file(name_train, MASK)
        X2, y2, z2 = load_L2R_file(name_vali, MASK)
        X3, y3, z3 = load_L2R_file(name_test, MASK)

        Vetores_train = Consultas(X, y, z)
        Vetores_Vali = Consultas(X2, y2, z2)
        Vetores_Test = Consultas(X3, y3, z3)

        forest.Fold = fold
        forest.n_estimators = n_arvores
        forest.size = n_arvores

        if n_geracoes == 1:
            geracao = np.ones(n_arvores)
            IndNatural = Individuo(geracao, 1)
            individuo = forest.fit_forest([IndNatural], Vetores_train, Vetores_Test, mode="ndcg")
            imprimir_individuo(individuo[0], n_arvores, n_geracoes, n_individuos, fold, ga)

        else:
            IndTheBest = forest.ga([Vetores_train, Vetores_Vali], n_geracoes, n_individuos, selecaoTorneio,
                                  crossoverUniforme, elitist, n_arvores, mode)
            individuo = forest.fit_forest([IndTheBest], Vetores_train, Vetores_Test, mode="ndcg")
            imprimir_individuo(individuo[0], n_arvores, n_geracoes, n_individuos, fold, ga)

    return 1

def imprimir_individuo(individuo, num_arvores, num_geracao, total_geracao, fold, ga, time=0):
    '''
    Final Por Fold			Pasta			Nome Arquivo
			                FinalResultados/			/TheBests
    coleção		Fitness		GA
    fold	n arvores	ndcg	map	    geração	g. Ind	qt. ind	selecao	crossover	mutacao	elitismo	mascara

    1	    1000	    0.358	0.24	50  	48	    30	    1	    1   	1	    1
    '''

    try:
        os.mkdir('FinalResultados')
    except OSError:
        print('.')

    map = individuo.vetFitnessTrisk

    if time != 0:
        arquivo_name = 'FinalResultados/Compare_' + str(num_arvores) + '.csv'
        map = time
    elif num_geracao == 1:
        arquivo_name = 'FinalResultados/Original_' + str(num_arvores) + '.csv'
    else:
        arquivo_name = 'FinalResultados/TheBests_' + str(num_arvores) + '.csv'
    arquivo = open(arquivo_name, 'a+')

    arquivo.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};'.format(str(fold), str(num_arvores), str(individuo.vetFitnessNDCG),
                                                                    str(map), str(num_geracao), str(total_geracao),
                                                                    str(individuo.geracao), str(ga[0]), str(ga[1]),
                                                                    str(ga[2])))
    for i in individuo.mascara:
        arquivo.write(str(int(i)))
    arquivo.write("\n")

    arquivo.close()


'''
    Vetor_n_Arvores

       n_forest = numero de individuos no GA
       max_num_geracoes = numero de Gerações
        
    Vetor de elitist, crossover, selecao
        elitismo
            1 = true
            0 = false

        crossover
            1 = ponto a ponto
            0 = uniforme

        seleção
            1 = roleta
            0 = torneio
    '''

if __name__ == '__main__':
    main()
