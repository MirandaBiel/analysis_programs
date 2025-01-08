import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unidecode import unidecode

def calculate_errors(df):
    """Calcula erros absolutos e relativos."""
    df['Error_BPM_Abs'] = np.abs(df['PPG_BPM'] - df['ECG_BPM'])
    df['Error_BPM_Rel'] = df['Error_BPM_Abs'] / df['ECG_BPM'] * 100
    df['Error_iRPM_Abs'] = np.abs(df['PPG_iRPM'] - df['PRE_iRPM'])
    df['Error_iRPM_Rel'] = df['Error_iRPM_Abs'] / df['PRE_iRPM'] * 100
    return df

def process_csv_files(folder_path, exclude_files):
    """Lê e concatena os arquivos CSV em um DataFrame, exceto os arquivos especificados."""
    # Filtra os arquivos CSV, excluindo os presentes na lista exclude_files
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f not in exclude_files]
    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        df['Video'] = file  # Adiciona o nome do arquivo como coluna
        df = calculate_errors(df)  # Calcula os erros individuais
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

def filter_approximate(df, column, target, tolerance=0.1):
    """Filtra os dados baseados em um valor aproximado."""
    return df[np.isclose(df[column], target, atol=tolerance)]

def generate_plots(df, output_folder, suffix=""):
    """Gera gráficos considerando o conjunto completo."""
    # Gráfico de erros absolutos BPM por método
    plt.figure()
    #df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto (bpm) por Metodo {suffix}')
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_bpm_por_metodo{suffix}.png'))
    plt.close()

    # Gráfico de erros absolutos iRPM por método
    plt.figure()
    #df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto iRPM por Metodo {suffix}')
    df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_irpm_por_metodo{suffix}.png'))
    plt.close()

    # Gráfico de erros absolutos iRPM por patch
    plt.figure()
    #df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto iRPM por Patch {suffix}')
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_irpm_por_patch{suffix}.png'))
    plt.close()

    # Gráfico de erros absolutos BPM por patch
    plt.figure()
    #df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto BPM por Patch {suffix}')
    df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_bpm_por_patch{suffix}.png'))
    plt.close()

    # Gráfico de erro absoluto em função do SQI1
    plt.figure()
    plt.scatter(df['SQI1'], df['Error_BPM_Abs'], alpha=0.7)
    #plt.title(f'Erro Absoluto BPM vs SQI1 {suffix}')
    plt.xlabel('SQI1')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_vs_sqi1{suffix}.png'))
    plt.close()

    # Gráfico de erro absoluto em função do SQI2
    plt.figure()
    plt.scatter(df['SQI2'], df['Error_BPM_Abs'], alpha=0.7)
    #plt.title(f'Erro Absoluto BPM vs SQI2 {suffix}')
    plt.xlabel('SQI2')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f'erro_vs_sqi2{suffix}.png'))
    plt.close()

def analyze_and_save_results(df, output_file, suffix=""):
    """Realiza as análises e salva os resultados em um arquivo de texto."""
    with open(output_file, 'a') as f:
        def write_line(text):
            f.write(unidecode(text) + '\n')

        write_line(f"\n\nAnalise Conjunta {suffix}\n")
        write_line("="*50)

        # 1. Erros globais
        errors_global = df[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
        write_line("\nErros globais:")
        write_line(errors_global.to_string())
        write_line("")

        # 2. Erros por método
        write_line("\nErros por metodo:")
        for method, group in df.groupby('Metodo'):
            errors_method = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Metodo: {method}")
            write_line(errors_method.to_string())
            write_line("")

        # 3. Erros por patch
        write_line("\nErros por patch:")
        for patch, group in df.groupby('Patch'):
            errors_patch = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Patch: {patch}")
            write_line(errors_patch.to_string())
            write_line("")

if __name__ == "__main__":
    folder_path = "17-12-Resultados/Gustavo"
    output_folder = "17-12-Resultados/Gustavo_results"
    exclude_files = ['video_1_resultados.csv', 'video_9_resultados.csv']  # Lista de arquivos para excluir

    os.makedirs(output_folder, exist_ok=True)

    # Processa os arquivos
    combined_df = process_csv_files(folder_path, exclude_files)

    # Análise conjunta
    output_file = os.path.join(output_folder, "combined_analysis.txt")
    analyze_and_save_results(combined_df, output_file)
    generate_plots(combined_df, output_folder)

    # Análise por tempo aproximado
    for time in [10, 30]:
        df_time = filter_approximate(combined_df, 'Tempo', time)
        suffix = f"_tempo_{time}s"
        analyze_and_save_results(df_time, output_file, suffix)
        generate_plots(df_time, output_folder, suffix)

    # Análise por frequência de amostragem aproximada
    for fs in [30, 60]:
        df_fs = filter_approximate(combined_df, 'FS', fs)
        suffix = f"_fs_{fs}"
        analyze_and_save_results(df_fs, output_file, suffix)
        generate_plots(df_fs, output_folder, suffix)

    print("Processamento concluído.")
