# RF_TRISK - Documentação Completa

## Índice
1. [Visão Geral do Projeto](#visão-geral)
2. [Diferenças em Relação ao RF_SPEA2](#diferenças)
3. [Estrutura do Projeto](#estrutura)
4. [Componentes Principais](#componentes)
5. [Guia de Configuração](#configuração)
6. [Guia de Execução](#execução)
7. [Métricas e Avaliação](#métricas)
8. [Fluxo de Processamento](#fluxo)

---

## Visão Geral do Projeto {#visão-geral}

**RF_TRISK** é um sistema de otimização de Random Forest baseado em **Algoritmo Genético (GA)** que busca selecionar o melhor subconjunto de árvores para maximizar a métrica **TRISK** (Trade-off Risk) em tarefas de Learning-to-Rank (L2R).

### Características Principais:
- **Objetivo**: Otimizar a seleção de árvores em uma Floresta Aleatória usando TRISK como métrica primária
- **Algoritmo**: Genetic Algorithm (GA) com operadores de seleção, crossover e mutação
- **Validação**: 5-fold cross-validation com dados do LETOR dataset
- **Métrica Primária**: TRISK (Trade-off Risk entre NDCG basal e NDCG otimizado)
- **Cache de Árvores**: Mecanismo de persistência em pickle para reutilização eficiente

---

## Diferenças em Relação ao RF_SPEA2 {#diferenças}

| Aspecto | RF_SPEA2 | RF_TRISK |
|--------|---------|---------|
| **Algoritmo** | SPEA2 (Multiobjective) | GA Single-Objective |
| **Métrica Primária** | NDCG | TRISK (Trade-off Risk) |
| **Objetivo** | Otimizar múltiplos objetivos | Maximizar TRISK |
| **Modo de Avaliação** | Dois objetivos (NDCG vs outro) | Um objetivo (TRISK) |
| **Fitness** | Baseado em dominância Pareto | TRISK = (base_ndcg - opt_ndcg) / (5 folds) |

### Métrica TRISK:
```
TRISK = Σ(base_ndcg[i] - otimizado_ndcg[i]) / número_folds

Onde:
- base_ndcg: NDCG do Random Forest original (sem otimização)
- otimizado_ndcg: NDCG do indivíduo GA otimizado
- A métrica captura o "risco" (degradação) na performance
```

---

## Estrutura do Projeto {#estrutura}

```
RF_TRISK/
├── __main__.py                    # Entrada principal do programa
├── Forest_GA/
│   ├── __init__.py
│   ├── forest.py                  # Classe Forest - wrapper de RandomForest
│   ├── picke.py                   # Utilitários de serialização
│   └── PIBIC/
│       ├── __init__.py
│       ├── ga.py                  # Algoritmo Genético
│       ├── h_l2rMeasures.py       # Métricas de avaliação (NDCG, MAP, TRISK)
│       └── h_l2rMiscellaneous.py  # Funções utilitárias (carregar dados, etc)
```

### Arquivo Principal: `__main__.py`
- **Responsabilidade**: Coordenar a execução dos folds e GA
- **Funções Principais**:
  - `main()`: Ponto de entrada, controla flags de execução
  - `folds_works()`: Processa cada fold (1-5) com GA
  - `imprimir_individuo()`: Salva resultados em CSV

### Arquivo de Floresta: `forest.py`
- **Classe**: `Forest(RandomForestRegressor)`
- **Responsabilidades**:
  - Treinar Random Forest inicial com `fit()`
  - Criar cache de árvores com `get_Trees()`
  - Carregar subconjuntos de árvores com `fitLoadTrees()`
  - Executar GA com `ga()` e `fit_forest()`

### Arquivo de GA: `ga.py`
- **Classes**:
  - `Individuo`: Representa uma solução (máscara binárias de árvores)
  - `GeneticAlgorithm`: Implementa operadores GA
  - `Consultas`: Container para dados de treinamento/validação
  - `Arquive`: Bagging de populações

### Arquivo de Métricas: `h_l2rMeasures.py`
- **Funções Principais**:
  - `modelEvaluation()`: Calcula NDCG e MAP
  - `getTRisk()`: Calcula métrica TRISK
  - `getGeoRisk()`: Calcula GeoRisk (alternativa)

---

## Componentes Principais {#componentes}

### 1. Classe Forest
```python
class Forest(RandomForestRegressor):
    # Atributos
    rota: str              # Caminho para armazenar árvores
    size: int              # Número total de árvores (genes)
    Fold: int              # Fold atual (1-5)
    
    # Métodos principais
    fit_forest(geracao, VetorTrain, VetorVali, mode="ndcg")
    ga(Vet_Train_Vali, max_num_geracoes, n_treesForest, ...)
    get_Trees(maskList="all")
    fitLoadTrees(X, y, forest, all_trees)
```

### 2. Classe Individuo (GA)
```python
class Individuo:
    # Atributos
    fita: np.array         # Máscara binária [0,1,1,0,1,...] (genes)
    fitness: float         # Valor TRISK calculado
    map: float            # Métrica MAP
    bool_fit: int         # Flag se foi avaliado (1) ou não (0)
    geracao: int          # Geração onde foi criado
    
    # Métodos
    get_fita()            # Retorna máscara
    set_fitness(valor)    # Define fitness
```

### 3. Classe GeneticAlgorithm
```python
class GeneticAlgorithm:
    # Atributos de Controle
    tamanho_populacao: int           # Número de indivíduos (n_individuos)
    num_caracteristicas: int         # Número de genes/árvores
    elitist: int                     # (1=com elitismo, 0=sem)
    bool_selecaoTorneio_Roleta: int  # (1=torneio, 0=roleta)
    bool_crossoverUniforme_Ponto: int # (1=uniforme, 0=ponto)
    
    # Métodos
    GenerateInicial()        # Cria população inicial aleatória
    GA(geracao, num_ger)     # Executa um ciclo GA
    ElitistGroup(g1, g2)     # Agrupa com elitismo
```

### 4. Classe Consultas
```python
class Consultas:
    x: np.array      # Features (n_samples, n_features)
    y: np.array      # Targets (n_samples,)
    z: np.array      # Query groups (para ranking)
```

---

## Guia de Configuração {#configuração}

### Parâmetros Principais em `__main__.py`

```python
# Flags de Execução
comparar = 0                              # 1=testar RF individual, 0=desativar
executar_por_fold = 1                     # 1=rodar GA por fold, 0=desativar
executar_threads = 0                      # 1=rodar em paralelo, 0=desativar

# Caminhos e Dados
rota_pasta_letor = "../Colecoes/2003_td_dataset/"  # Caminho LETOR dataset
numero_de_estimadores = 1000              # Total de árvores na floresta inicial

# Parâmetros GA (em folds_works)
n_geracoes = 30          # Número de gerações do GA
n_individuos = 75        # Tamanho da população (indivíduos por geração)
n_arvores = 1000         # Número de árvores total (genes)

# Operadores GA
ga[0] = 1               # selecaoTorneio (1=torneio, 0=roleta)
ga[1] = 1               # crossoverUniforme (1=uniforme, 0=ponto)
ga[2] = 1               # elitist (1=com elitismo, 0=sem)

# Métrica
mode = "tRisk"          # Usar TRISK como métrica
```

### Máscara de Features
```python
MASK = [1] * 64  # Use todos os 64 atributos disponíveis
                 # Para usar subconjunto: [1,1,0,1,0,...] (1=usar, 0=ignorar)
```

---

## Guia de Execução {#execução}

### 1. Execução Básica: GA com 5 Folds
```python
python __main__.py
# Com executar_por_fold = 1, isso executa:
# - Processa fold 1 a 5
# - Para cada fold: treina RF, executa GA (30 gerações, 75 indivíduos)
# - Salva resultados em FinalResultados/
```

### 2. Teste Individual (Random Forest sem GA)
```python
# Em __main__.py, set comparar = 1
# Isso testa uma floresta fixa (máscara pré-definida)
# Útil para comparar RF original vs otimizado
```

### 3. Execução com Threads (Paralela)
```python
# Em __main__.py, set executar_threads = 1
# Executa múltiplos cenários de teste em paralelo
# Cada combinação de n_arvores, n_geracoes, n_individuos roda simultaneamente
```

### 4. Executar um Fold Específico
```python
# Modifique a função folds_works() para processar apenas um fold:
for fold in range(1, 2):  # Apenas fold 1
    # ... resto do código
```

---

## Métricas e Avaliação {#métricas}

### NDCG (Normalized Discounted Cumulative Gain)
- **Propósito**: Medir qualidade de ranking
- **Range**: [0, 1]
- **Interpretação**: Quanto maior, melhor
- **Cálculo**: Pondera documentos relevantes pela sua posição

### MAP (Mean Average Precision)
- **Propósito**: Média de precisão em top-k
- **Range**: [0, 1]
- **Uso em RF_TRISK**: Registrado mas não otimizado

### TRISK (Trade-off Risk)
- **Propósito**: Capturar degradação de performance
- **Fórmula**: `TRISK = Σ(base_ndcg - otimizado_ndcg) / 5`
- **Range**: [-∞, +∞]
- **Interpretação**: 
  - Negativo = Melhoria (ótimo)
  - Positivo = Degradação (ruim)
- **Otimização**: Minimizar TRISK (encontrar valor mais negativo)

### Função getTRisk
```python
def getTRisk(valor_ndgc, base_ndcg, n_folds=5):
    """
    valor_ndgc: NDCG otimizado para cada fold
    base_ndcg: NDCG original (sem GA) para cada fold
    n_folds: Número de folds (padrão 5)
    
    Retorna: Valor TRISK agregado
    """
    risco = np.sum(base_ndcg - valor_ndgc)
    trisk = risco / n_folds
    return trisk
```

---

## Fluxo de Processamento {#fluxo}

### Fluxo Geral: Main → Folds → GA → Resultados

```
main()
  ├─ flag: comparar = 0 (desativar teste individual)
  ├─ flag: executar_por_fold = 1 (ativar GA por fold)
  └─ Chama: folds_works([1,1,1], rota, 30, 75, 1000, "tRisk")
     
     folds_works()
       ├─ Inicializa Forest(n_estimators=1000, n_jobs=4)
       ├─ Para cada fold (1 a 5):
       │  ├─ Carrega dados (train, vali, test) do LETOR
       │  ├─ Cria Consultas(X, y, z) para train, vali, test
       │  ├─ Chama forest.ga() [GA principal]
       │  │
       │  └─ GA Flow:
       │     ├─ Gera população inicial aleatória (75 indivíduos)
       │     ├─ fit_forest() avalia fitness de cada um
       │     │  └─ Usa getTRisk() como métrica
       │     ├─ Para cada geração (1 a 30):
       │     │  ├─ Seleciona pais (torneio ou roleta)
       │     │  ├─ Crossover (uniforme ou ponto)
       │     │  ├─ Mutação
       │     │  ├─ fit_forest() avalia offspring
       │     │  └─ Elitismo (se ativado) preserva melhores
       │     └─ Retorna melhor indivíduo (The_Best)
       │
       ├─ forest.fit_forest([The_Best], train, test, mode="ndcg")
       │  └─ Avalia best indivíduo no conjunto de teste
       │
       └─ imprimir_individuo() salva resultados em CSV
          └─ FinalResultados/TheBests_1000.csv
```

### Subfluxo: fit_forest (Avaliação de Indivíduo)

```
fit_forest(geracao, VetorTrain, VetorVali, mode="ndcg")
  ├─ Carrega todas as árvores do cache (get_Trees("all"))
  ├─ Se não existir cache: fit() cria e pickle
  ├─ Treina RandomForest base para obter base_ndcg
  │
  ├─ Para cada indivíduo na geração:
  │  ├─ Se não foi avaliado (bool_fit == 0):
  │  │  ├─ fitLoadTrees() carrega subconjunto de árvores
  │  │  ├─ predict() faz predição com subconjunto
  │  │  ├─ modelEvaluation() calcula NDCG e MAP
  │  │  │
  │  │  ├─ Se mode == "tRisk":
  │  │  │  ├─ getTRisk() computa TRISK
  │  │  │  └─ set_fitness(trisk) atualiza fitness
  │  │  │
  │  │  ├─ set_map() atualiza MAP
  │  │  └─ bool_fit = 1 marca como avaliado
  │  │
  │  └─ Se foi avaliado: apenas adiciona à saída
  │
  └─ Retorna geração com fitness preenchido
```

### Subfluxo: GA (Um Ciclo Genético)

```
GA.GA(geracao_com_fit, numero_geracao)
  │
  ├─ SelectionOperator() [Torneio ou Roleta]
  │  ├─ Torneio: seleciona melhores N/2 pares por competição
  │  └─ Roleta: probabilidade proporcional ao fitness
  │
  ├─ CrossoverOperator(pai1, pai2) [Uniforme ou Ponto]
  │  ├─ Uniforme: cada gene tem 50% chance de vir de cada pai
  │  └─ Ponto: ponto de corte, herda antes e depois
  │
  ├─ MutationOperator(individuo)
  │  └─ Cada gene tem 1/n_genes probabilidade de flip (0→1 ou 1→0)
  │
  └─ Retorna offspring (nova população sem fitness ainda)
```

### Saída: Arquivo CSV de Resultados

**Arquivo**: `FinalResultados/TheBests_1000.csv`

**Formato**:
```csv
fold;n_arvores;fitness(trisk);map;num_geracao;total_geracao;geracao_criacao;selecao;crossover;elitismo;mascara_binaria
1;1000;-0.0524;0.3421;30;75;28;1;1;1;101010101101010101...
2;1000;-0.0389;0.3287;30;75;25;1;1;1;110101010110101010...
...
```

**Campos**:
- `fold`: Qual fold (1-5)
- `fitness(trisk)`: Valor TRISK (negativo é melhor)
- `map`: Métrica MAP do indivíduo
- `num_geracao`: Qual geração (1-30)
- `total_geracao`: Tamanho população (75)
- `geracao_criacao`: Em que geração foi criado
- `selecao`: 1=torneio, 0=roleta
- `crossover`: 1=uniforme, 0=ponto
- `elitismo`: 1=com elitismo, 0=sem
- `mascara_binaria`: String de 1000 bits (qual árvore usar)

---

## Troubleshooting

### Problema: "Fold... não encontrado"
**Solução**: Verifique caminho em `rota_pasta_letor`. Estrutura esperada:
```
Colecoes/2003_td_dataset/
  ├─ Fold1/
  │  ├─ Norm.train.txt
  │  ├─ Norm.vali.txt
  │  └─ Norm.test.txt
  ├─ Fold2/
  ...
```

### Problema: GA converge rápido demais
**Solução**: 
- Aumentar `n_individuos` (população maior)
- Aumentar taxa de mutação em `ga.py`
- Usar roleta ao invés de torneio (mais exploração)

### Problema: Fitness muito negativo ou NaN
**Solução**:
- Verificar dados LETOR (missing values?)
- Verificar se modo está como "tRisk"
- Verificar se base_ndcg está sendo calculado corretamente

### Problema: Memória insuficiente
**Solução**:
- Reduzir `n_estimadores`
- Reduzir `n_individuos`
- Usar `n_jobs=2` ao invés de 4 em Forest()

---

## Referências Rápidas

- **Arquivo Entrada**: `__main__.py`
- **Arquivo Florest**: `Forest_GA/forest.py`
- **Arquivo GA**: `Forest_GA/PIBIC/ga.py`
- **Arquivo Métricas**: `Forest_GA/PIBIC/h_l2rMeasures.py`
- **Arquivo Dados**: `Forest_GA/PIBIC/h_l2rMiscellaneous.py`
- **Saída Resultados**: `FinalResultados/TheBests_*.csv`
- **Cache Árvores**: `Fold{size}/forest_Fold{fold}.All.Trees.pickle`

