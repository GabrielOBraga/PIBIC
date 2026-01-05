# Exemplos Práticos - RF_SPEA2_WEB

## Exemplo 1: Executar GA Simples (Um Fold)

```python
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import Individuo, Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import numpy as np

# Configuração
MASK = [1] * 136  # Web10k: 136 features

# Carregar dados
print("Carregando dados...")
X_train, y_train, q_train = load_L2R_file("../Colecoes/web10k/Fold1/Norm.train.txt", MASK)
X_vali, y_vali, q_vali = load_L2R_file("../Colecoes/web10k/Fold1/Norm.vali.txt", MASK)
X_test, y_test, q_test = load_L2R_file("../Colecoes/web10k/Fold1/Norm.test.txt", MASK)

# Encapsular em Consultas
Vet_train = Consultas(X_train, y_train, q_train)
Vet_vali = Consultas(X_vali, y_vali, q_vali)
Vet_test = Consultas(X_test, y_test, q_test)

# Criar Forest
print("Criando Random Forest...")
forest = Forest(n_estimators=1000, n_jobs=4)
forest.Fold = 1
forest.size = 1000

# Executar GA
print("Executando Algoritmo Genético (30 gerações)...")
melhor_individuo = forest.ga(
    [Vet_train, Vet_vali],
    max_num_geracoes=30,
    n_treesForest=75,
    selecaoTorneio=1,
    crossoverUniforme=1,
    elitist=1,
    numero_genes=1000,
    mode="spea2"
)

# Avaliar no conjunto de teste
resultado = forest.fit_forest([melhor_individuo], Vet_train, Vet_test, mode="ndcg")

# Mostrar resultados
print(f"\n=== RESULTADOS ===")
print(f"NDCG Final: {resultado[0].fitnessNDCG:.4f}")
print(f"TRISK: {resultado[0].fitnessTrisk:.4f}")
print(f"Árvores selecionadas: {int(sum(melhor_individuo.mascara))} / 1000")
print(f"Redução: {(1 - sum(melhor_individuo.mascara) / 1000) * 100:.1f}%")
```

---

## Exemplo 2: Comparar Diferentes Configurações de GA

```python
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import numpy as np

MASK = [1] * 136

# Carregar dados (usar Fold1 para este exemplo)
X_train, y_train, q_train = load_L2R_file("../Colecoes/web10k/Fold1/Norm.train.txt", MASK)
X_vali, y_vali, q_vali = load_L2R_file("../Colecoes/web10k/Fold1/Norm.vali.txt", MASK)
X_test, y_test, q_test = load_L2R_file("../Colecoes/web10k/Fold1/Norm.test.txt", MASK)

Vet_train = Consultas(X_train, y_train, q_train)
Vet_vali = Consultas(X_vali, y_vali, q_vali)
Vet_test = Consultas(X_test, y_test, q_test)

# Configurações a testar
configs = [
    {"selecao": 1, "crossover": 1, "nome": "Torneio + Uniforme"},
    {"selecao": 1, "crossover": 0, "nome": "Torneio + Um Ponto"},
    {"selecao": 0, "crossover": 1, "nome": "Roleta + Uniforme"},
    {"selecao": 0, "crossover": 0, "nome": "Roleta + Um Ponto"},
]

resultados = []

for cfg in configs:
    print(f"\nTestando: {cfg['nome']}")
    
    forest = Forest(n_estimators=1000, n_jobs=4)
    forest.Fold = 1
    forest.size = 1000
    
    melhor = forest.ga(
        [Vet_train, Vet_vali],
        max_num_geracoes=30,
        n_treesForest=75,
        selecaoTorneio=cfg["selecao"],
        crossoverUniforme=cfg["crossover"],
        elitist=1,
        numero_genes=1000,
        mode="spea2"
    )
    
    resultado = forest.fit_forest([melhor], Vet_train, Vet_test, mode="ndcg")
    
    resultados.append({
        "config": cfg["nome"],
        "ndcg": resultado[0].fitnessNDCG,
        "trisk": resultado[0].fitnessTrisk,
        "arvores": int(sum(melhor.mascara))
    })
    
    print(f"  NDCG: {resultado[0].fitnessNDCG:.4f} | TRISK: {resultado[0].fitnessTrisk:.4f}")

# Mostrar resumo
print("\n=== RESUMO COMPARATIVO ===")
for r in resultados:
    print(f"{r['config']:25} | NDCG: {r['ndcg']:.4f} | TRISK: {r['trisk']:.4f}")
```

---

## Exemplo 3: Executar GA para Todos os 5 Folds

```python
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import numpy as np

MASK = [1] * 136
resultados_por_fold = []

for fold in range(1, 6):
    print(f"\n{'='*50}")
    print(f"PROCESSANDO FOLD {fold}")
    print('='*50)
    
    # Carregar dados
    train_file = f"../Colecoes/web10k/Fold{fold}/Norm.train.txt"
    vali_file = f"../Colecoes/web10k/Fold{fold}/Norm.vali.txt"
    test_file = f"../Colecoes/web10k/Fold{fold}/Norm.test.txt"
    
    try:
        X_train, y_train, q_train = load_L2R_file(train_file, MASK)
        X_vali, y_vali, q_vali = load_L2R_file(vali_file, MASK)
        X_test, y_test, q_test = load_L2R_file(test_file, MASK)
    except FileNotFoundError:
        print(f"Arquivos não encontrados para Fold{fold}")
        continue
    
    Vet_train = Consultas(X_train, y_train, q_train)
    Vet_vali = Consultas(X_vali, y_vali, q_vali)
    Vet_test = Consultas(X_test, y_test, q_test)
    
    # GA
    forest = Forest(n_estimators=1000, n_jobs=4)
    forest.Fold = fold
    forest.size = 1000
    
    melhor = forest.ga(
        [Vet_train, Vet_vali],
        max_num_geracoes=30,
        n_treesForest=75,
        selecaoTorneio=1,
        crossoverUniforme=1,
        elitist=1,
        numero_genes=1000,
        mode="spea2"
    )
    
    resultado = forest.fit_forest([melhor], Vet_train, Vet_test, mode="ndcg")
    
    resultados_por_fold.append({
        "fold": fold,
        "ndcg": resultado[0].fitnessNDCG,
        "trisk": resultado[0].fitnessTrisk,
        "arvores": int(sum(melhor.mascara))
    })
    
    print(f"Fold {fold}: NDCG={resultado[0].fitnessNDCG:.4f}, TRISK={resultado[0].fitnessTrisk:.4f}")

# Estatísticas
print(f"\n{'='*50}")
print("RESULTADOS FINAIS (Todos os Folds)")
print('='*50)

ndcgs = [r["ndcg"] for r in resultados_por_fold]
trisks = [r["trisk"] for r in resultados_por_fold]

print(f"NDCG Médio: {np.mean(ndcgs):.4f} ± {np.std(ndcgs):.4f}")
print(f"TRISK Médio: {np.mean(trisks):.4f} ± {np.std(trisks):.4f}")
print(f"Árvores Médio: {np.mean([r['arvores'] for r in resultados_por_fold]):.0f}")

for r in resultados_por_fold:
    print(f"Fold {r['fold']}: NDCG={r['ndcg']:.4f} | TRISK={r['trisk']:.4f} | Árvores={r['arvores']}")
```

---

## Exemplo 4: Testar Sem GA (Random Forest Padrão)

```python
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import Individuo, Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import numpy as np

MASK = [1] * 136

# Carregar dados
X_train, y_train, q_train = load_L2R_file("../Colecoes/web10k/Fold1/Norm.train.txt", MASK)
X_vali, y_vali, q_vali = load_L2R_file("../Colecoes/web10k/Fold1/Norm.vali.txt", MASK)
X_test, y_test, q_test = load_L2R_file("../Colecoes/web10k/Fold1/Norm.test.txt", MASK)

Vet_train = Consultas(X_train, y_train, q_train)
Vet_vali = Consultas(X_vali, y_vali, q_vali)
Vet_test = Consultas(X_test, y_test, q_test)

# Forest padrão (TODAS as 1000 árvores)
forest = Forest(n_estimators=1000, n_jobs=4)
forest.Fold = 1
forest.size = 1000

# Indivíduo com todas as árvores (all-ones)
mascara_baseline = np.ones(1000)
ind_baseline = Individuo(mascara_baseline, 1)

# Avaliar
print("Avaliando RF padrão (1000 árvores)...")
resultado = forest.fit_forest([ind_baseline], Vet_train, Vet_test, mode="ndcg")

print(f"\n=== BASELINE ===")
print(f"NDCG: {resultado[0].fitnessNDCG:.4f}")
print(f"TRISK: {resultado[0].fitnessTrisk:.4f}")
print(f"Árvores: 1000 / 1000 (100%)")
```

---

## Exemplo 5: Analisar Resultados Salvos

```python
import pandas as pd
import numpy as np
import os

# Ler arquivo de resultados finais
resultado_file = "FinalResultados/TheBests_1000.csv"

if os.path.exists(resultado_file):
    df = pd.read_csv(resultado_file, sep=';')
    
    print("=== ANÁLISE DE RESULTADOS ===\n")
    
    # Converter colunas de interesse
    df['ndcg_vals'] = df['ndcg_vals'].apply(lambda x: float(x.split('[')[1].split(',')[0]) if '[' in str(x) else 0)
    
    # Agrupar por fold
    for fold in df['fold'].unique():
        fold_data = df[df['fold'] == fold]
        print(f"Fold {fold}:")
        print(f"  NDCG: {fold_data['ndcg'].mean():.4f}")
        print(f"  TRISK: {fold_data['map'].mean():.4f}")
        print(f"  Árvores médio: {fold_data['n arvores'].mean():.0f}")
        print()
else:
    print("Arquivo de resultados não encontrado")

# Análise por geração
gen_file = "N_1000/Fold_1/G_30Ind_75GA_1111_store.csv"

if os.path.exists(gen_file):
    df_gen = pd.read_csv(gen_file, sep=';')
    print(f"\n=== EVOLUÇÃO GENÉTICA ===")
    print(f"Gerações processadas: {df_gen.shape[0]}")
    print(f"Última geração NDCG: {df_gen.iloc[-1, 1]:.4f}")
else:
    print("Arquivo de gerações não encontrado")
```

---

## Exemplo 6: Customizar Probabilidades do GA

```python
from Forest_GA.forest import Forest
from Forest_GA.PIBIC.ga import GeneticAlgorithm, Consultas
from Forest_GA.PIBIC.h_l2rMiscellaneous import load_L2R_file
import numpy as np

MASK = [1] * 136

# Carregar dados
X_train, y_train, q_train = load_L2R_file("../Colecoes/web10k/Fold1/Norm.train.txt", MASK)
X_vali, y_vali, q_vali = load_L2R_file("../Colecoes/web10k/Fold1/Norm.vali.txt", MASK)
X_test, y_test, q_test = load_L2R_file("../Colecoes/web10k/Fold1/Norm.test.txt", MASK)

Vet_train = Consultas(X_train, y_train, q_train)
Vet_vali = Consultas(X_vali, y_vali, q_vali)
Vet_test = Consultas(X_test, y_test, q_test)

forest = Forest(n_estimators=1000, n_jobs=4)
forest.Fold = 1
forest.size = 1000

# GA com probabilidades customizadas
GA = GeneticAlgorithm([], 1)
GA.tamanho_populacao = 100        # Aumentar população
GA.num_caracteristicas = 1000
GA.probabilidade = 0.7            # Maior prob. de crossover
GA.probabilidadeMutacao = 0.5     # Maior prob. de mutação
GA.elitist = 1
GA.bool_selecaoTorneio_Roleta = 1
GA.bool_crossoverUniforme_Ponto = 1

# Gerar população inicial
print("Gerando população inicial...")
geracao = GA.GenerateInicial()
geracao_com_fit = forest.fit_forest(geracao, Vet_train, Vet_vali, mode="spea2")

# Evoluir manualmente
for gen in range(1, 31):
    print(f"Geração {gen}/30")
    geracao_nova = GA.GA(geracao_com_fit, gen+1, "spea2")
    geracao_com_fit = forest.fit_forest(geracao_nova, Vet_train, Vet_vali, mode="spea2")
    
    # Elitismo manual
    geracao_com_fit = GA.ElitistGroup(geracao_com_fit, geracao_com_fit)

# Melhor indivíduo
melhor = max(geracao_com_fit, key=lambda x: x.fitnessSpea2)
print(f"\nFitness final: {melhor.fitnessSpea2:.4f}")
```

---

## Exemplo 7: Visualizar Evolução do GA

```python
import matplotlib.pyplot as plt
import numpy as np

# Simular dados de evolução (em prática, viria do PrintExcelGA)
geracoes = np.arange(1, 31)
ndcg_por_gen = [0.340 + 0.020 * np.log(g) for g in geracoes]
trisk_por_gen = [0.250 - 0.005 * np.log(g) for g in geracoes]

# Plotar
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# NDCG
ax1.plot(geracoes, ndcg_por_gen, 'b-o', linewidth=2, markersize=4)
ax1.set_xlabel('Geração')
ax1.set_ylabel('NDCG')
ax1.set_title('Evolução NDCG')
ax1.grid(True, alpha=0.3)

# TRISK
ax2.plot(geracoes, trisk_por_gen, 'r-o', linewidth=2, markersize=4)
ax2.set_xlabel('Geração')
ax2.set_ylabel('TRISK')
ax2.set_title('Evolução TRISK')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('evolucao_ga.png', dpi=100)
print("Gráfico salvo em: evolucao_ga.png")
```

---

## Notas Importantes

⚠️ **Antes de executar:**
1. Verificar que arquivos de dados existem nos caminhos corretos
2. Ter espaço em disco suficiente (~500MB para cache de árvores)
3. Processos podem levar várias horas (30 gerações × 5 folds)

💡 **Tips:**
- Usar `n_jobs=-1` para máximo paralelismo
- Salvar estado intermediário (PrintExcelGA faz isso)
- Começar com `max_num_geracoes=5` para debug
- Aumentar `tamanho_populacao` para melhor exploração

📊 **Benchmarks Esperados:**
- Web10k: NDCG ~0.36-0.38, TRISK ~0.18-0.25
- Redução de árvores: 30-50% comum
- Tempo por fold: 2-4 horas (1000 árvores)

---

**Última atualização**: 2024 | **Versão**: 1.0
