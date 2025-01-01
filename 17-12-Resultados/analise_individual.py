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

def process_csv_files(folder_path):
    """Lê e concatena os arquivos CSV em um DataFrame."""
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        df['Video'] = file  # Adiciona o nome do arquivo como coluna
        df = calculate_errors(df)  # Calcula os erros individuais
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return dfs, combined_df

def analyze_individual_files(dfs, output_folder):
    """Realiza análises individuais para cada arquivo."""
    for df in dfs:
        video_name = df['Video'].iloc[0]
        video_output_folder = os.path.join(output_folder, video_name)
        os.makedirs(video_output_folder, exist_ok=True)
        
        output_file = os.path.join(video_output_folder, f"{video_name}_analysis.txt")
        analyze_and_save_results(df, output_file)
        
        generate_plots(df, video_output_folder)

def analyze_and_save_results(df, output_file):
    """Realiza as análises e salva os resultados em um arquivo de texto."""
    with open(output_file, 'w') as f:
        def write_line(text):
            f.write(unidecode(text) + '\n')

        write_line(f"Analise do arquivo: {df['Video'].iloc[0]}\n")

        # 1. Erros globais
        errors_global = df[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
        write_line("Erros globais:")
        write_line(errors_global.to_string())
        write_line("")

        # 2. Erros por método
        write_line("Erros por metodo:")
        for method, group in df.groupby('Metodo'):
            errors_method = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Metodo: {method}")
            write_line(errors_method.to_string())
            write_line("")

        # 3. Erros por patch
        write_line("Erros por patch:")
        for patch, group in df.groupby('Patch'):
            errors_patch = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Patch: {patch}")
            write_line(errors_patch.to_string())
            write_line("")

        # 4. Top 100 casos com melhores SQI1
        top_sqi1 = df.nlargest(100, 'SQI1')
        write_line("Top 100 casos com melhores SQI1:")
        write_line(top_sqi1[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI1', 'SQI2']].to_string(index=False))
        write_line("")

        # 5. Top 100 casos com menores SQI2
        top_sqi2 = df.nsmallest(100, 'SQI2')
        write_line("Top 100 casos com menores SQI2:")
        write_line(top_sqi2[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI1', 'SQI2']].to_string(index=False))
        write_line("")

def generate_plots(df, output_folder):
    """Gera gráficos para análises do vídeo individual."""
    video_name = df['Video'].iloc[0]

    # Gráfico de erros absolutos BPM por método
    plt.figure()
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto BPM por Metodo - {video_name}')
    plt.ylabel('Erro Absoluto BPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_bpm_por_metodo.png'))
    plt.close()

    # Gráfico de erros absolutos iRPM por método
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto iRPM por Metodo - {video_name}')
    plt.ylabel('Erro Absoluto iRPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_irpm_por_metodo.png'))
    plt.close()

    # Gráfico de erros absolutos iRPM por patch
    plt.figure()
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto iRPM por Patch - {video_name}')
    plt.ylabel('Erro Absoluto iRPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_irpm_por_patch.png'))
    plt.close()

    # Gráfico de erros absolutos BPM por patch
    plt.figure()
    df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar', title=f'Erro Absoluto BPM por Patch - {video_name}')
    plt.ylabel('Erro Absoluto BPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_bpm_por_patch.png'))
    plt.close()

    # Gráfico de erro absoluto em função do SQI1
    plt.figure()
    plt.scatter(df['SQI1'], df['Error_BPM_Abs'], alpha=0.7)
    plt.title(f'Erro Absoluto BPM vs SQI1 - {video_name}')
    plt.xlabel('SQI1')
    plt.ylabel('Erro Absoluto BPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_vs_sqi1.png'))
    plt.close()

    # Gráfico de erro absoluto em função do SQI2
    plt.figure()
    plt.scatter(df['SQI2'], df['Error_BPM_Abs'], alpha=0.7)
    plt.title(f'Erro Absoluto BPM vs SQI2 - {video_name}')
    plt.xlabel('SQI2')
    plt.ylabel('Erro Absoluto BPM')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'erro_vs_sqi2.png'))
    plt.close()

if __name__ == "__main__":
    folder_path = "17-12-Resultados/Gustavo"
    output_folder = "17-12-Resultados/Gustavo_results"
    os.makedirs(output_folder, exist_ok=True)

    dfs, combined_df = process_csv_files(folder_path)

    # Análise individual para cada vídeo
    analyze_individual_files(dfs, output_folder)

    print("Processamento concluído.")
