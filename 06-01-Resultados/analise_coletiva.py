import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unidecode import unidecode
import glob

def calculate_errors(df):
    """Calcula erros absolutos e relativos."""
    df['Error_BPM_Abs'] = np.abs(df['PPG_BPM'] - df['ECG_BPM'])
    df['Error_BPM_Rel'] = df['Error_BPM_Abs'] / df['ECG_BPM'] * 100
    df['Error_iRPM_Abs'] = np.abs(df['PPG_iRPM'] - df['PRE_iRPM'])
    df['Error_iRPM_Rel'] = df['Error_iRPM_Abs'] / df['PRE_iRPM'] * 100
    return df

def process_csv_files(folder_path):
    """Lê e combina arquivos CSV em um DataFrame."""
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        df['Video'] = os.path.basename(file).replace(".csv", "")
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return dfs, combined_df

def analyze_collective_data(df, output_folder):
    """Realiza análises coletivas e salva os resultados em um arquivo de texto."""
    text_output_file = os.path.join(output_folder, "collective_analysis.txt")
    plot_output_folder = os.path.join(output_folder, "plots_collective")
    os.makedirs(plot_output_folder, exist_ok=True)

    with open(text_output_file, 'w') as f:
        def write_line(text):
            f.write(unidecode(text) + '\n')

        write_line("Análise Coletiva de Todos os Vídeos\n")

        # 1. Erros globais
        write_line("1. Erros Globais:")
        errors_global = df[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
        write_line(errors_global.to_string())
        write_line("")

        # 2. Erros por método
        write_line("2. Erros por Método:")
        for method, group in df.groupby('Metodo'):
            errors_method = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Metodo: {method}")
            write_line(errors_method.to_string())
            write_line("")

        # 3. Erros por patch
        write_line("3. Erros por Patch:")
        for patch, group in df.groupby('Patch'):
            errors_patch = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            write_line(f"Patch: {patch}")
            write_line(errors_patch.to_string())
            write_line("")

        # 6. Top 30 combinações de patch e método para menor erro absoluto BPM e iRPM
        top_bpm = df.groupby(['Patch', 'Metodo'])['Error_BPM_Abs'].mean().nsmallest(30)
        write_line("Top 30 combinações de Patch e Metodo com menor erro absoluto BPM:")
        write_line(top_bpm.to_string())
        write_line("")

        # 4. Top 1000 melhores casos com menor erro absoluto
        write_line("4. Top 100 melhores casos com menor erro absoluto (incluindo vídeo, patch, método e SQIs):")
        top_cases = df.nsmallest(1000, 'Error_BPM_Abs')
        write_line(top_cases[['Video', 'Metodo', 'Patch', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel', 'SQI1', 'SQI2']].to_string(index=False))
        write_line("")

        # Variação do erro com limiares de SQI
        write_line("5. Variação dos erros com limiares de SQI:")
        for sqi in ['SQI1', 'SQI2']:
            sqi_range = np.linspace(df[sqi].min(), df[sqi].max(), 11)
            write_line(f"{sqi} - Intervalos: {sqi_range}")
            for threshold in sqi_range[1:]:
                filtered_df = df[df[sqi] >= threshold]
                errors_filtered = filtered_df[['Error_BPM_Abs', 'Error_iRPM_Abs']].mean()
                write_line(f"Limiar {threshold} - Erros: {errors_filtered.to_string()}")
            write_line("")

    generate_collective_plots(df, plot_output_folder)

def generate_collective_plots(df, output_folder):
    """Gera gráficos coletivos para todos os vídeos combinados."""
    # Identificar colunas que representam os SQIs
    sqi_columns = [col for col in df.columns if col.startswith("SQI")]

    for sqi_col in sqi_columns:
        # Inicializar listas para armazenar os erros médios e o número de amostras
        sqi_thresholds = np.linspace(df[sqi_col].min(), df[sqi_col].max(), 20)
        bpm_errors = []
        irpm_errors = []
        num_samples = []

        for threshold in sqi_thresholds:
            filtered_df = df[df[sqi_col] >= threshold]
            bpm_errors.append(filtered_df['Error_BPM_Abs'].mean())
            irpm_errors.append(filtered_df['Error_iRPM_Abs'].mean())
            num_samples.append(len(filtered_df))

        # Gráfico de erros médios para BPM
        plt.figure()
        plt.plot(sqi_thresholds, bpm_errors, marker='o')
        for i, (x, y, n) in enumerate(zip(sqi_thresholds, bpm_errors, num_samples)):
            plt.text(x, y, f'{n}', fontsize=8, ha='center', va='bottom')  # Adiciona o número de amostras
        plt.title(f'')
        plt.xlabel(f'Limiar de {sqi_col}')
        plt.ylabel('Erro absoluto médio (bpm)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'Variacao_Erro_BPM_com_{sqi_col}.png'))
        plt.close()

        # Gráfico de erros médios para iRPM
        plt.figure()
        plt.plot(sqi_thresholds, irpm_errors, marker='o', color='orange', label=f'Erro Médio iRPM')
        for i, (x, y, n) in enumerate(zip(sqi_thresholds, irpm_errors, num_samples)):
            plt.text(x, y, f'{n}', fontsize=8, ha='center', va='bottom')  # Adiciona o número de amostras
        plt.title(f'Variação do Erro Médio iRPM com Limiar de {sqi_col}')
        plt.xlabel(f'Limiar de {sqi_col}')
        plt.ylabel('Erro Médio iRPM')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'Variacao_Erro_iRPM_com_{sqi_col}.png'))
        plt.close()

    # Gráficos existentes (como barras por método e patch)
    plt.figure()
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto BPM por Método - Coletivo')
    plt.ylabel('Erro Absoluto Médio (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_bpm.png'))
    plt.close()

    plt.figure()
    df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM por Método - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm.png'))
    plt.close()

    plt.figure()
    df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto BPM por Patch - Coletivo')
    plt.ylabel('Erro Absoluto Médio (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_bpm.png'))
    plt.close()

    plt.figure()
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm.png'))
    plt.close()


if __name__ == "__main__":
    folder_path = "06-01-Resultados/geral_data"
    output_folder = "06-01-Resultados/geral_results"
    os.makedirs(output_folder, exist_ok=True)

    dfs, combined_df = process_csv_files(folder_path)
    combined_df = calculate_errors(combined_df)
    analyze_collective_data(combined_df, output_folder)

    print("Análises coletivas concluídas.")
