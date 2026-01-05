# RF_TRISK - Exemplos Práticos

## Índice
1. [Exemplo 1: Execução Completa Padrão](#exemplo1)
2. [Exemplo 2: Ajuste de Parâmetros GA](#exemplo2)
3. [Exemplo 3: Teste Individual (Sem GA)](#exemplo3)
4. [Exemplo 4: Leitura e Análise de Resultados](#exemplo4)
5. [Exemplo 5: Otimização Customizada](#exemplo5)

---

## Exemplo 1: Execução Completa Padrão {#exemplo1}

Executa GA com configuração padrão para todos os 5 folds.

### Código Principal (`__main__.py`)

```python
def main():
    # Configuração de flags
    comparar = 0                              # Desativar teste individual
    executar_por_fold = 1                     # ATIVAR GA por fold
    executar_threads = 0                      # Desativar execução paralela
    
    # Configuração de dataset
    rota_pasta_letor = "../Colecoes/2003_td_dataset/"
    numero_de_estimadores = 1000
    
    # Máscara: usar todos os 64 atributos
    MASK = [1] * 64
    
    # Executar GA por fold
    if executar_por_fold:
        check = folds_works(
            [1, 1, 1],                        # [selecao, crossover, elitismo]
            rota_pasta_letor,                 # Caminho LETOR
            30,                               # 30 gerações
            75,                               # 75 indivíduos por geração
            1000,                             # 1000 árvores totais
            "tRisk"                           # Métrica: TRISK
        )
        if check == 1:
            print("GA finalizado com sucesso para todos os 5 folds")

if __name__ == '__main__':
    main()
```

### Saída Esperada

```
Lendo Arquivos ... (Fold 1)
Treinando RandomForest base (1000 árvores)...
Gerando população inicial...
Geração 1/30: Fitness médio = -0.0234
Geração 2/30: Fitness médio = -0.0312
...
Geração 30/30: Fitness médio = -0.0524
Fold 1 concluído!
Resultado salvo em: FinalResultados/TheBests_1000.csv

[Repetindo para Fold 2-5]

finished
```

### Arquivo Gerado: `FinalResultados/TheBests_1000.csv`

```csv
fold;n_arvores;fitness(trisk);map;num_geracao;total_geracao;geracao_criacao;selecao;crossover;elitismo;mascara_binaria
1;1000;-0.0524;0.3421;30;75;28;1;1;1;11010101011010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101
```

### Interpretação dos Resultados

- **fitness(trisk) = -0.0524**: Melhoria de ~5.24% em TRISK (valores negativos são melhores)
- **map = 0.3421**: MAP médio de 0.3421 (relevância média)
- **mascara_binaria**: 1=usar árvore, 0=descartar árvore (neste caso, 507 árvores de 1000)

---

## Exemplo 2: Ajuste de Parâmetros GA {#exemplo2}

Varia parâmetros de GA para encontrar melhor configuração.

### Código: Teste de Diferentes Configurações

```python
def main():
    comparar = 0
    executar_por_fold = 0  # Desativar GA normal
    executar_threads = 1   # ATIVAR execução paralela
    
    rota_pasta_letor = "../Colecoes/2003_td_dataset/"
    
    # Vetores para testar diferentes configurações
    ex_vetor_n_arvores = [500, 1000, 2000]      # Varia tamanho floresta
    ex_geracoes = [20, 30, 50]                   # Varia gerações
    ex_n_individuos = [50, 75, 100]              # Varia população
    
    # Testa todas as combinações em paralelo
    for nn in ex_vetor_n_arvores:
        for gg in ex_geracoes:
            for ii in ex_n_individuos:
                # Executa: 3 * 3 * 3 = 27 configurações diferentes
                # Cada uma em thread separada
                processes = [
                    mp.Process(
                        target=folds_works,
                        args=([1, 1, 1], rota_pasta_letor, gg, ii, nn, "tRisk")
                    )
                    for _ in range(3)
                ]
                
                for p in processes:
                    p.start()
                for p in processes:
                    p.join()
                
                print(f"Concluído: n_arvores={nn}, geracoes={gg}, populacao={ii}")
```

### Interpretação de Resultados Comparativos

Após executar todas as combinações, analise o arquivo `FinalResultados/TheBests_*.csv`:

```python
import pandas as pd

# Lê resultados
df = pd.read_csv('FinalResultados/TheBests_1000.csv', sep=';')

# Agrupa por configuração GA e calcula média
grupos = df.groupby(['selecao', 'crossover', 'elitismo'])['fitness'].agg(['mean', 'std'])

print("Melhores configurações GA:")
print(grupos.sort_values('mean'))  # Menor (mais negativo) é melhor

# Exemplo saída:
#         mean    std
# 1,1,1  -0.052  0.008   # Melhor
# 1,0,1  -0.041  0.012   # Bom
# 0,1,1  -0.038  0.015   # Aceitável
```

---

## Exemplo 3: Teste Individual (Sem GA) {#exemplo3}

Testa Random Forest original sem otimização GA (baseline).

### Código Principal

```python
def main():
    comparar = 1  # ATIVAR teste individual
    executar_por_fold = 0  # Desativar GA
    executar_threads = 0
    
    rota_pasta_letor = "../Colecoes/2003_td_dataset/"
    numero_de_estimadores = 1000
    
    RandomForest = Forest(n_estimators=numero_de_estimadores, n_jobs=4)
    
    # Máscara: usar TODAS as árvores (sem otimização)
    forest = np.ones(numero_de_estimadores)  # [1,1,1,...,1]
    
    fold = "1"
    
    # Carrega dados do Fold 1
    nomeArquivoTrain = rota_pasta_letor + "Fold" + fold + "/Norm.train.txt"
    nomeArquivoVali = rota_pasta_letor + "Fold" + fold + "/Norm.vali.txt"
    nomeArquivoTest = rota_pasta_letor + "Fold" + fold + "/Norm.test.txt"
    
    MASK = [1] * 64
    
    print("Lendo Arquivos ...")
    X, y, z = load_L2R_file(nomeArquivoTrain, MASK)
    X2, y2, z2 = load_L2R_file(nomeArquivoVali, MASK)
    X3, y3, z3 = load_L2R_file(nomeArquivoTest, MASK)
    
    # Cria estruturas de dados
    Vetores_Train = Consultas(X, y, z)
    Vetores_Vali = Consultas(X2, y2, z2)
    Vetores_Test = Consultas(X3, y3, z3)
    
    # Configura floresta
    ind = Individuo(forest, 1)  # 1=usar todas as árvores
    RandomForest.Fold = int(fold)
    RandomForest.size = numero_de_estimadores
    
    start = time.clock()
    
    # Treina RF com todas as árvores
    ger = RandomForest.fit_forest([ind], Vetores_Train, Vetores_Test)
    
    final = time.clock() - start
    
    # Salva resultado (tempo em segundos)
    imprimir_individuo(ger[0], numero_de_estimadores, 1, 1, fold, [0, 0, 0], final)
```

### Saída Esperada: `FinalResultados/Original_1000.csv`

```csv
fold;n_arvores;fitness(trisk);map;num_geracao;total_geracao;geracao_criacao;selecao;crossover;elitismo;mascara_binaria
1;1000;0.0000;0.3142;1;1;1;0;0;0;1111111111111111111111111111111111...1111 (1000 1's)
```

**Interpretação**:
- **fitness = 0.0000**: Baseline (sem GA)
- **Comparar com GA**: Se GA dá -0.0524, melhoria = (0 - (-0.0524)) / 0 = 5.24% melhor

---

## Exemplo 4: Leitura e Análise de Resultados {#exemplo4}

Carrega e analisa resultados salvos em CSV.

### Script de Análise

```python
import pandas as pd
import numpy as np

# Lê arquivo de resultados
df = pd.read_csv('FinalResultados/TheBests_1000.csv', sep=';')

# 1. Estatísticas gerais
print("=== ESTATÍSTICAS GERAIS ===")
print(f"Total de indivíduos: {len(df)}")
print(f"Folds processados: {df['fold'].unique()}")
print(f"Gerações por fold: {df['num_geracao'].max()}")
print()

# 2. Melhor indivíduo global
melhor = df.loc[df['fitness'].idxmin()]
print("=== MELHOR INDIVÍDUO ===")
print(f"Fitness (TRISK): {melhor['fitness']:.6f}")
print(f"MAP: {melhor['map']:.4f}")
print(f"Fold: {melhor['fold']}")
print(f"Geração: {melhor['num_geracao']}")
print(f"Número de árvores usadas: {int(melhor['mascara_binaria'].count('1'))}/1000")
print()

# 3. Resultado por Fold
print("=== RESULTADOS POR FOLD ===")
for fold in sorted(df['fold'].unique()):
    subset = df[df['fold'] == fold]
    melhor_fold = subset.loc[subset['fitness'].idxmin()]
    print(f"Fold {fold}: TRISK={melhor_fold['fitness']:.6f}, MAP={melhor_fold['map']:.4f}")
print()

# 4. Convergência do GA
print("=== CONVERGÊNCIA DO GA (Fold 1) ===")
fold1 = df[df['fold'] == 1].sort_values('num_geracao')
print("Geração | Melhor Fitness | MAP")
for _, row in fold1.iterrows():
    print(f"{row['num_geracao']:3d}      | {row['fitness']:13.6f} | {row['map']:.4f}")
print()

# 5. Efeito de cada operador GA
print("=== EFEITO DE OPERADORES GA ===")
ga_config = df.groupby(['selecao', 'crossover', 'elitismo'])['fitness'].agg(['mean', 'count', 'std'])
ga_config.columns = ['Fitness Médio', 'Contagem', 'Desvio Padrão']
print(ga_config.sort_values('Fitness Médio'))
```

### Saída Esperada

```
=== ESTATÍSTICAS GERAIS ===
Total de indivíduos: 150
Folds processados: [1 2 3 4 5]
Gerações por fold: 30

=== MELHOR INDIVÍDUO ===
Fitness (TRISK): -0.058432
MAP: 0.3521
Fold: 3
Geração: 27
Número de árvores usadas: 512/1000

=== RESULTADOS POR FOLD ===
Fold 1: TRISK=-0.052400, MAP=0.3421
Fold 2: TRISK=-0.041800, MAP=0.3287
Fold 3: TRISK=-0.058432, MAP=0.3521
Fold 4: TRISK=-0.035600, MAP=0.3156
Fold 5: TRISK=-0.047200, MAP=0.3389

=== CONVERGÊNCIA DO GA (Fold 1) ===
Geração | Melhor Fitness | MAP
  1      | -0.023400      | 0.3142
  2      | -0.028900      | 0.3187
  3      | -0.032100      | 0.3245
  ...
 28      | -0.052100      | 0.3415
 29      | -0.052100      | 0.3415
 30      | -0.052400      | 0.3421

=== EFEITO DE OPERADORES GA ===
                   Fitness Médio  Contagem  Desvio Padrão
selecao=1, cross=1, elitismo=1   -0.0524         50        0.0089
selecao=0, cross=1, elitismo=1   -0.0412         50        0.0134
selecao=1, cross=0, elitismo=1   -0.0389         50        0.0156
```

---

## Exemplo 5: Otimização Customizada {#exemplo5}

Exemplo avançado: otimizar apenas um fold com configuração customizada.

### Código Customizado

```python
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import Individuo, Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import time

def otimizar_fold_customizado(fold_num=1):
    """
    Otimiza apenas um fold com parâmetros customizados
    """
    
    # === CONFIGURAÇÃO CUSTOMIZADA ===
    n_arvores = 500              # Menos árvores = mais rápido
    n_geracoes = 50              # Mais gerações = melhor convergência
    n_individuos = 100           # Mais indivíduos = mais exploração
    selecao_torneio = 1          # 1=torneio, 0=roleta
    crossover_uniforme = 1       # 1=uniforme, 0=ponto
    elitismo = 1                 # 1=com elitismo
    
    # === SETUP ===
    rota_pasta = "../Colecoes/2003_td_dataset/"
    MASK = [1] * 64
    
    # Carrega dados
    name_train = f"{rota_pasta}Fold{fold_num}/Norm.train.txt"
    name_vali = f"{rota_pasta}Fold{fold_num}/Norm.vali.txt"
    name_test = f"{rota_pasta}Fold{fold_num}/Norm.test.txt"
    
    X, y, z = load_L2R_file(name_train, MASK)
    X2, y2, z2 = load_L2R_file(name_vali, MASK)
    X3, y3, z3 = load_L2R_file(name_test, MASK)
    
    # Cria estruturas
    Vetores_train = Consultas(X, y, z)
    Vetores_vali = Consultas(X2, y2, z2)
    Vetores_test = Consultas(X3, y3, z3)
    
    # === EXECUTA GA ===
    forest = Forest(n_estimators=n_arvores, n_jobs=4)
    forest.Fold = fold_num
    forest.n_estimators = n_arvores
    forest.size = n_arvores
    
    print(f"=== Otimizando Fold {fold_num} ===")
    print(f"Floresta: {n_arvores} árvores")
    print(f"GA: {n_geracoes} gerações, {n_individuos} indivíduos")
    print()
    
    start = time.time()
    
    # Executa GA principal
    melhor = forest.ga(
        [Vetores_train, Vetores_vali],
        max_num_geracoes=n_geracoes,
        n_treesForest=n_individuos,
        selecaoTorneio=selecao_torneio,
        crossoverUniforme=crossover_uniforme,
        elitist=elitismo,
        numero_genes=n_arvores,
        mode="tRisk"
    )
    
    # Avalia no conjunto de teste
    resultado = forest.fit_forest([melhor], Vetores_train, Vetores_test, mode="ndcg")
    individuo = resultado[0]
    
    tempo = time.time() - start
    
    # === RELATÓRIO ===
    n_trees_used = int(np.sum(individuo.get_fita()))
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Fitness (TRISK): {individuo.fitness:.6f}")
    print(f"MAP: {individuo.map:.4f}")
    print(f"Árvores usadas: {n_trees_used}/{n_arvores} ({100*n_trees_used/n_arvores:.1f}%)")
    print(f"Tempo: {tempo:.2f} segundos")
    print(f"Melhoria esperada: {abs(individuo.fitness)*100:.2f}%")
    
    return individuo

# Executa
if __name__ == '__main__':
    melhor_individuo = otimizar_fold_customizado(fold_num=1)
```

### Saída Esperada

```
=== Otimizando Fold 1 ===
Floresta: 500 árvores
GA: 50 gerações, 100 indivíduos

Processando...
Geração 1/50: Best=-0.0142
Geração 2/50: Best=-0.0189
...
Geração 50/50: Best=-0.0634

=== RESULTADO FINAL ===
Fitness (TRISK): -0.063421
MAP: 0.3654
Árvores usadas: 234/500 (46.8%)
Tempo: 287.43 segundos
Melhoria esperada: 6.34%
```

### Variações Possíveis

```python
# Variação 1: Apenas mutation (sem crossover)
# Descomentar em ga.py para testar convergência mais lenta

# Variação 2: Populações muito grandes para exploração
n_individuos = 200
n_geracoes = 20

# Variação 3: Muitas gerações com população pequena (intensivo)
n_individuos = 30
n_geracoes = 100

# Variação 4: Roleta + Ponto (convergência rápida)
selecao_torneio = 0
crossover_uniforme = 0
```

---

## Resumo de Exemplos

| Exemplo | Caso de Uso | Tempo Est. |
|---------|------------|-----------|
| 1 | Execução padrão (GA todos folds) | ~2-3 horas |
| 2 | Benchmark múltiplas configurações | ~10+ horas (paralelo) |
| 3 | Baseline sem GA (rápido) | ~30 minutos |
| 4 | Análise de resultados | Instantâneo |
| 5 | Otimização single-fold customizada | ~5-10 minutos |

---

## Dicas de Otimização

### Para Resultados Melhores:
1. Aumente `n_geracoes` (30→50)
2. Aumente `n_individuos` (75→150)
3. Use `selecao_torneio=1` (menos convergência prematura)
4. Use `elitismo=1` (preserva melhores)

### Para Execução Mais Rápida:
1. Diminua `n_arvores` (1000→500)
2. Diminua `n_geracoes` (30→10)
3. Diminua `n_individuos` (75→25)
4. Use `n_jobs=2` ao invés de 4

### Para Análise de Convergência:
Modifique `ga.py` para salvar melhor fitness a cada geração em arquivo separado

