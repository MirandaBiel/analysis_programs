import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Configurar exibição gráfica
sns.set(style="whitegrid")

# Função para calcular estatísticas de erro
def calcular_estatisticas(df):
    df["Erro_Absoluto"] = np.abs(df["PPG_BPM"] - df["ECG_BPM"])
    df["Erro_Relativo"] = df["Erro_Absoluto"] / df["ECG_BPM"] * 100
    estatisticas = {
        "Erro Absoluto Médio": df["Erro_Absoluto"].mean(),
        "Erro Relativo Médio (%)": df["Erro_Relativo"].mean(),
        "SQI1 Médio": df["SQI1"].mean(),
        "SQI2 Médio": df["SQI2"].mean(),
    }
    return estatisticas

# Função para gerar gráficos
def gerar_graficos(df, folder_out, prefix=""):
    # Boxplot de erros por método
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="Metodo", y="Erro_Absoluto")
    plt.title("Erro Absoluto por Método")
    plt.savefig(os.path.join(folder_out, f"{prefix}_erro_absoluto_por_metodo.png"))
    plt.close()

    # Boxplot de erros por patch
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="Patch", y="Erro_Absoluto")
    plt.title("Erro Absoluto por Patch")
    plt.savefig(os.path.join(folder_out, f"{prefix}_erro_absoluto_por_patch.png"))
    plt.close()

    # Scatterplot de SQI vs Erro
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x="SQI1", y="Erro_Absoluto", hue="Metodo")
    plt.title("SQI1 vs Erro Absoluto")
    plt.savefig(os.path.join(folder_out, f"{prefix}_sqi1_vs_erro_absoluto.png"))
    plt.close()

# Função principal para análise
def analisar_pasta_csv(pasta_csv, pasta_out, sqi1_limite=0, sqi2_limite=0):
    if not os.path.exists(pasta_out):
        os.makedirs(pasta_out)

    resultados_gerais = []
    arquivos_csv = [f for f in os.listdir(pasta_csv) if f.endswith('.csv')]

    for arquivo in arquivos_csv:
        caminho_arquivo = os.path.join(pasta_csv, arquivo)
        df = pd.read_csv(caminho_arquivo)

        # Estatísticas gerais
        estatisticas = calcular_estatisticas(df)
        estatisticas["Arquivo"] = arquivo
        resultados_gerais.append(estatisticas)

        # Análise e gráficos gerais
        gerar_graficos(df, pasta_out, prefix=arquivo.split('.')[0])

        # Análises específicas por método
        for metodo, df_metodo in df.groupby("Metodo"):
            gerar_graficos(df_metodo, pasta_out, prefix=f"{arquivo.split('.')[0]}_{metodo}")

        # Análises específicas por patch
        for patch, df_patch in df.groupby("Patch"):
            gerar_graficos(df_patch, pasta_out, prefix=f"{arquivo.split('.')[0]}_patch_{patch}")

        # Análise com filtros de qualidade
        df_filtrado = df[(df["SQI1"] > sqi1_limite) & (df["SQI2"] > sqi2_limite)]
        if not df_filtrado.empty:
            gerar_graficos(df_filtrado, pasta_out, prefix=f"{arquivo.split('.')[0]}_sqi_filtrado")

    # Salvar resultados gerais
    resultados_gerais_df = pd.DataFrame(resultados_gerais)
    resultados_gerais_df.to_csv(os.path.join(pasta_out, "resultados_gerais.csv"), index=False)

    print("Análise concluída. Os resultados foram salvos na pasta:", pasta_out)

# Exemplo de execução
# Substitua "caminho_para_pasta_csv" e "caminho_para_pasta_saida" pelos caminhos apropriados
pasta_csv = "17-12-Resultados/Gustavo"
pasta_saida = "17-12-Resultados/Gustavo_analisado"
analisar_pasta_csv(pasta_csv, pasta_saida, sqi1_limite=0.8, sqi2_limite=0.1)
