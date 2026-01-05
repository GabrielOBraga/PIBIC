# coding=utf-8
"""
MÓDULO: ga.py
RESPONSABILIDADE: Implementar o Algoritmo Genético (GA) para seleção de árvores
CLASSES PRINCIPAIS:
    - Consultas: Encapsula dados de entrada
    - Individuo: Representa um candidato (solução) no GA
    - GeneticAlgorithm: Implementa operadores genéticos
    - Arquive: Mantém histórico de melhores soluções
"""

import random
import os

import numpy as np


class Consultas:
    """
    Encapsula dados de uma sesão de Learning-to-Rank.
    
    Atributos:
        - x: Matriz de features (n_samples × n_features)
        - y: Array de rótulos/relevância (n_samples,)
        - q: Array de query IDs (n_samples,) - identifica qual query cada amostra pertence
    """
    def __init__(self, x, y, z):
        self.x = x  # Matriz de features/características
        self.y = y  # Rótulos: relevância (0/1 ou 0/1/3 dependendo dataset)
        self.q = z  # Query IDs: identifica grupos de documentos


class Individuo:
    """
    Representa um candidato/solução no Algoritmo Genético.
    
    Uma solução é uma máscara binária [0,1,...,1] de tamanho = número de árvores.
    Cada 1 indica "incluir árvore", 0 indica "excluir árvore".
    
    Atributos:
        - mascara: Array [0,1,...,1] - genótipo do indivíduo
        - geracao: Número da geração em que foi criado
        - fitnessNDCG: Qualidade do ranking (maior = melhor)
        - vetFitnessNDCG: NDCG por query
        - fitnessTrisk: Risco relativo ao baseline (menor = melhor)
        - vetFitnessTrisk: TRISK por query
        - fitnessSpea2: Fitness SPEA2 multiobjetivo
        - bool_fit: Flag 0/1 indicando se fitness foi calculado
    """
    def __init__(self, mascara, geracao):
        self.mascara = mascara  # Genótipo: array binário
        self.geracao = geracao  # Número da geração

        # Fitness por NDCG (qualidade)
        self.vetFitnessNDCG = []      # NDCG por query
        self.fitnessNDCG = 0          # NDCG agregado (média)

        # Fitness por TRISK (risco)
        self.vetFitnessTrisk = []     # TRISK por query
        self.fitnessTrisk = 0         # TRISK agregado

        # Fitness SPEA2 (multiobjetivo)
        self.fitnessSpea2 = 0         # Fitness após análise Pareto
        self.vetTStastitico = 0       # Reservado para análise estatística

        self.bool_max_min = 1         # Indicador de otimização (não usado)
        self.bool_fit = 0             # 0=não avaliado, 1=fitness calculado

    def get_fita(self):
        """Retorna a máscara (genótipo) do indivíduo."""
        return self.mascara

    def set_fitness(self, fitness, tipo):
        """Define fitness conforme tipo."""
        if tipo == 1:
            self.fitnessNDCG = fitness
        elif tipo == 2:
            self.fitnessTrisk = fitness
        elif tipo == 3:
            self.fitnessSpea2 = fitness

    def get_fitness(self, tipo):
        """
        Retorna o fitness conforme tipo solicitado.
        
        tipo:
            - 0, 3: NDCG
            - 1, 4: TRISK
            - 2: SPEA2
        
        Retorna: (fitness_agregado, array_por_query)
        """
        if tipo == 0 or tipo == 3:
            return self.fitnessNDCG, self.vetFitnessNDCG
        elif tipo == 1 or tipo == 4:
            return self.fitnessTrisk, self.vetFitnessTrisk
        elif tipo == 2:
            return self.fitnessSpea2, self.vetTStastitico

    def getTipoFitness(self):
        """Retorna lista dos tipos de fitness disponíveis."""
        return ["ndcg", "trisk", "spea2", "ndcg/ts", "trisk/ts", "spea2/ts"]

    def len(self):
        """Retorna tamanho da máscara (número de genes/árvores)."""
        return len(self.mascara)

    def get_geracao(self):
        """Retorna número da geração em que foi criado."""
        return self.geracao


class GeneticAlgorithm:
    """
    Implementa o Algoritmo Genético para otimização de seleção de árvores.
    
    Operadores Genéticos Implementados:
        1. SELEÇÃO: Torneio ou Roleta
        2. CROSSOVER: Uniforme ou Um Ponto
        3. MUTAÇÃO: Uniforme ou Um Ponto
        4. SELEÇÃO DE SOBREVIVÊNCIA: Elitismo (opcional)
    
    Atributos:
        - tamanho_populacao: Quantos indivíduos por geração (ex: 75)
        - num_caracteristicas: Quantos genes por indivíduo (ex: 1000 árvores)
        - probabilidade: Prob. de crossover ocorrer (0.5 = 50%)
        - probabilidadeMutacao: Prob. de mutação em cada gene (0.3 = 30%)
        - bool_selecaoTorneio_Roleta: 1=Torneio, 0=Roleta
        - bool_crossoverUniforme_Ponto: 1=Uniforme, 0=Um Ponto
        - elitist: 1=Usar elitismo, 0=Sem elitismo
        - nFitness: Índice do tipo de fitness a usar (0-5)
    """
    def __init__(self, geracao1, num_geracao):
        self.populacao = geracao1
        self.num_geracao = num_geracao

        self.nova_geracao = []

        # Configurações padrão
        self.tamanho_populacao = 70
        self.num_caracteristicas = 1000

        self.elitist = 0

        self.bool_selecaoTorneio_Roleta = 1  # 1=Torneio, 0=Roleta

        self.bool_crossoverUniforme_Ponto = 1  # 1=Uniforme, 0=Um Ponto

        self.probabilidade = 0.5               # Prob. de crossover
        self.probabilidadeMutacao = 0.3        # Prob. de mutacao

    def GA(self, geracao_com_fitness, numero_da_geracao, tipo):
        """
        Executa uma geração completa do Algoritmo Genético.
        
        Algoritmo:
        Enquanto nova_geração < tamanho_populacao:
            1. Selecionar 2 pais (Torneio ou Roleta)
            2. Aplicar Crossover nos pais
            3. Aplicar Mutação em cada filho (30% de chance)
            4. Adicionar filhos à nova geração
        
        ENTRADA:
            - geracao_com_fitness: Geração anterior com fitness calculado
            - numero_da_geracao: Número desta geração
            - tipo: Tipo de fitness a usar ("ndcg", "trisk", "spea2", etc)
            
        SAÍDA: Nova geração de indivíduos (sem fitness calculado)
        """

        # Identificar qual fitness usar
        self.setTypeFitness(tipo)

        self.populacao = geracao_com_fitness
        self.num_geracao = numero_da_geracao

        tamanho_populacao = len(self.populacao)
        probabilidades = np.zeros(tamanho_populacao)

        # Calcular fitness de cada indivíduo
        for i in range(tamanho_populacao):
            probabilidades[i] = self.MyFitness(self.populacao[i])

        self.nova_geracao = []
        tamanho_nova_geracao = 0

        # === LOOP: Criar nova geração ===
        while tamanho_nova_geracao < tamanho_populacao:

            # Passo 1: SELEÇÃO - Escolher 2 pais
            [ind1, ind2] = self.Selecao(tipo=self.bool_selecaoTorneio_Roleta)

            # Passo 2: CROSSOVER - Cruzar pais para gerar 2 filhos
            cruzamentos = self.Crossover(self.populacao[int(ind1)], self.populacao[int(ind2)],
                                         tipo=self.bool_crossoverUniforme_Ponto)

            # Passo 3: MUTAÇÃO - Primeiro filho
            valor_sorteado = random.randint(0, 101) / 100
            if valor_sorteado <= self.probabilidadeMutacao:
                cruzamentos[0] = self.Mutacao(cruzamentos[0], tipo=1)

            # Passo 3: MUTAÇÃO - Segundo filho
            valor_sorteado = random.randint(0, 101) / 100
            if valor_sorteado <= self.probabilidadeMutacao:
                cruzamentos[1] = self.Mutacao(cruzamentos[1], tipo=1)

            # Passo 4: Adicionar filhos à nova geração
            self.nova_geracao.append(Individuo(cruzamentos[0], self.num_geracao))
            self.nova_geracao.append(Individuo(cruzamentos[1], self.num_geracao))

            tamanho_nova_geracao += 2

        return self.nova_geracao

    def GenerateInicial(self):
        """
        Cria a população inicial aleatória.
        
        Algoritmo:
        1. Para cada indivíduo (tamanho_populacao):
            - Criar máscara com genes aleatórios (50% 0, 50% 1)
        2. Converter máscaras em Individuo
        3. Primeiro indivíduo é SEMPRE all-ones (todas as árvores)
        
        SAÍDA: Lista de Individuo com genótipos aleatórios
        """
        populacao_inicial = []
        
        # Gerar populacao_inicial aleatória
        for j in range(self.tamanho_populacao):
            p = np.zeros(self.num_caracteristicas)
            for i in range(self.num_caracteristicas):
                p[i] = random.randint(0, 1)  # 50% chance 0, 50% chance 1
            populacao_inicial.append(p)

        # Converter arrays em objetos Individuo
        individuos_g1 = []
        for g in populacao_inicial:
            individuos_g1.append(Individuo(g, 1))  # Geração 1
        
        # IMPORTANTE: Primeiro indivíduo é sempre all-ones (baseline completo)
        individuos_g1[0] = Individuo(np.ones(self.num_caracteristicas), 1)
        
        return individuos_g1

    def Selecao(self, total_num_sorteados=2, tipo=1):
        """
        Seleciona pais para reprodução.
        
        Dois métodos disponíveis:
        
        tipo=1 - SELEÇÃO POR TORNEIO:
            - Selecionar 2 indivíduos aleatoriamente
            - Retornar o com melhor fitness
            - Vantagem: Simples, promove convergência
        
        tipo=0 - SELEÇÃO POR ROLETA (Roulette Wheel):
            - Probabilidade proporcional ao fitness
            - Indivíduos com fitness melhor têm maior chance
            - Vantagem: Mantém diversidade
        
        ENTRADA: tipo (0 ou 1)
        SAÍDA: Array com índices dos pais selecionados
        """

        if tipo == 0:  # ROLETA
            num_individuos = len(self.populacao)
            probabilidades = np.zeros(num_individuos)
            
            # Calcular fitness de cada indivíduo
            for i in range(num_individuos):
                probabilidades[i] = self.MyFitness(self.populacao[i])
            
            total = sum(probabilidades)
            valores_sorteados = np.zeros(total_num_sorteados)
            cont1 = 0
            
            # Selecionar usando roleta ponderada
            while (cont1 < total_num_sorteados):
                valor = random.uniform(0, total)
                soma_acumulada = 0
                posicao = 0
                
                # Encontrar posição na roleta
                while (soma_acumulada < valor):
                    soma_acumulada += probabilidades[posicao]
                    posicao += 1
                
                # Verificar se não foi selecionado antes
                contido = 0
                cont2 = 0
                while (cont2 < cont1):
                    if (valores_sorteados[cont2] == posicao - 1):
                        contido = 1
                        break
                    cont2 += 1
                
                # Adicionar se não está duplicado
                if not (contido):
                    valores_sorteados[cont1] = posicao - 1
                    cont1 += 1

        elif tipo == 1:  # TORNEIO
            valores_sorteados = [-1] * total_num_sorteados
            total_sorteados = 0
            
            while (total_sorteados < total_num_sorteados):
                valores_sorteados[total_sorteados] = self.Torneio(total_num_sorteados)
                total_sorteados += 1

        return valores_sorteados

    def Torneio(self, quantidade_competidores=2):
        """
        Implementa seleção por Torneio.
        
        Algoritmo:
        1. Selecionar 'quantidade_competidores' indivíduos aleatoriamente (sem repetição)
        2. Retornar o com MAIOR fitness
        
        ENTRADA: quantidade_competidores (ex: 2 para torneio binário)
        SAÍDA: Índice do vencedor
        """
        sorteados = np.zeros(quantidade_competidores)
        total_sorteados = 0
        total_individuos = len(self.populacao)
        
        # Selecionar competidores (sem repetição)
        while total_sorteados < quantidade_competidores:
            valor_aleatorio = random.randint(0, total_individuos - 1)
            contido = 0
            cont1 = 0

            # Verificar se não foi selecionado antes
            while cont1 < total_sorteados:
                if sorteados[cont1] == valor_aleatorio:
                    contido = 1
                    break
                cont1 += 1
            
            if not contido:
                sorteados[total_sorteados] = valor_aleatorio
                total_sorteados += 1
        
        # Encontrar vencedor (melhor fitness)
        posi_inicial = 0
        for i in range(quantidade_competidores):
            if self.MyFitness(self.populacao[int(sorteados[i])]) > self.MyFitness(self.populacao[int(sorteados[posi_inicial])]):
                posi_inicial = i
        
        return sorteados[posi_inicial]

    def Crossover(self, individuoA, individuoB, tipo=1):
        """
        Cria filhos combinando genótipos dos pais (recombinação sexual).
        
        Dois métodos disponíveis:
        
        tipo=1 - CROSSOVER UNIFORME:
            Para cada gene (posição):
                - Se prob. < self.probabilidade:
                    Trocar gene entre pais
            Vantagem: Maior exploração do espaço de soluções
        
        tipo=0 - CROSSOVER EM UM PONTO:
            - Selecionar ponto aleatório
            - Trocar genes APÓS esse ponto
            - Vantagem: Preserva blocos de genes
        
        ENTRADA:
            - individuoA, individuoB: Pais
            - tipo: Tipo de crossover (0 ou 1)
            
        SAÍDA: [filho1, filho2] (genótipos - arrays)
        """
        individuoAx = individuoA.mascara.copy()
        individuoBx = individuoB.mascara.copy()

        if tipo == 0:  # CROSSOVER EM UM PONTO
            tamanho = individuoA.len()
            valor_sorteado = random.randint(0, 101) / 100
            
            # Sortear se vai fazer crossover
            if (valor_sorteado <= self.probabilidade):
                posicao = random.randint(0, tamanho - 1)
                # Trocar genes após ponto de corte
                temp = individuoAx[posicao]
                individuoAx[posicao] = individuoBx[posicao]
                individuoBx[posicao] = temp

        elif tipo == 1:  # CROSSOVER UNIFORME
            for i in range(len(individuoAx)):
                valor_sorteado = random.randint(0, 101) / 100
                # Para cada gene, sortear se vai trocar
                if valor_sorteado <= self.probabilidade:
                    temp = individuoAx[i]
                    individuoAx[i] = individuoBx[i]
                    individuoBx[i] = temp

        return [individuoAx, individuoBx]

    def Mutacao(self, mascara, tipo=1):
        """
        Modifica aleatoriamente genes de um indivíduo (introduz diversidade).
        
        Dois métodos disponíveis:
        
        tipo=1 - MUTAÇÃO UNIFORME:
            Para cada gene:
                - Se prob. <= self.probabilidadeMutacao:
                    Inverter gene (0→1 ou 1→0)
            Vantagem: Maior exploração local
        
        tipo=0 - MUTAÇÃO EM UM PONTO:
            - Selecionar gene aleatório
            - Se prob. <= self.probabilidadeMutacao:
                Inverter apenas esse gene
            Vantagem: Mutação mais conservadora
        
        ENTRADA:
            - mascara: Genótipo a mutar
            - tipo: Tipo de mutação (0 ou 1)
            
        SAÍDA: Genótipo mutado
        """

        if tipo == 1:  # MUTAÇÃO UNIFORME
            valor_sorteado = random.randint(0, 101) / 100
            individuox = mascara
            for posicao in range(len(mascara)):
                if valor_sorteado <= self.probabilidadeMutacao:
                    if individuox[posicao] == 1:
                        individuox[posicao] = 0
                    else:
                        individuox[posicao] = 1
        
        if tipo == 0:  # MUTAÇÃO EM UM PONTO
            valor_sorteado = random.randint(0, 101) / 100
            individuox = mascara
            posicao = random.randint(0, len(mascara) - 1)

            if valor_sorteado <= self.probabilidadeMutacao:
                if individuox[posicao] == 1:
                    individuox[posicao] = 0
                else:
                    individuox[posicao] = 1
        
        return individuox

    def ElitistGroup(self, populacaoA, populacaoB):
        """
        Implementa SELEÇÃO ELITISTA (preserva melhores soluções).
        
        Algoritmo:
        1. Combinar população anterior (A) e nova (B)
        2. Ordenar por fitness (descendente)
        3. Retornar os melhores len(A) indivíduos
        
        Benefício: Garante que fitness nunca diminua entre gerações
        
        ENTRADA:
            - populacaoA: Geração anterior
            - populacaoB: Geração nova
            
        SAÍDA: Melhor mistura (tamanho = len(A))
        """
        tamanho_populacao = len(populacaoB) + len(populacaoA)

        populacaoNova = []

        # Combinar ambas as populações
        populacaoNova.extend(populacaoA + populacaoB)

        # ORDENAÇÃO BOLHA: Ordenar por fitness (decrescente)
        for i in range(tamanho_populacao):
            j = i + 1
            while j < tamanho_populacao:
                # Se indivíduo i tem fitness MENOR que j, trocar
                if self.MyFitness(populacaoNova[i]) < self.MyFitness(populacaoNova[j]):
                    temp = populacaoNova[i]
                    populacaoNova[i] = populacaoNova[j]
                    populacaoNova[j] = temp
                j += 1

        # Retornar os melhores len(A) indivíduos
        x = slice(0, len(populacaoA), 1)
        return populacaoNova[x]

    def setTypeFitness(self, tipo):
        """
        Identifica qual tipo de fitness usar e armazena seu índice.
        
        Mapeamento de tipos:
            0 - "ndcg"
            1 - "trisk"
            2 - "spea2"
            3 - "ndcg/ts"
            4 - "trisk/ts"
            5 - "spea2/ts"
        """
        cont = 0
        tipos = ["ndcg", "trisk", "spea2", "ndcg/ts", "trisk/ts", "spea2/ts"]
        for t in tipos:
            if tipo == t:
                self.nFitness = cont
            cont += 1

    def MyFitness(self, individuo):
        """
        Retorna o fitness atual de um indivíduo.
        
        Usa self.nFitness para determinar qual fitness retornar.
        """
        fitness, vect = individuo.get_fitness(self.nFitness)
        return fitness


class Arquive:
    """
    Mantém histórico das melhores soluções encontradas (arquivo elite).
    
    Funciona como um "pote" que armazena os melhores indivíduos de toda a evolução.
    Facilita a recuperação da melhor solução encontrada no final.
    
    Atributos:
        - size: Tamanho máximo do arquivo (ex: 150)
        - mode: Índice do fitness a usar para ranking
        - arq: Lista de indivíduos (mantida ordenada por fitness)
        - type: Tipo de indivíduo armazenado (para referência)
    """
    def __init__(self, tamanho=100, mode=1):
        self.mode = mode
        self.size = tamanho
        self.arq = []
        self.type = 0

    def fit(self, individuo):
        """Calcula fitness de um indivíduo conforme self.mode."""
        fitness, vect = individuo.get_fitness(self.mode)
        return fitness

    def getBag(self, params='default'):
        """
        Retorna indivíduos do arquivo.
        
        params:
            - 'default': Retorna toda a lista
            - 1: Retorna o MELHOR (primeiro)
            - N: Retorna os N melhores
        """
        if params == 'default':
            return self.arq
        elif params == 1:
            return self.arq[0]
        elif (params > 1) and (params < len(self.arq)):
            x = slice(0, params, 1)
            return self.arq[x]

    def appendBag(self, newItens):
        """
        Adiciona novos itens ao arquivo e mantém ordenado.
        
        Algoritmo:
        1. Combinar arquivo atual com novos itens
        2. Ordenar por fitness (descendente)
        3. Se ultrapassou tamanho máximo, descartar piores
        """
        ArquiveNew = []

        sizeA = len(newItens) + len(self.arq)
        sizeM = self.size

        # Combinar
        ArquiveNew.extend(self.arq + newItens)

        # ORDENAR (Bubble Sort)
        for i in range(sizeA):
            j = i + 1
            while j < sizeA:
                n1 = self.fit(ArquiveNew[i])
                n2 = self.fit(ArquiveNew[j])
                # Se i tem fitness MENOR que j, trocar
                if n1 < n2:
                    temp = ArquiveNew[i]
                    ArquiveNew[i] = ArquiveNew[j]
                    ArquiveNew[j] = temp
                j += 1

        # Se tamanho > máximo, descartar piores
        if sizeA > sizeM:
            x = slice(0, sizeM, 1)
            self.arq = []
            self.arq = ArquiveNew
        else:
            x = slice(0, sizeA, 1)
            self.arq = []
            self.arq = ArquiveNew


def PrintExcelGA(fold, geracao, populacao, ga, mode=0):
    """
    Registra resultados de uma geração em arquivo CSV.
    
    Arquivo gerado:
        - Diretório: N_<tamanho_gene>/Fold_<fold>/
        - Nome: G_<geracao>Ind_<pop>GA_<config>_store.csv
    
    Colunas do CSV:
        - geracao, fitness, vetores_fitness, mascara
    
    ENTRADA:
        - fold: Número do fold
        - geracao: Número da geração
        - populacao: Lista de Individuo
        - ga: [selecao, crossover, mutacao, elitismo]
        - mode: Índice do fitness a registrar
    """
    [selecao, crossover, mutacao, elitist] = ga

    # Criar diretório
    FOLD = 'N_' + str(populacao[0].len()) + '/Fold_' + str(fold) + '/'
    NOME_ARQUIVO = 'G_' + str(geracao) + 'Ind_' + str(len(populacao)) + 'GA_' + str(selecao) \
                   + str(crossover) + str(mutacao) + str(elitist) + '_store.csv'

    try:
        os.makedirs(FOLD)
    except OSError:
        n = 0

    # Escrever arquivo
    arquivo = open(FOLD + NOME_ARQUIVO, 'w')

    for p in range(len(populacao)):
        fitness, vect = populacao[p].get_fitness(mode)
        arquivo.write(str(populacao[p].geracao) + ";")

    arquivo.write(str(fitness) + ";")

    for i in vect:
        arquivo.write(str(i) + ";")

    # Escrever máscara binária
    for i in populacao[p].mascara:
        arquivo.write(str(int(i)))
    arquivo.write("\n")

    arquivo.close()
