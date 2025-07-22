
# SCRIPT PRINCIPAL E FINAL: Treina, Avalia e Prevê (com Camada de Correção)

import pandas as pd
import re
import gc
import joblib
import os

# Imports do Scikit-learn e do LightGBM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import lightgbm as lgb
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURAÇÃO ---
# Mude aqui o nome do arquivo para o mês que você quer prever
NOME_ARQUIVO_PARA_PREVER = 'junho_2025_saidas.csv'
NOME_ARQUIVO_SAIDA = 'junho_2025_com_previsoes_corrigido.csv'
# --------------------

# --- Funções Auxiliares ---
def get_existing_features(df, feature_list):
    return [f for f in feature_list if f in df.columns]

# --- PARTE A: TREINAMENTO E AVALIAÇÃO (SÓ EXECUTA SE OS MODELOS NÃO EXISTIREM) ---
print("--- Verificando a existência dos modelos treinados ---")

if not os.path.exists('modelo_grupo_sus.joblib') or not os.path.exists('modelo_complexidade_sus.joblib'):
    print("Modelos não encontrados. Iniciando treinamento inicial...")

    try:
        df_historico = pd.read_csv('historico_saidas(ajustado).csv', encoding='latin-1', sep=';', low_memory=False)
    except Exception as e:
        raise ValueError(f"Não foi possível ler o arquivo historico_saidas(ajustado).csv: {e}")

    print("Realizando pré-processamento dos dados históricos...")
    df_historico.columns = map(str.lower, df_historico.columns)
    df_historico['capitulo_cid'] = df_historico['cid_1_principal'].astype(str).str[0]
    colunas_para_limpar = ['grupo_sus', 'complexidade_sus', 'idade', 'sexo', 'nr_dias_internacao']
    df_historico.dropna(subset=[col for col in colunas_para_limpar if col in df_historico.columns], inplace=True)

    df_train, df_test = train_test_split(df_historico, test_size=0.2, random_state=42)
    print(f"\nDados divididos em {len(df_train)} para treino e {len(df_test)} para avaliação.")
    del df_historico
    gc.collect()

    print("Definindo o pipeline de pré-processamento...")
    features_categoricas = ['cid_entrada', 'procedimento_entrada', 'cid_1_principal', 'cirurgia', 'capitulo_cid', 'sexo', 'medico_resp_atend']
    features_numericas = ['idade', 'nr_dias_internacao']
    preprocessor = ColumnTransformer(transformers=[('num', StandardScaler(), get_existing_features(df_train, features_numericas)), ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), get_existing_features(df_train, features_categoricas))], remainder='drop')

    print("\nTreinando e salvando modelo para GRUPO_SUS...")
    pipeline_grupo_sus = Pipeline([('preprocessor', preprocessor), ('classifier', lgb.LGBMClassifier(random_state=42, n_jobs=-1))])
    pipeline_grupo_sus.fit(df_train, df_train['grupo_sus'])
    joblib.dump(pipeline_grupo_sus, 'modelo_grupo_sus.joblib')
    print(">> Modelo 'modelo_grupo_sus.joblib' salvo.")

    print("\nTreinando e salvando modelo para COMPLEXIDADE_SUS...")
    pipeline_complexidade_sus = Pipeline([('preprocessor', preprocessor), ('classifier', lgb.LGBMClassifier(random_state=42, n_jobs=-1))])
    pipeline_complexidade_sus.fit(df_train, df_train['complexidade_sus'])
    joblib.dump(pipeline_complexidade_sus, 'modelo_complexidade_sus.joblib')
    print(">> Modelo 'modelo_complexidade_sus.joblib' salvo.")

    print("\n--- AVALIANDO PERFORMANCE DOS NOVOS MODELOS ---")
    gs_preds_eval = pipeline_grupo_sus.predict(df_test)
    cs_preds_eval = pipeline_complexidade_sus.predict(df_test)
    print("\nRelatório de Avaliação para GRUPO_SUS:")
    print(classification_report(df_test['grupo_sus'], gs_preds_eval, zero_division=0))
    print("\nRelatório de Avaliação para COMPLEXIDADE_SUS:")
    print(classification_report(df_test['complexidade_sus'], cs_preds_eval, zero_division=0))

else:
    print("Modelos já existem. Pulando o treinamento e avaliação.")


# --- PARTE B: PREDIÇÃO EM NOVOS DADOS ---
print(f"\n--- Iniciando predição no arquivo '{NOME_ARQUIVO_PARA_PREVER}' ---")

try:
    pipeline_grupo_sus = joblib.load('modelo_grupo_sus.joblib')
    pipeline_complexidade_sus = joblib.load('modelo_complexidade_sus.joblib')
    df_para_prever = pd.read_csv(NOME_ARQUIVO_PARA_PREVER, encoding='latin-1', sep=';', low_memory=False)
    df_final = df_para_prever.copy()
    print("Modelos e arquivo de predição carregados.")

    df_para_prever.columns = map(str.lower, df_para_prever.columns)
    if 'cid_1_principal' in df_para_prever.columns:
        df_para_prever['capitulo_cid'] = df_para_prever['cid_1_principal'].astype(str).str[0]

    features_esperadas = ['cid_entrada', 'procedimento_entrada', 'cid_1_principal', 'cirurgia', 'capitulo_cid', 'sexo', 'medico_resp_atend', 'idade', 'nr_dias_internacao']
    for col in features_esperadas:
        if col not in df_para_prever.columns:
            df_para_prever[col] = 0 if col in ['idade', 'nr_dias_internacao'] else 'DESCONHECIDO'

    print("Realizando previsões...")
    grupo_sus_previsto = pipeline_grupo_sus.predict(df_para_prever)
    complexidade_sus_prevista = pipeline_complexidade_sus.predict(df_para_prever)

    ### INÍCIO DA CORREÇÃO (PÓS-PROCESSAMENTO) ###
    print("Aplicando regra de negócio de override para 'Cirurgia'...")

    if 'cirurgia' not in df_para_prever.columns: df_para_prever['cirurgia'] = 'DESCONHECIDO'
    df_para_prever['cirurgia'] = df_para_prever['cirurgia'].astype(str)

    valores_nao_cirurgicos = ['DESCONHECIDO', 'NAO_CIRURGICO', 'nan', '']
    condicao_cirurgia_presente = ~df_para_prever['cirurgia'].isin(valores_nao_cirurgicos)
    condicao_erro_modelo = (grupo_sus_previsto == 'Procedimentos clínicos')
    indices_para_corrigir = df_para_prever[condicao_cirurgia_presente & condicao_erro_modelo].index

    if not indices_para_corrigir.empty:
        print(f"Corrigindo {len(indices_para_corrigir)} previsões onde a regra de cirurgia foi ignorada pelo modelo...")
        # Trabalhamos com a Series numpy para modificar
        grupo_sus_previsto_corrigido = grupo_sus_previsto.copy()
        grupo_sus_previsto_corrigido[indices_para_corrigir] = 'Procedimentos cirúrgicos'
        df_final['GRUPO_SUS_PREVISTO'] = grupo_sus_previsto_corrigido
    else:
        print("Nenhuma correção necessária. O modelo já respeitou a regra de cirurgia.")
        df_final['GRUPO_SUS_PREVISTO'] = grupo_sus_previsto
    ### FIM DA CORREÇÃO ###

    df_final['COMPLEXIDADE_PREVISTA'] = complexidade_sus_prevista

    df_final.to_csv(NOME_ARQUIVO_SAIDA, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nSUCESSO! As previsões foram salvas no arquivo: '{NOME_ARQUIVO_SAIDA}'")

except FileNotFoundError:
    print(f"\nERRO: O arquivo '{NOME_ARQUIVO_PARA_PREVER}' não foi encontrado.")
except Exception as e:
    print(f"\nOcorreu um erro durante a predição: {e}")