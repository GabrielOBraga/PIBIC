# coding=utf-8
import random
import os
from warnings import warn

import numpy as np


class Consultas:
    def __init__(self, x, y, z):
        self.x = x  ## Consultas
        self.y = y  ## Relevante ou não relevante
        self.q = z  ## todos os documentos


class Individuo:
    def __init__(self, mascara, geracao):
        self.mascara = mascara
        self.geracao = geracao
        self.fitness = 0
        self.map = 0
        self.bool_fit = 0

    def get_fita(self):
        return self.mascara

    def set_fitness(self, fitness):
        self.fitness = fitness

    def set_map(self, map):
        self.map = map

    def get_fitness(self):
        return self.fitness

    def len(self):
        return len(self.mascara)

    def get_geracao(self):
        return self.geracao


class GeneticAlgorithm:
    def __init__(self, geracao1, num_geracao):
        self.populacao = geracao1
        self.num_geracao = num_geracao

        self.nova_geracao = []

        self.tamanho_populacao = 70
        self.num_caracteristicas = 1000

        self.elitist = 0

        self.bool_selecaoTorneio_Roleta = 1  ## Torneio 1 Roleta 0

        self.bool_crossoverUniforme_Ponto = 1  ## Uniforme 1 Pontual 0

        self.probabilidade = 0.5  ## de crossover
        self.probabilidadeMutacao = 0.3  ## de mutacao

    def GA(self, geracao_com_fitness, numero_da_geracao):

        self.populacao = geracao_com_fitness
        self.num_geracao = numero_da_geracao

        tamanho_populacao = len(self.populacao)
        probabilidades = np.zeros(tamanho_populacao)

        for i in range(tamanho_populacao):
            probabilidades[i] = self.MyFitness(self.populacao[i])

        self.nova_geracao = []
        tamanho_nova_geracao = 0

        while tamanho_nova_geracao < tamanho_populacao:

            ''' Tipo de Selecao de Pais'''
            [ind1, ind2] = self.Selecao(tipo=self.bool_selecaoTorneio_Roleta)

            ''' Tipo de Selecao de Crossover'''
            cruzamentos = self.Crossover(self.populacao[int(ind1)], self.populacao[int(ind2)],
                                         tipo=self.bool_crossoverUniforme_Ponto)

            ''' Mutação nos dois filhos'''
            valor_sorteado = random.randint(0, 101) / 100
            if valor_sorteado <= self.probabilidadeMutacao:
                cruzamentos[0] = self.Mutacao(cruzamentos[0], tipo=1)

            valor_sorteado = random.randint(0, 101) / 100
            if valor_sorteado <= self.probabilidadeMutacao:
                cruzamentos[1] = self.Mutacao(cruzamentos[1], tipo=1)

            ''' Salvando novos individuos'''

            self.nova_geracao.append(Individuo(cruzamentos[0], self.num_geracao))
            self.nova_geracao.append(Individuo(cruzamentos[1], self.num_geracao))

            tamanho_nova_geracao += 2

        return self.nova_geracao

    def GenerateInicial(self):
        populacao_inicial = []
        for j in range(self.tamanho_populacao):
            p = np.zeros(self.num_caracteristicas)
            for i in range(self.num_caracteristicas):
                p[i] = random.randint(0, 1)  ## Criar opção de Porcentagem de Genes Dominantes
            populacao_inicial.append(p)

        ''' Converte mascara para individuo'''
        individuos_g1 = []
        for g in populacao_inicial:
            individuos_g1.append(Individuo(g, 1))  ### Geracao Inicial Parametro = 1
        individuos_g1[0] = Individuo(np.ones(self.num_caracteristicas), 1)
        return individuos_g1

    ''' Tipo: 1 para torneio 0 para roleta'''

    def Selecao(self, total_num_sorteados=2, tipo=1):

        if tipo == 0:  ### 0 para Roleta
            num_individuos = len(self.populacao)
            probabilidades = np.zeros(num_individuos)
            for i in range(num_individuos):
                probabilidades[i] = self.MyFitness(self.populacao[i])
            total = sum(probabilidades)
            valores_sorteados = np.zeros(total_num_sorteados)
            cont1 = 0
            while (cont1 < total_num_sorteados):
                valor = random.uniform(0, total)
                soma_acumulada = 0
                posicao = 0
                while (soma_acumulada < valor):
                    soma_acumulada += probabilidades[posicao]
                    posicao += 1
                contido = 0
                cont2 = 0
                while (cont2 < cont1):
                    if (valores_sorteados[cont2] == posicao - 1):
                        contido = 1
                        break
                    cont2 += 1
                if not (contido):
                    valores_sorteados[cont1] = posicao - 1
                    cont1 += 1

        elif tipo == 1:  ## 1 Selecao por Torneio
            valores_sorteados = [-1] * total_num_sorteados
            total_sorteados = 0
            while (total_sorteados < total_num_sorteados):
                valores_sorteados[total_sorteados] = self.Torneio(total_num_sorteados)
                total_sorteados += 1

        return valores_sorteados

    def Torneio(self, quantidade_competidores=2):
        sorteados = np.zeros(quantidade_competidores)
        total_sorteados = 0
        total_individuos = len(self.populacao)
        while total_sorteados < quantidade_competidores:
            valor_aleatorio = random.randint(0, total_individuos - 1)
            contido = 0
            cont1 = 0

            while cont1 < total_sorteados:
                if sorteados[cont1] == valor_aleatorio:
                    contido = 1
                    break
                cont1 += 1
            if not contido:
                sorteados[total_sorteados] = valor_aleatorio
                total_sorteados += 1
        posi_inicial = 0
        for i in range(quantidade_competidores):
            if self.populacao[int(sorteados[i])].fitness > self.populacao[int(sorteados[posi_inicial])].fitness:
                posi_inicial = i
        return sorteados[posi_inicial]

    ''' Tipo: 1 para uniforme 0 para pontual'''

    def Crossover(self, individuoA, individuoB, tipo=1):
        individuoAx = individuoA.mascara
        individuoBx = individuoB.mascara

        if tipo == 0:  ## Cruzamento em um ponto
            tamanho = individuoA.len()
            valor_sorteado = random.randint(0, 101) / 100
            if (valor_sorteado <= self.probabilidade):
                posicao = random.randint(0, tamanho - 1)
                temp = individuoAx[posicao]
                individuoAx[posicao] = individuoBx[posicao]
                individuoBx[posicao] = temp

        elif tipo == 1:  ## Cruzamento uniforme
            for i in range(len(individuoAx)):
                valor_sorteado = random.randint(0, 101) / 100
                if valor_sorteado <= self.probabilidade:
                    temp = individuoAx[i]
                    individuoAx[i] = individuoBx[i]
                    individuoBx[i] = temp

        return [individuoAx, individuoBx]

    ''' Tipo= 1 para uniforme 0 para pontual'''

    def Mutacao(self, mascara, tipo=1):

        if tipo == 1:  ## Mutacao uniforme
            valor_sorteado = random.randint(0, 101) / 100
            individuox = mascara
            for posicao in range(len(mascara)):
                if valor_sorteado <= self.probabilidadeMutacao:
                    if individuox[posicao] == 1:
                        individuox[posicao] = 0
                    else:
                        individuox[posicao] = 1
        if tipo == 0:  ## Mutacao em um ponto
            valor_sorteado = random.randint(0, 101) / 100
            individuox = mascara
            posicao = random.randint(0, len(mascara))

            if valor_sorteado <= self.probabilidadeMutacao:
                if individuox[posicao] == 1:
                    individuox[posicao] = 0
                else:
                    individuox[posicao] = 1
        return individuox

    def ElitistGroup(self, populacaoA, populacaoB):
        tamanho_populacao = len(populacaoB) + len(populacaoA)

        populacaoNova = []

        populacaoNova.extend(populacaoA + populacaoB)

        for i in range(tamanho_populacao):
            j = i + 1
            while j < tamanho_populacao:
                if self.MyFitness(populacaoNova[i]) < self.MyFitness(populacaoNova[j]):
                    temp = populacaoNova[i]
                    populacaoNova[i] = populacaoNova[j]
                    populacaoNova[j] = temp
                j += 1

        x = slice(0, len(populacaoA), 1)
        return populacaoNova[x]

    def MyFitness(self, individuo):
        return individuo.get_fitness()


class Arquive:
    def __init__(self, tamanho=100):
        self.size = tamanho
        self.arq = []
        self.type = 0

    def getBag(self, params='default'):

        if params == 'default':
            return self.arq
        elif params == 1:
            return self.arq[0]
        elif (params > 1) and (params < len(self.arq)):
            x = slice(0, params, 1)
            return self.arq[x]

    def appendBag(self, newItens):
        ArquiveNew = []

        sizeA = len(newItens) + len(self.arq)
        sizeM = self.size

        ArquiveNew.extend(self.arq + newItens)

        for i in range(sizeA):
            j = i + 1
            while j < sizeA:
                if ArquiveNew[i].fitness < ArquiveNew[j].fitness:
                    temp = ArquiveNew[i]
                    ArquiveNew[i] = ArquiveNew[j]
                    ArquiveNew[j] = temp
                j += 1

        if sizeA > sizeM:
            x = slice(0, sizeM, 1)
            self.arq = []
            self.arq = ArquiveNew
        else:
            x = slice(0, sizeA, 1)
            self.arq = []
            self.arq = ArquiveNew


def PrintExcelGA(fold, geracao, populacao, ga):
    ''' Impressao de Arquivo para futuras analises'''

    '''
    N_NArvores/Fold_X/			/G_NG_I_NI_GA_1111

    NG = 	Numero da geração
    NI =	Quantidade de Individuos
    GA = 	selecao/crossover/mutacao/elitismo

    NIndividuo	ndcg	map 	mascara

    '''
    [selecao, crossover, mutacao, elitist] = ga

    FOLD = 'N_' + str(populacao[0].len()) + '/Fold_' + str(fold) + '/'

    NOME_ARQUIVO = 'G_' + str(geracao) + 'Ind_' + str(len(populacao)) + 'GA_' + str(selecao) \
                   + str(crossover) + str(mutacao) + str(elitist) + '_store.csv'

    try:
        os.makedirs(FOLD)
    except OSError:
        n = 0

    arquivo = open(FOLD + NOME_ARQUIVO, 'w')

    for p in range(len(populacao)):
        arquivo.write(
            '{0};{1};'.format(str(populacao[p].geracao), str(populacao[p].fitness)))

        for i in populacao[p].mascara:
            arquivo.write(str(int(i)))
        arquivo.write("\n")

    arquivo.close()
