# Sistema Preditivo para Classificação Hospitalar

Este repositório contém o código e a metodologia para um sistema de Inteligência Artificial desenvolvido para prever classificações essenciais de atendimentos em um ambiente hospitalar privado.

## 🎯 Objetivo do Projeto

O objetivo principal deste projeto é apoiar a gestão hospitalar através da previsão de duas classificações-chave no momento da admissão do paciente:
1.  **Grupo do Procedimento (`GRUPO_SUS`)**: Determinar se o atendimento será primariamente clínico, cirúrgico, diagnóstico, etc.
2.  **Complexidade Assistencial (`COMPLEXIDADE_SUS`)**: Estimar o nível de recursos (Atenção Básica, Média ou Alta Complexidade) que o paciente irá demandar.

Estas previsões permitem uma gestão proativa de recursos, otimização do planejamento operacional e melhor previsibilidade de custos.

## 🚀 Resultados Principais

O sistema utiliza um modelo de Machine Learning (LightGBM) treinado com um histórico de dados enriquecido com features demográficas e clínicas. A performance final validada em um conjunto de teste foi:

* **92.5% de Acurácia** na previsão de `COMPLEXIDADE_SUS`.
* **88.6% de Acurácia** na previsão de `GRUPO_SUS`.

Além do modelo estatístico, foi implementada uma camada de regras de negócio para corrigir inconsistências lógicas, como classificar um atendimento como "clínico" quando um procedimento cirúrgico está explicitamente registrado.

## 🛠️ Estrutura e Como Usar

O projeto está organizado em um script principal que automatiza o ciclo de vida do modelo (MLOps).

* **`script_principal.py`**: Este é o script mestre.
    * **Treinamento:** Se os modelos (`.joblib`) não existirem, ele treina novos classificadores usando o `historico_saidas.csv` e os salva.
    * **Avaliação:** Após o treino, ele gera um relatório de performance para os modelos recém-criados.
    * **Previsão:** Ele carrega um novo arquivo de dados (ex: `junho_2025_saidas.csv`), aplica os modelos treinados e salva um novo CSV com as colunas de previsão (`GRUPO_SUS_PREVISTO` e `COMPLEXIDADE_SUS_PREVISTO`).

## 📊 Arquivos de Dados

* **`historico_saidas.csv`**: (DADO PRIVADO - NÃO INCLUÍDO) Contém o histórico completo de atendimentos anonimizados usado para o treinamento. Para rodar o script, um arquivo com esta estrutura é necessário.
* **Arquivos Mensais (ex: `abril_2025_saidas.csv`)**: Contêm os novos dados a serem classificados.

## 💻 Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Bibliotecas Principais:** Pandas, Scikit-learn, LightGBM, Joblib.

---
*Este projeto foi desenvolvido como um caso de estudo para a aplicação de IA na gestão de saúde e será submetido à Sessão Pôster do CONAHP 2025 no eixo de INOVAÇÃO.*
