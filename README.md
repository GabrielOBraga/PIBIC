# Aprendendo a Ranquear com Florestas Aleatórias e Algoritmos Genéticos (PIBIC)

![Badge em Desenvolvimento](http://img.shields.io/static/v1?label=STATUS&message=CONCLUÍDO&color=GREEN&style=for-the-badge)
![Badge Python](http://img.shields.io/static/v1?label=LINGUAGEM&message=PYTHON&color=blue&style=for-the-badge)
![Badge IFG](http://img.shields.io/static/v1?label=INSTITUIÇÃO&message=IFG%20ANÁPOLIS&color=red&style=for-the-badge)

## 📄 Sobre o Projeto

Este repositório contém os artefatos desenvolvidos durante o projeto de Iniciação Científica (PIBIC), vinculado ao **Instituto Federal de Goiás (IFG) - Câmpus Anápolis**.

O foco da pesquisa foi a aplicação de técnicas de **Learning to Rank (LtR)**, uma subárea do Aprendizado de Máquina voltada para a otimização de sistemas de recuperação de informação (como motores de busca). O trabalho explorou o uso de **Algoritmos Genéticos (AG)** para otimizar e selecionar atributos em modelos baseados em **Florestas Aleatórias (Random Forests)**, visando melhorar a precisão do ranqueamento.

### 🎯 Objetivos

* Investigar o desempenho de modelos de *Learning to Rank* baseados em árvores de decisão.
* Implementar e avaliar o uso de Algoritmos Genéticos para otimização de hiperparâmetros e seleção de características (feature selection).
* Comparar a eficiência da abordagem proposta com métodos tradicionais de ranqueamento.

## 📁 Estrutura do Repositório

A organização dos arquivos neste projeto segue a seguinte estrutura:

```
📦 PIBIC
 ┣ 📂 Apresentacao           # Slides, banners e materiais visuais do IX SIC
 ┣ 📂 BACKUPS                # Versões anteriores e arquivos históricos
 ┣ 📂 RF_SPEA2_WEB           # Random Forest com SPEA2 (multiobjective)
 │ ┣ 📄 DOCUMENTATION.md     # Documentação completa (3000+ linhas)
 │ ┣ 📄 QUICK_REFERENCE.md   # Guia rápido
 │ ┣ 📄 EXAMPLES.md          # Exemplos práticos
 │ ┗ 📂 Forest_GA/
 ┣ 📂 RF_TRISK               # ⭐ Random Forest com GA + TRISK (RECOMENDADO)
 │ ┣ 📄 DOCUMENTATION.md     # Documentação técnica (4000+ linhas)
 │ ┣ 📄 EXAMPLES.md          # 5 exemplos executáveis (2000+ linhas)
 │ ┣ 📄 INDEX.md             # Índice e navegação
 │ ┣ 📄 SUMMARY.md           # Sumário de documentação
 │ ┣ 📄 COMPLETION.md        # Checklist de conclusão
 │ ┣ 💻 __main__.py          # Código principal com 350+ comentários
 │ ┗ 📂 Forest_GA/
 │   ┣ 💻 forest_commented.py # Métodos explicados (480+ comentários)
 │   ┣ 💻 forest.py           # Classe Forest (RandomForest + GA)
 │   ┗ 📂 PIBIC/              # Algoritmo Genético e métricas
 ┗ 📜 README.md               # Este arquivo
```

> **Nota:** A pasta `Apresentacao` contém os materiais expositivos defendidos no IX Seminário de Iniciação Científica do IFG.
> **Recomendação:** Comece com **RF_TRISK** - contém 7000+ linhas de documentação profissional + exemplos executáveis.

## 🛠 Tecnologias Utilizadas

O projeto foi desenvolvido utilizando as seguintes ferramentas e bibliotecas:

* **Python 3.x:** Linguagem principal.
* **Scikit-Learn:** Para implementação de Random Forests e algoritmos de ML.
* **DEAP:** Framework para Algoritmos Genéticos (alternativa implementação interna).
* **NumPy & SciPy:** Computação numérica e otimização.
* **Joblib:** Paralelismo e cache de objetos grandes (árvores).
* **Pandas:** Manipulação e análise de dados.
* **Jupyter Notebook:** Ambiente de desenvolvimento e prototipagem (opcional).

## 🧬 Metodologia

A pesquisa combinou dois pilares da Inteligência Artificial:

1. **Random Forests (Florestas Aleatórias):** Utilizado como o regressor/classificador base para atribuir pontuações de relevância aos documentos.
2. **Algoritmos Genéticos:** Empregados como meta-heurística para buscar a melhor combinação de parâmetros e o subconjunto ideal de árvores que maximize métricas de avaliação de ranqueamento.

### Abordagens Implementadas

#### **RF_SPEA2_WEB** (Multiobjective - 6000+ linhas documentadas)
- **Algoritmo:** SPEA2 (Strength Pareto Evolutionary Algorithm 2)
- **Múltiplos Objetivos:** NDCG vs outras métricas simultaneamente
- **Dominância:** Análise de dominância Pareto para balancear objetivos
- **Seleção:** Seleção de features + subconjunto de árvores
- **Aplicação:** Quando múltiplas métricas são igualmente importantes

**Arquivos:**
- `RF_SPEA2_WEB/DOCUMENTATION.md` - Explicação SPEA2
- `RF_SPEA2_WEB/EXAMPLES.md` - Exemplos de uso
- `RF_SPEA2_WEB/QUICK_REFERENCE.md` - Referência rápida

#### **RF_TRISK** (Single-Objective - 7000+ linhas documentadas) ⭐
- **Algoritmo:** Algoritmo Genético (GA) clássico com elitismo
- **Objetivo Único:** Maximizar TRISK (minimizar degradação vs baseline)
- **Operadores GA:**
  - **Seleção:** Torneio (Tournament) vs Roleta (Roulette Wheel)
  - **Crossover:** Uniforme vs Ponto único
  - **Mutação:** Flip de genes com probabilidade configurável
  - **Elitismo:** Preservação automática dos melhores indivíduos
- **Validação:** 5-fold cross-validation
- **Cache:** Pickle para reutilização eficiente de árvores treinadas
- **Paralelismo:** Joblib para fitness evaluation paralela
- **Aplicação:** Otimização rápida e com foco em uma métrica específica

**Arquivos:**
- `RF_TRISK/DOCUMENTATION.md` - Documentação técnica completa
- `RF_TRISK/EXAMPLES.md` - 5 exemplos executáveis
- `RF_TRISK/__main__.py` - Código principal comentado
- `RF_TRISK/Forest_GA/forest_commented.py` - Implementação GA detalhada

---

## 📊 Comparação: RF_SPEA2_WEB vs RF_TRISK

| Característica | RF_SPEA2_WEB | RF_TRISK |
|---|---|---|
| **Algoritmo** | SPEA2 (Multiobjective) | GA Single-Objective |
| **Métrica Primária** | NDCG + Pareto | TRISK (Trade-off Risk) |
| **Modo de Avaliação** | Múltiplos objetivos | Um objetivo |
| **Fitness** | Dominância Pareto | TRISK = (base - otim) / 5 |
| **Operadores GA** | Seleção, Crossover, Mutação | Seleção, Crossover, Mutação, Elitismo |
| **Paralelismo** | Padrão Python | Joblib para fitness |
| **Cache de Árvores** | Não | Sim (Pickle) |
| **Validação** | 5-fold | 5-fold |
| **Tempo de Execução** | Maior (múltiplos objetivos) | Menor (objetivo único) |
| **Documentação** | 6 arquivos (6000+ linhas) | 5 arquivos + comentários (7000+ linhas) |
| **Recomendação** | Pesquisa avançada | Começar aqui! |

---

### Instalação de Dependências

```bash
pip install numpy scipy scikit-learn joblib
```

### Executar RF_TRISK (Recomendado para Começar)

```bash
cd RF_TRISK
python __main__.py
```

**Resultado:** Arquivos CSV em `FinalResultados/TheBests_1000.csv`

### Documentação e Exemplos

Cada projeto contém documentação completa:

- **Iniciante:** Leia `RF_TRISK/EXAMPLES.md` (Exemplo 1)
- **Desenvolvedor:** Leia `RF_TRISK/__main__.py` comentado + `DOCUMENTATION.md`
- **Pesquisador:** Leia `RF_TRISK/DOCUMENTATION.md` completo

### Arquivos Principais

| Arquivo | Descrição | Linhas |
|---------|-----------|--------|
| `RF_TRISK/__main__.py` | Entrada + folds + GA | 270 comentadas |
| `RF_TRISK/Forest_GA/forest.py` | Random Forest + cache | 387 (480 comentadas) |
| `RF_TRISK/Forest_GA/PIBIC/ga.py` | Algoritmo Genético | 374 |
| `RF_TRISK/DOCUMENTATION.md` | Manual técnico | 4000+ |
| `RF_TRISK/EXAMPLES.md` | 5 exemplos práticos | 2000+ |
## ✨ Features Principais

### RF_SPEA2_WEB
- ✅ Otimização SPEA2 (multiobjective)
- ✅ Análise de dominância Pareto
- ✅ Múltiplas métricas simultâneas
- ✅ Seleção de features + árvores
- ✅ Documentação extensiva (6 arquivos)

### RF_TRISK
- ✅ Algoritmo Genético otimizado
- ✅ Métrica TRISK (trade-off risk)
- ✅ 5-fold cross-validation
- ✅ Cache de árvores em pickle (eficiência)
- ✅ Paralelismo com joblib
- ✅ 7000+ linhas de documentação
- ✅ 350+ linhas de código comentado
- ✅ 5 exemplos práticos executáveis

### Operadores GA Implementados
- **Seleção:** Torneio vs Roleta
- **Crossover:** Uniforme vs Ponto
- **Mutação:** Flip de genes
- **Elitismo:** Preservação dos melhores
- **Avaliação:** Fitness em paralelo

---

## 🎓 Métricas Explicadas

O projeto utiliza três métricas padrão de Learning-to-Rank:

### NDCG (Normalized Discounted Cumulative Gain)
- **Propósito:** Mede qualidade do ranking ponderando posições
- **Range:** [0, 1] - quanto maior, melhor
- **Cálculo:** Pondera documentos relevantes pela posição (penaliza resultados ruins em posições altas)
- **Uso:** Métrica base em ambos RF_SPEA2_WEB e RF_TRISK

### MAP (Mean Average Precision)
- **Propósito:** Média de precisão em top-k resultados
- **Range:** [0, 1] - quanto maior, melhor
- **Cálculo:** Média de precisão em cada posição relevante
- **Uso:** Métrica secundária em RF_SPEA2_WEB

### TRISK (Trade-off Risk) - Exclusivo RF_TRISK
- **Propósito:** Mede degradação de performance vs baseline
- **Fórmula:** `TRISK = Σ(base_ndcg - otimizado_ndcg) / n_folds`
- **Range:** [-∞, +∞] - **negativo é melhor** (melhoria de performance)
- **Exemplo:** 
  - Se base NDCG = 0.8 e otimizado = 0.85, TRISK = -0.05 (5% melhoria)
  - Se base NDCG = 0.8 e otimizado = 0.75, TRISK = +0.05 (5% piora)
- **Uso:** Métrica primária em RF_TRISK (foco principal)

---
## � Documentação Disponível

### ⭐ RF_TRISK (RECOMENDADO - 7000+ linhas de documentação)

**Arquivos Principais:**

1. **[DOCUMENTATION.md](RF_TRISK/DOCUMENTATION.md)** - Manual Técnico (~4000 linhas)
   - Visão geral do projeto e características
   - Diferenças com RF_SPEA2 (tabela comparativa)
   - Estrutura de diretórios anotada
   - Componentes principais com pseudo-código
   - Guia de configuração (todos parâmetros explicados)
   - Guia de execução (4 cenários diferentes)
   - Métricas e avaliação (NDCG, MAP, TRISK detalhado)
   - Fluxo de processamento (diagramas)
   - Troubleshooting e problemas comuns

2. **[EXAMPLES.md](RF_TRISK/EXAMPLES.md)** - 5 Exemplos Executáveis (~2000 linhas)
   - Exemplo 1: Execução completa padrão (GA todos 5 folds)
   - Exemplo 2: Ajuste de parâmetros GA (teste múltiplas configurações)
   - Exemplo 3: Teste individual sem GA (baseline RandomForest)
   - Exemplo 4: Leitura e análise de resultados (script Python)
   - Exemplo 5: Otimização customizada single-fold (código avançado)
   - Dicas de otimização (performance vs qualidade)

3. **[INDEX.md](RF_TRISK/INDEX.md)** - Índice de Navegação
   - Links rápidos para todas seções
   - Mapa de componentes

4. **[SUMMARY.md](RF_TRISK/SUMMARY.md)** - Sumário Executivo
   - Checklist de documentação
   - Estatísticas de linhas de código

5. **Código Comentado:**
   - **[__main__.py](RF_TRISK/__main__.py)** - 350+ linhas comentadas
     - Imports explicados
     - Função `folds_works()` documentada
     - Função `imprimir_individuo()` com docstrings
   - **[forest_commented.py](RF_TRISK/Forest_GA/forest_commented.py)** - 480+ linhas comentadas
     - Classe Forest completamente anotada
     - Métodos: `fit_forest()`, `ga()`, `get_Trees()`, `fitLoadTrees()`, `fit()`

### RF_SPEA2_WEB (Multiobjective - 6000+ linhas de documentação)

- **[DOCUMENTATION.md](RF_SPEA2_WEB/DOCUMENTATION.md)** - Manual SPEA2
- **[EXAMPLES.md](RF_SPEA2_WEB/EXAMPLES.md)** - Exemplos
- **[QUICK_REFERENCE.md](RF_SPEA2_WEB/QUICK_REFERENCE.md)** - Guia rápido

---

## �👨‍💻 Autor e Orientação
```
Pesquisador:
Gabriel Oliveira Braga - https://github.com/GabrielOBraga
Bacharelado em Ciência da Computação - IFG Anápolis
Orientador:
Prof. Dr. Daniel Xavier de Sousa
```
Este projeto foi financiado pelo Programa Institucional de Bolsas de Iniciação Científica (PIBIC/CNPq).
