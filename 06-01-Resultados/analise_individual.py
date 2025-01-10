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
    text_output_folder = os.path.join(output_folder, "texts")
    plot_output_folder = os.path.join(output_folder, "plots")
    os.makedirs(text_output_folder, exist_ok=True)
    os.makedirs(plot_output_folder, exist_ok=True)

    for df in dfs:
        video_name = df['Video'].iloc[0]
        video_plot_folder = os.path.join(plot_output_folder, video_name)
        #os.makedirs(video_plot_folder, exist_ok=True)

        output_file = os.path.join(text_output_folder, f"{video_name}_analysis.txt")
        analyze_and_save_results(df, output_file)

        generate_plots(df, video_plot_folder, video_name)

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

        # 4. Top 100 casos com melhores SQI1 e SQI3
        top_sqi1 = df.nlargest(100, 'SQI1')
        write_line("Top 100 casos com melhores SQI1:")
        write_line(top_sqi1[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI1']].to_string(index=False))
        write_line("")

        top_sqi3 = df.nlargest(100, 'SQI3')
        write_line("Top 100 casos com melhores SQI3:")
        write_line(top_sqi3[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI3']].to_string(index=False))
        write_line("")

        # 5. Top 100 casos com menores SQI2 e SQI4
        top_sqi2 = df.nsmallest(100, 'SQI2')
        write_line("Top 100 casos com menores SQI2:")
        write_line(top_sqi2[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI2']].to_string(index=False))
        write_line("")

        top_sqi4 = df.nsmallest(100, 'SQI4')
        write_line("Top 100 casos com menores SQI4:")
        write_line(top_sqi4[['Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI4']].to_string(index=False))
        write_line("")

        # 6. Top 30 combinações de patch e método para menor erro absoluto BPM e iRPM
        top_bpm = df.groupby(['Patch', 'Metodo'])['Error_BPM_Abs'].mean().nsmallest(30)
        write_line("Top 30 combinações de Patch e Metodo com menor erro absoluto BPM:")
        write_line(top_bpm.to_string())
        write_line("")

        top_irpm = df.groupby(['Patch', 'Metodo'])['Error_iRPM_Abs'].mean().nsmallest(30)
        write_line("Top 30 combinações de Patch e Metodo com menor erro absoluto iRPM:")
        write_line(top_irpm.to_string())
        write_line("")

        # 7. Variação do erro com limiares de SQI
        write_line("Variação dos erros com limiares de SQI:")
        for sqi in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
            sqi_range = np.linspace(df[sqi].min(), df[sqi].max(), 11)
            write_line(f"{sqi} - Intervalos: {sqi_range}")
            for threshold in sqi_range[1:]:
                filtered_df = df[df[sqi] >= threshold]
                errors_filtered = filtered_df[['Error_BPM_Abs', 'Error_iRPM_Abs']].mean()
                write_line(f"Limiar {threshold} - Erros: {errors_filtered.to_string()}")
            write_line("")

def generate_plots(df, output_folder, video_name):
    """Gera gráficos organizados por categorias temáticas."""
    # Criação das subpastas fixas
    subfolders = [
        "Erro_por_metodo_bpm",
        "Erro_por_metodo_irpm",
        "Erro_por_patch_bpm",
        "Erro_por_patch_irpm",
        "SQI1_vs_Erro_bpm",
        "SQI1_vs_Erro_irpm",
        "SQI2_vs_Erro_bpm",
        "SQI2_vs_Erro_irpm",
        "SQI3_vs_Erro_bpm",
        "SQI3_vs_Erro_irpm",
        "SQI4_vs_Erro_bpm",
        "SQI4_vs_Erro_irpm"
    ]
    output_folder = os.path.dirname(output_folder)
    for subfolder in subfolders:
        os.makedirs(os.path.join(output_folder, subfolder), exist_ok=True)

    # Gráficos de dispersão para SQI vs erros
    for col in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
        # Erro BPM
        plt.figure()
        plt.scatter(df[col], df['Error_BPM_Abs'], alpha=0.7)
        plt.title(f'Erro BPM vs {col} - {video_name}')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (bpm)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_bpm', f'{video_name}_erro_bpm_vs_{col}.png'))
        plt.close()

        # Erro iRPM
        plt.figure()
        plt.scatter(df[col], df['Error_iRPM_Abs'], alpha=0.7)
        plt.title(f'Erro iRPM vs {col} - {video_name}')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (irpm)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_irpm', f'{video_name}_erro_irpm_vs_{col}.png'))
        plt.close()

    # Gráficos de barras para erros por método (BPM)
    plt.figure()
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title(f'Erro Absoluto BPM por Método - {video_name}')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_bpm', f'{video_name}_erro_bpm_por_metodo.png'))
    plt.close()

    # Gráficos de barras para erros por método (iRPM)
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title(f'Erro Absoluto iRPM por Método - {video_name}')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm', f'{video_name}_erro_irpm_por_metodo.png'))
    plt.close()

    # Gráficos de barras para erros por patch (BPM)
    plt.figure()
    df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title(f'Erro Absoluto BPM por Patch - {video_name}')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_bpm', f'{video_name}_erro_bpm_por_patch.png'))
    plt.close()

    # Gráficos de barras para erros por patch (iRPM)
    plt.figure()
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title(f'Erro Absoluto iRPM por Patch - {video_name}')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm', f'{video_name}_erro_irpm_por_patch.png'))
    plt.close()


if __name__ == "__main__":
    folder_path = "06-01-Resultados/Gustavo_sincronizacao_data"
    output_folder = "06-01-Resultados/Gustavo_sincronizacao_results"
    os.makedirs(output_folder, exist_ok=True)

    dfs, combined_df = process_csv_files(folder_path)

    # Análise individual para cada vídeo
    analyze_individual_files(dfs, output_folder)

    print("Processamento concluído.")
