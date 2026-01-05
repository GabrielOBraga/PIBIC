# Guia Rápido - RF_SPEA2_WEB

## Fluxo de Execução em 5 Passos

### 1. **Carregar Dados**
```python
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
from Forest_GA.PIBIC.ga import Consultas

MASK = [1] * 136  # Selecionar todas as 136 features
X, y, q = load_L2R_file("Fold1/Norm.train.txt", MASK)
Vet_train = Consultas(X, y, q)
```

### 2. **Criar Random Forest**
```python
from Forest_GA.forest import Forest

forest = Forest(n_estimators=1000, n_jobs=4)
forest.Fold = 1  # Qual fold está processando
forest.size = 1000
```

### 3. **Indivíduo & População**
```python
from Forest_GA.PIBIC.ga import Individuo
import numpy as np

# Criar um indivíduo (máscara binária)
mascara = np.random.randint(0, 2, 1000)  # 1000 genes
ind = Individuo(mascara, geracao=1)

# Ou criar população inicial
geracao_inicial = [Individuo(np.random.randint(0, 2, 1000), 1) for _ in range(75)]
```

### 4. **Avaliar Fitness**
```python
# fit_forest calcula NDCG e TRISK
geracao_com_fitness = forest.fit_forest(
    geracao_inicial,           # Indivíduos a avaliar
    Vet_train,                # Dados treinamento
    Vet_vali,                 # Dados validação
    mode="spea2"              # Tipo de fitness
)
```

### 5. **Executar GA Completo**
```python
melhor_individuo = forest.ga(
    [Vet_train, Vet_vali],
    max_num_geracoes=30,
    n_treesForest=75,
    selecaoTorneio=1,         # 1=Torneio, 0=Roleta
    crossoverUniforme=1,      # 1=Uniforme, 0=Ponto
    elitist=1,                # 1=Com elitismo, 0=Sem
    numero_genes=1000,
    mode="spea2"
)
```

---

## Estrutura de Classes

```
Forest (RandomForestRegressor)
├─ fit_forest(geracao, VetorTrain, VetorVali, mode)
│  └─ Avalia fitness de indivíduos
├─ ga(Vet_Train_Vali, max_num_geracoes, ...)
│  └─ Executa GA completo
├─ get_Trees(maskList)
│  └─ Carrega/seleciona árvores
└─ fitLoadTrees(X, y, forest, all_trees)
   └─ Configura Forest com subset de árvores

GeneticAlgorithm
├─ GenerateInicial()
│  └─ Cria população inicial aleatória
├─ GA(geracao_com_fitness, numero_da_geracao, tipo)
│  └─ Executa uma geração
├─ Selecao(tipo)
│  └─ Seleciona pais (Torneio/Roleta)
├─ Crossover(individuoA, individuoB, tipo)
│  └─ Cria filhos
├─ Mutacao(mascara, tipo)
│  └─ Modifica genes aleatoriamente
├─ ElitistGroup(populacaoA, populacaoB)
│  └─ Seleciona melhores indivíduos
└─ MyFitness(individuo)
   └─ Retorna fitness de um indivíduo

Individuo
├─ mascara: Array binário [0,1,...,1]
├─ fitnessNDCG: Qualidade (0-1)
├─ fitnessTrisk: Risco relativo (0-1)
├─ fitnessSpea2: Multobjetivo
├─ bool_fit: 0/1 se foi avaliado
└─ get_fitness(tipo): Retorna fitness

Consultas
├─ x: Matriz features
├─ y: Array labels
└─ q: Array query IDs

Arquive
├─ arq: Lista de melhores indivíduos
├─ appendBag(novos): Adiciona e ordena
└─ getBag(n): Retorna n melhores
```

---

## Métricas Explicadas

### NDCG (Normalized Discounted Cumulative Gain)
- **Intervalo**: 0 - 1
- **Interpretação**: Qualidade do ranking (1 = perfeito)
- **Objetivo**: MAXIMIZAR
- **Fórmula**: DCG / IDCG

### TRISK (Temporal Risk)
- **Intervalo**: 0 - ∞
- **Interpretação**: Risco relativo ao baseline
- **Objetivo**: MINIMIZAR
- **Valores típicos**: 0.1 - 2.0
- **Significado**:
  - 0.5 = Modelo tem 50% de risco (melhor que baseline)
  - 1.0 = Mesmo risco que baseline
  - 2.0 = Dobro do risco (pior que baseline)

### SPEA2 Fitness
- **Cálculo**: 1 / (número de dominadores + 1)
- **Intervalo**: 0 - 2
- **Interpretação**: Fitness multobjetivo
- **Vantagem**: Balanceia NDCG vs TRISK

---

## Tipos de Seleção

| Tipo | Método | Vantagem | Desvantagem |
|------|--------|----------|-------------|
| Torneio (1) | Seleciona k indivíduos, retorna melhor | Simples, rápido | Menos diversidade |
| Roleta (0) | Probabilidade proporcional ao fitness | Maior diversidade | Pode escolher fracos |

---

## Tipos de Crossover

| Tipo | Método | Vantagem | Desvantagem |
|------|--------|----------|-------------|
| Uniforme (1) | Trocar genes individualmente | Maior exploração | Quebra blocos bons |
| Um Ponto (0) | Trocar após ponto aleatório | Preserva blocos | Menor exploração |

---

## Tipos de Mutação

| Tipo | Método | Vantagem | Desvantagem |
|------|--------|----------|-------------|
| Uniforme (1) | Mutar cada gene independentemente | Maior diversidade | Mais disruptivo |
| Um Ponto (0) | Mutar apenas 1 gene | Exploração local | Menos diversidade |

---

## Interpretando Resultados

### Arquivo: `FinalResultados/TheBests_1000.csv`

```
fold;n_arvores;ndcg;trisk;geracao;tamanho_pop;selecao;crossover;elitismo;mascara
1;1000;0.365;0.18;30;75;1;1;1;011010110...
```

**Interpretação**:
- **fold=1**: Experimento no fold 1
- **n_arvores=1000**: Total de 1000 árvores
- **ndcg=0.365**: Qualidade do ranking (36.5%)
- **trisk=0.18**: Risco é 18% do baseline (MELHOR!)
- **geracao=30**: Evoluiu por 30 gerações
- **tamanho_pop=75**: População de 75 indivíduos
- **selecao=1**: Usou Torneio
- **crossover=1**: Usou Crossover Uniforme
- **elitismo=1**: Usou Elitismo
- **mascara**: Quais árvores foram selecionadas
  - Contar "1"s = número de árvores selecionadas
  - Esperado: ~400-600 (redução de 40-60%)

---

## Problemas Comuns & Soluções

### Problema: "Arquivo não encontrado"
```python
# Verificar estrutura
# Fold1/
#   ├─ Norm.train.txt
#   ├─ Norm.vali.txt
#   └─ Norm.test.txt
```

### Problema: "Memória insuficiente"
```python
# Reduzir complexidade
forest = Forest(n_estimators=500, n_jobs=2)  # Menos árvores e cores
```

### Problema: "GA não converge"
```python
# Aumentar variabilidade
GA.probabilidadeMutacao = 0.5  # Aumentar de 0.3 para 0.5
GA.tamanho_populacao = 100     # Aumentar de 75 para 100
```

### Problema: "Muito lento"
```python
# Paralelizar
forest = Forest(n_estimators=1000, n_jobs=8)  # Mais cores
# Ou usar já implementado no __main__.py
executar_threads = 1
```

---

## Callbacks & Hooks (Avançado)

### Verificar progresso durante GA
```python
# PrintExcelGA salva resultados por geração
# Arquivo: N_1000/Fold_1/G_1Ind_75GA_1111_store.csv

# Ler durante execução
import pandas as pd
df = pd.read_csv('N_1000/Fold_1/G_1Ind_75GA_1111_store.csv')
print(df.iloc[-1])  # Última linha (gerações mais recentes)
```

### Customizar função de fitness
```python
# Editar em forest.py fit_forest():
# Adicionar novo modo após modo="spea2"
if mode == "custom":
    # Seu código aqui
    ind.fitnessCustom = valor
```

---

## Configurações Padrão vs Recomendadas

| Parâmetro | Padrão | Para Exploração | Para Convergência |
|-----------|--------|-----------------|-------------------|
| tamanho_populacao | 70 | 100+ | 50 |
| max_gerações | 30 | 50+ | 20 |
| probabilidade_crossover | 0.5 | 0.7+ | 0.3 |
| probabilidade_mutacao | 0.3 | 0.5+ | 0.1 |
| elitismo | 0 | 1 | 1 |
| seleção | Torneio | Roleta | Torneio |

---

## Pipeline Completo (Exemplo)

```python
# Configurações
colecao = "web10k"
MASK = [1] * 136

# Dados
X_tr, y_tr, q_tr = load_L2R_file("../Colecoes/web10k/Fold1/Norm.train.txt", MASK)
X_va, y_va, q_va = load_L2R_file("../Colecoes/web10k/Fold1/Norm.vali.txt", MASK)
X_te, y_te, q_te = load_L2R_file("../Colecoes/web10k/Fold1/Norm.test.txt", MASK)

Vet_train = Consultas(X_tr, y_tr, q_tr)
Vet_vali = Consultas(X_va, y_va, q_va)
Vet_test = Consultas(X_te, y_te, q_te)

# Forest
forest = Forest(n_estimators=1000, n_jobs=4)
forest.Fold = 1
forest.size = 1000

# GA
print("Executando GA...")
best = forest.ga(
    [Vet_train, Vet_vali],
    max_num_geracoes=30,
    n_treesForest=75,
    selecaoTorneio=1,
    crossoverUniforme=1,
    elitist=1,
    numero_genes=1000,
    mode="spea2"
)

# Avaliação final
resultado = forest.fit_forest([best], Vet_train, Vet_test, mode="ndcg")

print(f"NDCG: {resultado[0].fitnessNDCG:.4f}")
print(f"TRISK: {resultado[0].fitnessTrisk:.4f}")
print(f"Árvores selecionadas: {int(sum(best.mascara))}")
```

---

## Recursos Adicionais

- `DOCUMENTATION.md`: Documentação técnica completa
- `__main__.py`: Exemplos de uso
- `h_l2rMeasures.py`: Cálculo de métricas L2R
- `h_functionsFilter.py`: Análise de dominância Pareto

---

**Versão**: 1.0 | **Última atualização**: 2024 | **Status**: Documentado ✓
