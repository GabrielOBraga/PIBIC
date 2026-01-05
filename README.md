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
 ┣ 📂 Apresentacao   # Slides, banners e materiais visuais utilizados no IX SIC e eventos.
 ┣ 📂 BACKUPS        # Versões anteriores de código, scripts de teste e logs de execução.
 ┗ 📜 README.md      # Documentação do projeto.
```


> **Nota:** A pasta `Apresentacao` contém os materiais expositivos defendidos no IX Seminário de Iniciação Científica do IFG.

## 🛠 Tecnologias Utilizadas

O projeto foi desenvolvido utilizando as seguintes ferramentas e bibliotecas:

* **Python 3.x:** Linguagem principal.
* **Scikit-Learn:** Para implementação de algoritmos de Machine Learning (Random Forests).
* **DEAP (Distributed Evolutionary Algorithms in Python):** Framework para implementação dos Algoritmos Genéticos.
* **NumPy & Pandas:** Manipulação e análise de dados.
* **Jupyter Notebook:** Ambiente de desenvolvimento e prototipagem.

## 🧬 Metodologia

A pesquisa combinou dois pilares da Inteligência Artificial:

1. **Random Forests (Florestas Aleatórias):** Utilizado como o regressor/classificador base para atribuir pontuações de relevância aos documentos.
2. **Algoritmos Genéticos:** Empregados como meta-heurística para buscar a melhor combinação de parâmetros da floresta e/ou o subconjunto ideal de atributos que maximizasse métricas de avaliação de ranqueamento (como NDCG ou MAP).

## 🚀 Como Executar

Para rodar os experimentos contidos nos backups ou scripts principais:

### 1. **Clone o repositório:**
```
   bash
   git clone [https://github.com/GabrielOBraga/PIBIC.git](https://github.com/GabrielOBraga/PIBIC.git)
   cd PIBIC
```

### 2. Instale as dependências:
```
Bash
pip install numpy pandas scikit-learn deap jupyter
```

### 3. Execute os notebooks:

Navegue até a pasta onde estão os scripts (provavelmente em BACKUPS se não houver pasta src na raiz) e inicie o Jupyter:
```
Bash
jupyter notebook
```

## 👨‍💻 Autor e Orientação
```
Pesquisador:
Gabriel Oliveira Braga - https://github.com/GabrielOBraga
Bacharelado em Ciência da Computação - IFG Anápolis
Orientador:
Prof. Dr. Daniel Xavier de Sousa
```
Este projeto foi financiado pelo Programa Institucional de Bolsas de Iniciação Científica (PIBIC/CNPq).
