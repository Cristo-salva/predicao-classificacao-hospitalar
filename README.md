# Sistema Preditivo para Classificação Hospitalar 🏥

> **Versão Atual:** v4.0 (Otimizada com Filtro Temporal e Balanceamento de Classes)

Este repositório contém o código e a metodologia para um sistema de Inteligência Artificial desenvolvido para prever classificações essenciais de atendimentos em um ambiente hospitalar privado.

## 🎯 Objetivo do Projeto

O objetivo principal deste projeto é apoiar a gestão hospitalar através da previsão de duas classificações-chave no momento da admissão do paciente:

1.  **Grupo do Procedimento (`GRUPO_SUS`):** Determinar se o atendimento será primariamente clínico, cirúrgico, diagnóstico, etc.
2.  **Complexidade Assistencial (`COMPLEXIDADE_SUS`):** Estimar o nível de recursos (Atenção Básica, Média ou Alta Complexidade) que o paciente irá demandar.

Estas previsões permitem uma gestão proativa de recursos, otimização do planejamento operacional e melhor previsibilidade de custos.

## 🔄 Evolução e Metodologia (v4.0)

O projeto passou por ciclos rigorosos de aprimoramento baseados em análise de dados:

* **Combate ao Data Drift:** Uma análise de distribuição temporal revelou uma mudança significativa no perfil dos procedimentos hospitalares entre 2012 e 2019. Para garantir precisão máxima na realidade atual, o modelo agora utiliza uma **janela deslizante**, treinando apenas com dados a partir de **2020**.
* **Balanceamento de Classes (SMOTE):** Para resolver o desbalanceamento natural dos dados de saúde, foi implementada a técnica *Synthetic Minority Over-sampling Technique* (SMOTE), aumentando drasticamente a capacidade do modelo de detectar casos raros e de **Alta Complexidade**.
* **Regras de Negócio Híbridas:** Uma camada lógica pós-processamento corrige inconsistências, garantindo que procedimentos cirúrgicos explícitos não sejam classificados incorretamente.

## 🚀 Resultados Principais

O sistema utiliza modelos de Machine Learning (**LightGBM**) otimizados. A performance validada nos dados mais recentes (Outubro/2025) atingiu:

* **96% de Acurácia** na previsão de `COMPLEXIDADE_SUS`.
    * *Destaque:* O **Recall para "Alta Complexidade" atingiu 83%**, permitindo a identificação antecipada da grande maioria dos casos críticos.
* **95% de Acurácia** na previsão de `GRUPO_SUS`.
    * *Destaque:* O F1-Score médio subiu para 0.87, demonstrando grande equilíbrio entre as classes clínicas e cirúrgicas.

## 🛠️ Estrutura e Como Usar

O projeto está organizado em um script mestre que automatiza o ciclo de vida do modelo (MLOps).

**Arquivo Principal:** `script_classificacao_sus_otimizado_v4.py`

O script executa três etapas automaticamente:
1.  **Treinamento Inteligente:** Verifica se os modelos existem. Se não, carrega o histórico, aplica a limpeza, filtra os dados (2020+), aplica o SMOTE e treina novos classificadores.
2.  **Avaliação:** Gera relatórios de precisão, recall e f1-score para validar a performance.
3.  **Previsão:** Carrega novos arquivos mensais (suporte a `.csv` e `.xlsx`), gera as previsões e aplica as regras de correção de negócio.

## 📊 Arquivos de Dados

* `historico_saidas(ajustado).csv`: (DADO PRIVADO - NÃO INCLUÍDO) Base histórica anonimizada usada para o treinamento.
* `[mes]_2025_saidas.xlsx`: Arquivos de entrada mensal com os novos atendimentos a serem classificados.

## 💻 Tecnologias Utilizadas

* **Linguagem:** Python 3.11+
* **Core:** Pandas, Scikit-learn, LightGBM.
* **Técnicas Avançadas:** Imbalanced-learn (SMOTE), OpenPyXL.

---
*Este projeto foi desenvolvido como um caso de estudo para a aplicação de IA na gestão de saúde e aprovado para apresentação na Sessão Pôster do **CONAHP 2025** no eixo de INOVAÇÃO.*
