# 📚 Mapa de Documentação - RF_SPEA2_WEB

## 🎯 Você está procurando por...?

### "Quero entender O QUÊ é este projeto"
```
→ DOCUMENTATION.md
  ├─ Seção: Visão Geral
  ├─ Seção: Estrutura do Projeto
  └─ Seção: Componentes Principais
```

### "Quero COMEÇAR RAPIDAMENTE"
```
→ QUICK_REFERENCE.md
  ├─ Seção: Fluxo de Execução em 5 Passos
  ├─ Seção: Exemplos Básicos
  └─ EXAMPLES.md
     └─ Exemplo 1: GA Simples
```

### "Quero CÓDIGO FUNCIONANDO AGORA"
```
→ EXAMPLES.md
  ├─ Exemplo 1: GA Simples (um fold)
  ├─ Exemplo 3: Todos os 5 folds
  └─ Exemplo 2: Comparar configurações
```

### "Preciso CUSTOMIZAR o comportamento"
```
→ EXAMPLES.md
  ├─ Exemplo 6: Customizar probabilidades
  └─ DOCUMENTATION.md
     └─ Seção: Configurações e Parâmetros
```

### "Não entendo as MÉTRICAS (NDCG, TRISK, SPEA2)"
```
→ QUICK_REFERENCE.md
  └─ Seção: Métricas Explicadas
```

### "Como INTERPRETAR os RESULTADOS?"
```
→ QUICK_REFERENCE.md
  ├─ Seção: Interpretando Resultados
  └─ EXAMPLES.md
     └─ Exemplo 5: Analisar Resultados Salvos
```

### "Algo DEU ERRO, o que fazer?"
```
→ QUICK_REFERENCE.md
  └─ Seção: Problemas Comuns & Soluções
      ou
→ DOCUMENTATION.md
  └─ Seção: Troubleshooting
```

### "Quero ENTENDER o algoritmo GENÉTICO"
```
→ DOCUMENTATION.md
  ├─ Seção: Fluxo de Execução
  ├─ Seção: Componentes Principais (GA)
  └─ Seção: Módulos Detalhados (ga.py)
      ou
→ QUICK_REFERENCE.md
  ├─ Seção: Estrutura de Classes
  └─ Seção: Tipos de Seleção/Crossover/Mutação
      ou
→ ga.py (arquivo comentado)
```

### "Como funcionam os OPERADORES GENÉTICOS?"
```
→ QUICK_REFERENCE.md
  ├─ Tabela: Tipos de Seleção
  ├─ Tabela: Tipos de Crossover
  └─ Tabela: Tipos de Mutação
      ou
→ DOCUMENTATION.md
  └─ Seção: Módulos Detalhados / GeneticAlgorithm
      ou
→ ga.py (Métodos Selecao, Crossover, Mutacao)
```

### "Preciso CLONAR e MODIFICAR o código"
```
→ forest.py (código comentado)
  ├─ Leia docstring da classe Forest
  ├─ Entenda método fit_forest
  └─ Estude método ga
      ou
→ ga.py (código comentado)
  ├─ Leia GeneticAlgorithm
  ├─ Estude cada operador
  └─ Veja Arquive (histórico)
```

### "Qual é o FLUXO COMPLETO de execução?"
```
→ DOCUMENTATION.md
  ├─ Seção: Fluxo de Execução (overview)
  ├─ Seção: Fluxo Detalhado da Função fit_forest()
  └─ Seção: Fluxo Detalhado de Execução (SPEA2)
      ou
→ EXAMPLES.md
  └─ "Pipeline Completo (Exemplo)"
```

### "Quero VER EXEMPLOS DE CÓDIGO"
```
→ EXAMPLES.md
  ├─ Exemplo 1: GA Simples
  ├─ Exemplo 2: Comparar Configurações
  ├─ Exemplo 3: Todos os Folds
  ├─ Exemplo 4: Baseline (sem GA)
  ├─ Exemplo 5: Analisar Resultados
  ├─ Exemplo 6: Customizar Probabilidades
  └─ Exemplo 7: Visualizar Evolução
```

### "Como SALVAR E CARREGAR ÁRVORES?"
```
→ DOCUMENTATION.md
  └─ Seção: Módulos Detalhados / forest.py
     ├─ Método: get_Trees()
     └─ Método: fitLoadTrees()
      ou
→ forest.py (método get_Trees - comentado)
```

### "Preciso PARALELIZAR o processamento"
```
→ EXAMPLES.md
  └─ Exemplo 3: Executar para Todos os Folds
      ou
→ __main__.py
  └─ Seção: executar_threads = 1
      ou
→ QUICK_REFERENCE.md
  └─ Seção: Problemas Comuns (Muito lento)
```

### "Quero COMPARAR diferentes CONFIGURAÇÕES de GA"
```
→ EXAMPLES.md
  └─ Exemplo 2: Comparar Diferentes Configurações
      ou
→ QUICK_REFERENCE.md
  └─ Tabela: Configurações Padrão vs Recomendadas
```

### "Como USAR com meus PRÓPRIOS DADOS?"
```
→ DOCUMENTATION.md
  └─ Seção: Módulos Detalhados / h_l2rMiscellaneous.py
     └─ Função: load_L2R_file()
      ou
→ EXAMPLES.md
  └─ Exemplo 1/2/3 (ver como carregam dados)
```

### "Qual é o FORMATO esperado dos DADOS?"
```
→ DOCUMENTATION.md
  ├─ Seção: Módulos Detalhados / h_l2rMiscellaneous.py
  │  └─ Função load_L2R_file() - "Formato de Entrada"
  └─ Seção: Configurações e Parâmetros / Datasets Suportados
```

### "Como INTERPRETAR a MÁSCARA binária?"
```
→ QUICK_REFERENCE.md
  └─ Seção: Interpretando Resultados
     └─ "Máscara Binária"
      ou
→ DOCUMENTATION.md
  └─ Seção: Saídas Esperadas / Interpretar Resultados
     └─ "Máscara Binária"
```

### "Qual é a REDUÇÃO ESPERADA de árvores?"
```
→ QUICK_REFERENCE.md
  └─ Seção: Interpretando Resultados / Ganho Esperado
      ou
→ DOCUMENTATION.md
  └─ Seção: Interpretação de Resultados / Ganho Esperado
```

### "Preciso ENTENDER a OTIMIZAÇÃO MULTOBJETIVO"
```
→ DOCUMENTATION.md
  ├─ Seção: Componentes Principais (SPEA2)
  ├─ Seção: Módulos Detalhados / h_functionsFilter.py
  └─ Seção: Notas Técnicas / "Algoritmo SPEA2 vs NDCG/TRISK"
      ou
→ QUICK_REFERENCE.md
  └─ "Tipos de Seleção" / Exemplo SPEA2
```

---

## 📂 Estrutura de Arquivos de Documentação

```
RF_SPEA2_WEB/
│
├── 📄 README.md ⭐
│   └─ Visão geral, índice, como usar documentação
│
├── 📖 DOCUMENTATION.md (3000+ linhas) ⭐⭐⭐
│   ├─ Visão Geral
│   ├─ Estrutura do Projeto
│   ├─ Componentes Principais
│   ├─ Fluxo de Execução
│   ├─ Módulos Detalhados (8 módulos/classes)
│   ├─ Configurações e Parâmetros
│   ├─ Exemplos de Uso
│   ├─ Fluxo Detalhado (SPEA2)
│   ├─ Saídas Esperadas
│   ├─ Interpretação de Resultados
│   ├─ Troubleshooting
│   └─ Notas Técnicas
│
├── 🚀 QUICK_REFERENCE.md (600+ linhas) ⭐⭐
│   ├─ Fluxo em 5 Passos
│   ├─ Estrutura de Classes
│   ├─ Métricas Explicadas
│   ├─ Tipos de Operadores (tabelas)
│   ├─ Interpretando Resultados
│   ├─ Problemas Comuns
│   ├─ Callbacks Avançados
│   └─ Configurações Recomendadas
│
├── 💻 EXAMPLES.md (400+ linhas) ⭐⭐
│   ├─ Exemplo 1: GA Simples
│   ├─ Exemplo 2: Comparar Configurações
│   ├─ Exemplo 3: Todos os Folds
│   ├─ Exemplo 4: Baseline (sem GA)
│   ├─ Exemplo 5: Analisar Resultados
│   ├─ Exemplo 6: Customizar Probabilidades
│   └─ Exemplo 7: Visualizar com Matplotlib
│
├── 🗺️ MAPS.md (este arquivo) ⭐
│   └─ Mapa de navegação da documentação
│
└── Código Comentado:
    ├── forest.py ⭐
    │   ├─ Classe Forest (comentada)
    │   ├─ fit_forest() (comentado)
    │   ├─ ga() (comentado)
    │   └─ get_Trees() (comentado)
    │
    └── ga.py ⭐
        ├─ Classe GeneticAlgorithm (comentada)
        ├─ GA() (comentado)
        ├─ GenerateInicial() (comentado)
        ├─ Selecao() (comentado)
        ├─ Crossover() (comentado)
        ├─ Mutacao() (comentado)
        ├─ ElitistGroup() (comentado)
        └─ Classe Arquive (comentada)
```

---

## ⭐ Importância dos Arquivos

| Arquivo | Importância | Tempo | Para Quem? |
|---------|-----------|-------|-----------|
| README.md | ⭐ | 5 min | Todos (começa aqui!) |
| DOCUMENTATION.md | ⭐⭐⭐ | 45 min | Desenvolvedores, pesquisadores |
| QUICK_REFERENCE.md | ⭐⭐ | 15 min | Usuários, estudantes |
| EXAMPLES.md | ⭐⭐ | 30 min | Iniciantes, prototipagem |
| MAPS.md | ⭐ | 5 min | Navegação (você está aqui!) |

---

## 🎯 Jornada de Aprendizado Recomendada

### Dia 1 - Entendimento (2 horas)
```
1. Ler README.md (5 min) - Visão geral
2. Ler QUICK_REFERENCE.md (15 min) - Conceitos principais
3. Ler DOCUMENTATION.md / "Visão Geral" (10 min)
4. Ler DOCUMENTATION.md / "Fluxo de Execução" (15 min)
5. Ler DOCUMENTATION.md / "Componentes Principais" (20 min)
6. Ver EXAMPLES.md / Exemplo 1 (10 min)
```

### Dia 2 - Prática (3 horas)
```
1. Rodar EXAMPLES.md / Exemplo 1 (30 min - execução + resultado)
2. Modificar Exemplo 1 (30 min)
3. Rodar EXAMPLES.md / Exemplo 2 (1 hora)
4. Entender resultados com QUICK_REFERENCE.md (30 min)
5. Ler código comentado em forest.py (30 min)
```

### Dia 3 - Profundidade (3 horas)
```
1. Ler DOCUMENTATION.md / "Módulos Detalhados" (1 hora)
2. Ler código comentado em ga.py (1 hora)
3. Rodar EXAMPLES.md / Exemplo 3 (executar apenas)
4. Rodar EXAMPLES.md / Exemplo 6 (customizar)
5. Ler DOCUMENTATION.md / "Troubleshooting" (30 min)
```

---

## 🔄 Ciclo de Resolução de Problemas

```
Problema?
│
├─ Já sabe o assunto?
│  ├─ Não → Ir para QUICK_REFERENCE.md
│  └─ Sim → Continuar
│
├─ Precisa de código?
│  ├─ Sim → EXAMPLES.md
│  └─ Não → Continuar
│
├─ Resposta encontrada em QUICK_REFERENCE?
│  ├─ Sim → ✓ Problema resolvido
│  └─ Não → Ir para DOCUMENTATION.md
│
├─ Procure em DOCUMENTATION por:
│  ├─ Seção relevante
│  ├─ Use Ctrl+F para buscar
│  └─ Se não encontrar → Continuar
│
├─ Leia código comentado:
│  ├─ forest.py ou ga.py
│  ├─ Procure método específico
│  └─ Se não entender → Continuar
│
└─ Último recurso:
   ├─ EXAMPLES.md - versão pronta
   ├─ Modificar e testar
   └─ ✓ Problema resolvido
```

---

## 🎓 Tópicos por Documento

### DOCUMENTATION.md Cobre:
- ✅ Visão geral + contexto
- ✅ Estrutura técnica completa
- ✅ Componentes e responsabilidades
- ✅ Fluxos de dados e controle
- ✅ Explicação linha-por-linha de algoritmos
- ✅ Configurações avançadas
- ✅ Formatos de entrada/saída
- ✅ Troubleshooting detalhado
- ✅ Notas técnicas e otimizações

### QUICK_REFERENCE.md Cobre:
- ✅ Resumo executivo
- ✅ Início rápido
- ✅ Diagrama de classes
- ✅ Referência de métricas
- ✅ Tabelas comparativas
- ✅ Interpretação de resultados
- ✅ FAQ resolvido
- ✅ Configurações recomendadas

### EXAMPLES.md Cobre:
- ✅ Código funcional pronto
- ✅ Diferentes casos de uso
- ✅ Comparações práticas
- ✅ Visualização de dados
- ✅ Análise de resultados
- ✅ Customização
- ✅ Dicas e truques

### Código Comentado Cobre:
- ✅ Implementação exata
- ✅ Docstrings detalhadas
- ✅ Comentários em linhas chave
- ✅ Fluxo de execução
- ✅ Estrutura de dados

---

## 📊 Cobertura de Tópicos

| Tópico | README | QUICK_REF | EXAMPLES | DOCS | Código |
|--------|--------|-----------|----------|------|--------|
| Visão Geral | ✅✅ | ✅ | - | ✅✅✅ | - |
| Começar Rápido | ✅ | ✅✅ | ✅✅✅ | - | - |
| Algoritmo GA | ✅ | ✅✅ | ✅ | ✅✅✅ | ✅✅✅ |
| Métricas | ✅ | ✅✅✅ | ✅ | ✅✅ | ✅ |
| Código/API | - | ✅ | ✅✅ | ✅✅ | ✅✅✅ |
| Exemplos | - | ✅ | ✅✅✅ | ✅ | - |
| Troubleshooting | - | ✅✅ | - | ✅✅ | ✅ |

---

## 🎯 Dica Final

> 💡 **Não sabe por onde começar?**
> 
> Comece aqui:
> 1. Leia este MAPS.md (você está!)
> 2. Encontre sua pergunta acima
> 3. Siga para o arquivo recomendado
> 4. Quando tiver dúvidas, volte ao mapa
>
> **Tempo estimado para sair do zero:** 2-3 dias
> 
> **Tempo para se tornar especialista:** 1-2 semanas

---

**Última atualização**: 2024 | **Status**: ✅ Mapa Completo
