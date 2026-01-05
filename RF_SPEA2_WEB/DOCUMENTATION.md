# Documentação RF_SPEA2_WEB

## Índice
1. [Visão Geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Componentes Principais](#componentes-principais)
4. [Fluxo de Execução](#fluxo-de-execução)
5. [Módulos Detalhados](#módulos-detalhados)
6. [Configurações e Parâmetros](#configurações-e-parâmetros)
7. [Exemplos de Uso](#exemplos-de-uso)

---

## Visão Geral

O projeto **RF_SPEA2_WEB** implementa um algoritmo genético (GA) aplicado à otimização de florestas aleatórias (Random Forest) para tarefas de Learning-to-Rank (L2R). O sistema utiliza o algoritmo SPEA2 (Strength Pareto Evolutionary Algorithm 2) para buscar combinações ótimas de árvores de decisão que maximizam métricas como NDCG (Normalized Discounted Cumulative Gain) e minimizam riscos.

### Objetivo Principal
- Otimizar a seleção de árvores em uma Random Forest usando algoritmos genéticos
- Minimizar o número de árvores mantendo ou melhorando o desempenho
- Avaliar o trade-off entre precisão (NDCG) e risco (TRISK)

### Tecnologias Utilizadas
- **Python 3.x**
- **NumPy**: Operações numéricas e matrizes
- **Scikit-learn**: Implementação de Random Forest
- **SciPy**: Funções estatísticas
- **Joblib**: Processamento paralelo

---

## Estrutura do Projeto

```
RF_SPEA2_WEB/
├── __main__.py                          # Ponto de entrada do programa
├── Forest_GA/
│   ├── __init__.py
│   ├── forest.py                        # Classe Forest (herança de RandomForestRegressor)
│   ├── picke.py                         # Utilitários de serialização
│   └── PIBIC/
│       ├── __init__.py
│       ├── ga.py                        # Algoritmo genético (GA)
│       ├── h_functionsFilter.py         # Funções de dominância Pareto
│       ├── h_l2rMeasures.py             # Métricas L2R (NDCG, TRISK, etc)
│       ├── h_l2rMiscellaneous.py        # Utilitários de carregamento de dados
│       └── h_ParetoSet.py               # Gestão de conjunto Pareto
└── FinalResultados/                     # Diretório de saída (criado dinamicamente)
```

---

## Componentes Principais

### 1. **Consultas** (ga.py)
Estrutura que encapsula dados de uma consulta.

```python
class Consultas:
    x  # Matriz de features/características das queries
    y  # Rótulos de relevância
    q  # Identificadores de query
```

### 2. **Individuo** (ga.py)
Representa um indivíduo no algoritmo genético (uma combinação de árvores).

```python
class Individuo:
    mascara           # Array binário: 1=árvore selecionada, 0=excluída
    geracao          # Número da geração em que foi criado
    fitnessNDCG      # Fitness baseado em NDCG
    fitnessTrisk     # Fitness baseado em TRISK
    fitnessSpea2     # Fitness baseado em SPEA2
    bool_fit         # Flag indicando se fitness foi calculado
```

### 3. **GeneticAlgorithm** (ga.py)
Implementa os operadores genéticos.

```python
class GeneticAlgorithm:
    populacao                        # População atual
    num_geracao                      # Número de gerações
    tamanho_populacao                # Tamanho da população (default: 70)
    num_caracteristicas              # Número de genes (árvores) (default: 1000)
    
    # Operadores
    bool_selecaoTorneio_Roleta      # 1=Torneio, 0=Roleta
    bool_crossoverUniforme_Ponto    # 1=Uniforme, 0=Um ponto
    probabilidade                    # Prob. de crossover (default: 0.5)
    probabilidadeMutacao            # Prob. de mutação (default: 0.3)
```

**Métodos Principais:**
- `GA()`: Executa uma geração completa
- `Selecao()`: Seleciona pais (Torneio ou Roleta)
- `Crossover()`: Cria filhos combinando pais
- `Mutacao()`: Modifica aleatoriamente genes
- `GenerateInicial()`: Cria população inicial
- `ElitistGroup()`: Aplica seleção elitista

### 4. **Forest** (forest.py)
Extensão de RandomForestRegressor otimizada para o algoritmo genético.

```python
class Forest(RandomForestRegressor):
    size             # Número de árvores (1000 por padrão)
    Fold             # Número do fold em processamento
    nameFile         # Nome do arquivo de cache
    treesName        # Sufixo do arquivo de árvores
```

**Métodos Principais:**
- `fit_forest()`: Avalia uma geração de indivíduos
- `ga()`: Executa o algoritmo genético completo
- `get_Trees()`: Carrega/salva árvores do cache
- `fitLoadTrees()`: Seleciona subset de árvores baseado na máscara

### 5. **Arquive** (ga.py)
Mantém um arquivo/histórico de soluções.

```python
class Arquive:
    size             # Tamanho máximo do arquivo
    mode             # Tipo de fitness a usar
    arq              # Lista de indivíduos
```

---

## Fluxo de Execução

### Fluxo Geral

```
main() 
  ├─ Carregar dados L2R (train, validation, test)
  ├─ Criar Forest (Random Forest com 1000 árvores)
  └─ Para cada fold (1-5):
      ├─ Se n_gerações == 1: Testar RF padrão (todas as árvores)
      └─ Senão: Executar GA
          ├─ forest.ga() - Algoritmo Genético
          │   ├─ GenerateInicial() - Criar população (75 indivíduos)
          │   ├─ fit_forest() - Avaliar fitness
          │   ├─ Para cada geração (1-30):
          │   │   ├─ GA.GA() - Operadores genéticos
          │   │   ├─ fit_forest() - Avalia nova geração
          │   │   ├─ ElitistGroup() - Seleciona elites
          │   │   └─ Arquivo.appendBag() - Armazena população
          │   └─ Retorna melhor indivíduo
          └─ Imprimir resultados
```

### Fluxo Detalhado da Função `fit_forest()`

1. **Carregamento de Árvores**
   - Se as árvores não foram criadas, executar `fit()` na Forest
   - Carregar todas as árvores em memória

2. **Previsão Base**
   - Usar todas as 1000 árvores para fazer previsão baseline
   - Calcular NDCG do baseline

3. **Para Cada Indivíduo**
   - Se ainda não tem fitness:
     - Selecionar subset de árvores conforme a máscara
     - Fazer previsões com o subset
     - Calcular NDCG (método "ndcg")
     - Calcular TRISK (método "trisk") - Risco relativo ao baseline
     - Para SPEA2: Calcular dominância Pareto

---

## Módulos Detalhados

### `__main__.py`
**Responsabilidade**: Ponto de entrada e orquestração de experimentos.

#### Configurações Principais:
```python
colecao = "web10k"                      # Dataset: "web10k" ou "2003_td_dataset"
numero_de_estimadores = 1000            # Árvores na Random Forest
ex_vetor_n_arvores = [300, 500, 750]    # Diferentes tamanhos a testar
ex_geracoes = [30]                      # Número de gerações do GA
ex_n_individuos = [75]                  # Tamanho da população
```

#### Fluxos Implementados:
1. **executar_por_fold = 1**: Executa GA para cada fold
2. **comparar = 1**: Compara performance de diferentes configurações
3. **executar_threads = 1**: Executa múltiplos experimentos em paralelo

#### Função `folds_works()`
Executa o GA para todos os 5 folds.
- **Entrada**: Configurações GA, caminho dos dados, parâmetros de GA
- **Saída**: Arquivo CSV com resultados

#### Função `imprimir_individuo()`
Salva resultados de um indivíduo em arquivo CSV.
- **Formato**: fold, n_arvores, NDCG, TRISK, geração, etc.

---

### `forest.py`
**Responsabilidade**: Gerenciar Random Forest e avaliar indivíduos do GA.

#### Classe `Forest`

**Atributos:**
- `rota`: Diretório para armazenar árvores em cache
- `size`: Número total de árvores
- `Fold`: Fold atual em processamento
- `nameFile`: Nome base dos arquivos de cache
- `treesName`: Sufixo ".All.Trees.pickle"

**Método `fit_forest(geracao, VetorTrain, VetorVali, mode="ndcg")`**

Avalia fitness de uma população de indivíduos.

**Parâmetros:**
- `geracao`: Lista de indivíduos a avaliar
- `VetorTrain`: Dados de treinamento (Consultas)
- `VetorVali`: Dados de validação (Consultas)
- `mode`: Tipo de fitness ("ndcg", "trisk", "spea2")

**Algoritmo:**
1. Carregar todas as árvores (se não existirem, treinar)
2. Para cada indivíduo sem fitness:
   - Selecionar árvores conforme máscara
   - Fazer previsão
   - Calcular NDCG
   - Calcular TRISK relativo
3. Se mode="spea2": Calcular dominância Pareto e fitness SPEA2
4. Retornar população com fitness calculado

**Método `ga(Vet_Train_Vali, max_num_geracoes, n_treesForest, ...)`**

Executa o algoritmo genético completo.

**Parâmetros:**
- `Vet_Train_Vali`: [VetorTrain, VetorValidacao]
- `max_num_geracoes`: Número de gerações (ex: 30)
- `n_treesForest`: Tamanho da população (ex: 75)
- `selecaoTorneio`: 1=Torneio, 0=Roleta
- `crossoverUniforme`: 1=Uniforme, 0=Um ponto
- `elitist`: 1=Com elitismo, 0=Sem
- `numero_genes`: Número de genes/árvores (ex: 1000)
- `mode`: Tipo de fitness

**Algoritmo:**
1. Criar população inicial aleatória
2. Avaliar fitness com `fit_forest()`
3. Para cada geração:
   - Aplicar operadores genéticos (seleção, crossover, mutação)
   - Avaliar nova geração
   - Selecionar população para próxima geração (elitismo opcional)
   - Armazenar em arquivo (Arquive)
4. Retornar melhor indivíduo do arquivo

**Método `get_Trees(maskList="all")`**

Carrega árvores do cache ou retorna subset.

- `maskList="all"`: Retorna todas as árvores
- `maskList="chess"`: Retorna árvores em padrão xadrez (i % 2 == 0)
- Outro array: Retorna árvores conforme máscara

**Método `fitLoadTrees(X, y, forest, all_trees)`**

Configura a Forest com um subset de árvores.
- `forest`: Array 0/1 indicando quais árvores usar
- `all_trees`: Todas as árvores disponíveis
- Monta `self.estimators_` com o subset

---

### `ga.py`
**Responsabilidade**: Implementar o algoritmo genético.

#### Classe `Consultas`
Encapsula dados de entrada para uma sesão.

```python
class Consultas:
    x  # shape: (n_samples, n_features) - Features
    y  # shape: (n_samples,) - Labels/relevância
    q  # shape: (n_samples,) - Query IDs
```

#### Classe `Individuo`
Representa uma solução candidata (um indivíduo).

**Atributos:**
- `mascara`: Array binário [0,1,...,1] (máscara de seleção de árvores)
- `geracao`: Número da geração
- `fitnessNDCG`: NDCG médio
- `vetFitnessNDCG`: NDCG por query
- `fitnessTrisk`: TRISK (risco relativo)
- `vetFitnessTrisk`: TRISK por query
- `fitnessSpea2`: Fitness SPEA2
- `bool_fit`: 0/1 indicando se fitness foi calculado

**Métodos:**
- `get_fita()`: Retorna a máscara
- `get_fitness(tipo)`: Retorna fitness conforme tipo (0-5)
- `set_fitness(fitness, tipo)`: Define fitness
- `len()`: Retorna tamanho da máscara

#### Classe `GeneticAlgorithm`
Implementa operadores genéticos.

**Atributos Importantes:**
- `tamanho_populacao`: Quantos indivíduos por geração (default: 70)
- `num_caracteristicas`: Quantos genes por indivíduo (default: 1000)
- `probabilidade`: Probabilidade de crossover (default: 0.5)
- `probabilidadeMutacao`: Probabilidade de mutação (default: 0.3)
- `elitist`: Usar seleção elitista? (0/1)
- `bool_selecaoTorneio_Roleta`: Tipo de seleção (1=Torneio, 0=Roleta)
- `bool_crossoverUniforme_Ponto`: Tipo de crossover (1=Uniforme, 0=Ponto)

**Método `GA(geracao_com_fitness, numero_da_geracao, tipo)`**

Executa uma geração completa do GA.

**Algoritmo:**
```
Para i = 1 até tamanho_populacao/2:
  1. Selecionar 2 pais (Torneio ou Roleta)
  2. Aplicar crossover
  3. Com probabilidade, aplicar mutação em cada filho
  4. Adicionar filhos à nova geração
Retornar nova geração
```

**Método `GenerateInicial()`**

Cria população inicial aleatória.
- Gera `tamanho_populacao` indivíduos
- Cada gene tem 50% de chance de ser 0 ou 1
- Primeiro indivíduo é sempre all-ones (todas as árvores)

**Método `Selecao(tipo=1)`**

Seleciona 2 pais para reprodução.

- `tipo=0`: **Seleção por Roleta**
  - Probabilidade proporcional ao fitness
  - Indivíduos com melhor fitness têm maior chance

- `tipo=1`: **Seleção por Torneio**
  - Seleciona 2 indivíduos aleatoriamente
  - Retorna o com melhor fitness

**Método `Torneio(quantidade_competidores=2)`**

Implementa seleção por torneio.
- Seleciona `quantidade_competidores` indivíduos aleatoriamente
- Retorna o com melhor fitness

**Método `Crossover(individuoA, individuoB, tipo=1)`**

Cria filhos combinando pais.

- `tipo=0`: **Crossover em Um Ponto**
  - Seleciona ponto aleatório
  - Troca genes após esse ponto

- `tipo=1`: **Crossover Uniforme**
  - Para cada gene, com probabilidade `self.probabilidade`:
    - Troca gene entre pais

**Método `Mutacao(mascara, tipo=1)`**

Modifica aleatoriamente genes.

- `tipo=1`: **Mutação Uniforme**
  - Para cada gene, com probabilidade `self.probabilidadeMutacao`:
    - Inverte gene (0→1 ou 1→0)

- `tipo=0`: **Mutação em Um Ponto**
  - Seleciona ponto aleatório
  - Inverte gene naquele ponto

**Método `ElitistGroup(populacaoA, populacaoB)`**

Implementa seleção elitista.
- Combina população anterior e nova
- Ordena por fitness (descendente)
- Retorna os melhores `tamanho_populacao` indivíduos

**Método `setTypeFitness(tipo)`**

Define qual fitness usar (índice interno).

**Método `MyFitness(individuo)`**

Retorna o fitness atual de um indivíduo.

#### Classe `Arquive`
Mantém histórico de soluções.

**Método `fit(individuo)`**
Calcula fitness de um indivíduo conforme `self.mode`.

**Método `getBag(params)`**
- `params='default'`: Retorna toda a lista
- `params=1`: Retorna primeiro (melhor)
- Outro número: Retorna elemento naquela posição

**Método `appendBag(populacao)`**
Adiciona população ao arquivo e ordena por fitness.

---

### `h_l2rMeasures.py`
**Responsabilidade**: Implementar métricas de Learning-to-Rank.

**Função `modelEvaluation(Consultas, scores, topK=64)`**

Calcula NDCG para um modelo.

**Parâmetros:**
- `Consultas`: Objeto com `y` (labels) e `q` (query IDs)
- `scores`: Previsões do modelo
- `topK`: Usar top K resultados (default: 64)

**Retorna:**
- `ndcg_valores`: Array com NDCG por query
- Média de NDCG

**Detalhes de Cálculo:**
- Para cada query:
  - Rankear documentos por score
  - Calcular DCG (Discounted Cumulative Gain)
  - Calcular IDCG ideal
  - NDCG = DCG / IDCG

**Função `getNdcgRelScore(dataset, label)`**

Retorna score de relevância conforme dataset.

- `dataset="web10k"`: [0, 1, 3, 7, 15]
- `dataset="letor"`: [0, 1, 3]

**Função `getTRisk(valor_ndcg, base_ndcg, alfa)`**

Calcula TRISK (risco relativo).

**Parâmetros:**
- `valor_ndcg`: NDCG do modelo candidato
- `base_ndcg`: NDCG do baseline
- `alfa`: Fator de penalidade (default: 5)

**Algoritmo:**
- Z_score = (valor - baseline) / sqrt(baseline)
- Se degradação: Z_score *= (1 + alfa)
- TRISK = norma cumulativa (Z_score)

**Função `getGeoRisk(mat, alpha=0.05)`**

Calcula risco geométrico (para análise de robustez).

**Parâmetros:**
- `mat`: Matriz (queries × sistemas)
- `alpha`: Significância estatística

**Função `getQueries(y, q)`**

Extrai queries e reorganiza dados.

**Função `readingFile(file)`**

Lê valores "mean=>" de um arquivo.

**Função `relevanceTest(dataset, value)`**

Classifica relevância binária.

- `web10k`: Relevante se value > 1
- `letor`: Relevante se value > 0

---

### `h_functionsFilter.py`
**Responsabilidade**: Análise Pareto e dominância.

#### Classe `basicStructure`
Encapsula métricas.

```python
class basicStructure:
    marginal         # Lista de valores agregados
    mat              # Matriz de valores por query
    pvalue           # P-value estatístico
    variance         # Variância
    greaterIsBetter  # 1 se maior é melhor, 0 se menor
```

#### Classe `dataset`
Encapsula dados.

```python
class dataset:
    q  # Query IDs
    x  # Features
    y  # Labels
```

**Função `obtainDominace(obj1, obj2, obj3, prediction, similarity, risk, variance, vetFeatures, nFeatures)`**

Calcula dominância Pareto entre objetivos.

**Parâmetros:**
- `obj1, obj2, obj3`: Nomes dos objetivos (ex: "prediction", "trisk")
- `prediction`: Valores de NDCG
- `similarity/risk/variance`: Métricas
- `vetFeatures`: Índices dos indivíduos
- `nFeatures`: Número de indivíduos

**Retorna:**
Array com fitness SPEA2 para cada indivíduo.

**Algoritmo:**
- Para cada par de indivíduos:
  - Se X domina Y: X domina este Y
  - Se Y domina X: X é dominado por Y
- Fitness = 1 / (número de dominadores)
- Se não dominado: Fitness = 2

**Função `dominate2(x, y, obj1, obj2, ...)`**

Verifica se X domina Y em 2 objetivos.

- NDCG: Maior é melhor
- TRISK: Menor é melhor

**Função `dominate3(x, y, obj1, obj2, obj3, ...)`**

Verifica se X domina Y em 3 objetivos.

---

### `h_l2rMiscellaneous.py`
**Responsabilidade**: Utilitários de dados.

**Função `load_L2R_file(TRAIN_FILE_NAME, MASK)`**

Carrega arquivo de dados L2R.

**Formato de Entrada:**
```
relevancia qid:query_id feature_id:valor feature_id:valor ... # comentário
```

**Parâmetros:**
- `TRAIN_FILE_NAME`: Caminho do arquivo
- `MASK`: Array [0,1,...] para selecionar features

**Retorna:**
- `X`: Matriz de features (n_samples × n_features_selecionadas)
- `y`: Array de relevâncias
- `q`: Array de query IDs

**Algoritmo:**
1. Contar linhas e features
2. Criar matrizes vazias
3. Para cada linha:
   - Extrair relevância, query ID, features
   - Aplicar MASK para selecionar features
   - Preencher matrizes
4. Retornar X, y, q

**Função `getIdFeatureOrder(vet, per, totalFeatures)`**

Retorna features mais importantes.

**Parâmetros:**
- `vet`: Array de importâncias
- `per`: Percentual (0-1) ou count
- `totalFeatures`: Total de features

**Retorna:**
Máscara string "110101..." indicando features selecionadas.

---

## Configurações e Parâmetros

### Parâmetros da Random Forest
```python
n_estimators = 1000    # Número de árvores
n_jobs = 4             # Processadores paralelos
criterion = 'mse'      # Critério de divisão (regressor)
bootstrap = True       # Usar bootstrap sampling
```

### Parâmetros do Algoritmo Genético
```python
Geração Inicial
├─ tamanho_populacao = 75       # Quantos indivíduos
├─ num_caracteristicas = 1000   # Quantos genes (árvores)
└─ primeiro_ind = all_ones      # Primeira solução é RF completa

Operadores Genéticos
├─ tipo_seleção = 1             # 1=Torneio, 0=Roleta
├─ tipo_crossover = 1           # 1=Uniforme, 0=Um ponto
├─ probabilidade_crossover = 0.5
├─ probabilidade_mutacao = 0.3
└─ elitismo = 1                 # 1=Usar elitismo, 0=Sem

Evolução
├─ número_gerações = 30         # Quantas gerações
├─ tamanho_arquivo = 150        # Melhor_população × 2
└─ modo = "spea2"               # "ndcg", "trisk", "spea2"
```

### Datasets Suportados

**Web10k**
- 136 features
- 4 níveis de relevância [0, 1, 3, 7, 15]
- 5 folds
- Arquivo: `../Colecoes/web10k/Fold{1-5}/{Norm.train,Norm.vali,Norm.test}.txt`

**2003 Terabyte Dataset**
- 64 features
- 2 níveis de relevância [0, 1, 3]
- 5 folds

---

## Exemplos de Uso

### Exemplo 1: Executar GA para um Dataset

```python
# Configurar
colecao = "web10k"
MASK = [1] * 136  # Usar todas as 136 features
numero_de_estimadores = 1000

# Rodar GA para todos os 5 folds
folds_works(
    ga=[1, 1, 1],           # Torneio, Uniforme, Elitismo
    rota_pasta_letor="../Colecoes/web10k/",
    n_geracoes=30,          # 30 gerações
    n_individuos=75,        # População de 75
    n_arvores=1000,         # 1000 árvores total
    mode="spea2"            # Usar SPEA2
)
```

### Exemplo 2: Testar múltiplas configurações

```python
# Executar com diferentes números de árvores
for n_arvores in [300, 500, 750, 1000]:
    for n_geracoes in [30, 50]:
        folds_works(
            ga=[1, 1, 1],
            rota_pasta_letor="../Colecoes/web10k/",
            n_geracoes=n_geracoes,
            n_individuos=75,
            n_arvores=n_arvores,
            mode="spea2"
        )
```

### Exemplo 3: Comparar RF padrão vs GA otimizado

```python
forest = Forest(n_estimators=1000, n_jobs=4)

# Carregar dados
X, y, z = load_L2R_file("train.txt", MASK)
X_val, y_val, z_val = load_L2R_file("vali.txt", MASK)
X_test, y_test, z_test = load_L2R_file("test.txt", MASK)

Vet_train = Consultas(X, y, z)
Vet_vali = Consultas(X_val, y_val, z_val)
Vet_test = Consultas(X_test, y_test, z_test)

# RF padrão (todas as árvores)
ind_baseline = Individuo(np.ones(1000), 1)
forest.fit_forest([ind_baseline], Vet_train, Vet_test)

# Executar GA
ind_otimizado = forest.ga(
    [Vet_train, Vet_vali],
    max_num_geracoes=30,
    n_treesForest=75,
    numero_genes=1000,
    mode="spea2"
)
```

---

## Fluxo Detalhado de Execução (SPEA2)

### Geração Inicial
```
1. GenerateInicial()
   └─ Cria 75 indivíduos aleatórios
   └─ Primeiro indivíduo = all-ones (todas as 1000 árvores)

2. fit_forest(geração_inicial)
   └─ Para cada indivíduo:
      ├─ Seleciona árvores conforme máscara
      ├─ Faz previsão em validação
      ├─ Calcula NDCG
      └─ Calcula TRISK relativo ao baseline

   └─ Como mode="spea2":
      ├─ Matriz NDCG (75 indivíduos × N queries)
      ├─ Matriz TRISK (75 indivíduos × N queries)
      ├─ Calcula dominância Pareto
      └─ Fitness = 1 / (dominadores + 1)
```

### Cada Geração (1-30)
```
1. GA.GA(população_atual, geração)
   └─ Novo loop por metade da população:
      ├─ Seleciona 2 pais (Torneio)
      ├─ Crossover uniforme
      ├─ Mutação em cada filho (30% de chance)
      └─ Adiciona filhos à nova geração

2. fit_forest(nova_geração)
   └─ Avalia fitness (mesmo que Geração Inicial)

3. ElitistGroup(geração_anterior, nova_geração)
   └─ Combina 75 + 75 = 150 indivíduos
   └─ Ordena por fitness (SPEA2)
   └─ Retorna melhores 75

4. Arquivo.appendBag(população_selecionada)
   └─ Armazena no máximo 150 melhores soluções
```

### Pós-GA
```
1. getBag(1)
   └─ Retorna o melhor indivíduo do arquivo

2. fit_forest([melhor_indivíduo], train, test)
   └─ Avaliação final no conjunto de teste

3. imprimir_individuo()
   └─ Salva resultados em CSV:
      - Fold, n_árvores, NDCG, TRISK
      - Geração, tamanho_pop, configuração GA
      - Máscara binária (quais árvores foram selecionadas)
```

---

## Saídas Esperadas

### Arquivos CSV Resultados
Localização: `FinalResultados/`

**Original_*.csv**: Baseline (RF com todas as árvores)
```
fold;n_arvores;ndcg;trisk;geracao;tamanho_pop;selecao;crossover;elitismo;mascara
1;1000;0.358;0.24;1;1;1;1;1;1111...1111
```

**TheBests_*.csv**: Resultado do GA otimizado
```
fold;n_arvores;ndcg;trisk;geracao;tamanho_pop;selecao;crossover;elitismo;mascara
1;1000;0.365;0.18;30;75;1;1;1;0110...0101
```

### Estrutura de Diretórios Criada
```
Fold1000/  (ou Fold{tamanho}/)
├─ forest_Fold1.All.Trees.pickle      # Cache das árvores treinadas
├─ forest_Fold2.All.Trees.pickle
├─ ...
└─ forest_Fold5.All.Trees.pickle
```

---

## Interpretação de Resultados

### Coluna NDCG
- Valor: 0.0 - 1.0
- **Significado**: Qualidade do ranking das previsões
- **Maior é melhor**: Sim
- **Comparação**: Comparar TheBests com Original para medir melhoria

### Coluna TRISK
- Valor: 0.0 - 1.0
- **Significado**: Risco relativo ao baseline
- **Menor é melhor**: Sim
- **Interpretação**: 
  - Próximo de 0: Modelo muito superior ao baseline
  - Próximo de 1: Modelo similar ao baseline
  - \> 1: Modelo inferior ao baseline (raro)

### Máscara Binária
- **Exemplo**: `110101...0101`
- **Significado**: Quais das 1000 árvores foram selecionadas
- **Uso**: Contar quantas árvores foram selecionadas (contagem de 1s)
- **Esperado**: Menos árvores que o baseline (redução de tamanho do modelo)

### Ganho Esperado
1. **NDCG**: Manutenção ou ligeira melhoria (esperado ≈ same)
2. **TRISK**: Redução (menor risco = melhor generalização)
3. **Árvores**: Redução de ~30-50% comparado a 1000

---

## Troubleshooting

### Problema: Arquivo de dados não encontrado
**Solução**: Verificar caminho em `rota_pasta_letor` e estrutura de folds (Fold1, Fold2, ..., Fold5)

### Problema: Memória insuficiente
**Solução**: 
- Reduzir `n_jobs` em Forest
- Reduzir `tamanho_populacao` em GA
- Usar `mode="ndcg"` em vez de "spea2"

### Problema: GA não melhora fitness
**Solução**:
- Aumentar `max_num_geracoes`
- Aumentar `tamanho_populacao`
- Aumentar `probabilidadeMutacao`
- Mudar `bool_selecaoTorneio_Roleta`

### Problema: Muito tempo de execução
**Solução**:
- Reduzir `numero_de_estimadores` (ex: 500 em vez de 1000)
- Reduzir `max_num_geracoes`
- Aumentar `n_jobs` para paralelização
- Executar foldsworks em paralelo (já implementado)

---

## Notas Técnicas

### Algoritmo SPEA2 vs NDCG/TRISK
- **NDCG**: Otimiza apenas qualidade
- **TRISK**: Otimiza risco relativo
- **SPEA2**: Multi-objetivo (balanceia NDCG vs TRISK via dominância Pareto)

### Otimização em Scikit-learn
- Usa Random Forest com regressão (MSE)
- Qualquer feature selection impacta as árvores (retraining não necessário)
- Cache de árvores permite reutilização eficiente

### Paralelização
- `n_jobs=4`: Usa 4 cores para treinar/prever em paralelo
- `mp.Process`: Processa múltiplos folds em paralelo
- Cada fold pode usar diferentes números de árvores

---

**Última atualização**: 2024
**Versão**: 1.0
**Autor**: PIBIC Team
