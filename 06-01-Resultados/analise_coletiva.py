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
    """
    Lê todos os arquivos CSV de um diretório, processa e combina em um único DataFrame.
    Retorna uma lista de DataFrames individuais e um DataFrame combinado.
    """
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    dfs = []
    
    for file in csv_files:
        # Lê o arquivo CSV
        df = pd.read_csv(file)
        # Adiciona uma coluna indicando o nome do vídeo (baseado no arquivo CSV)
        df['Video'] = os.path.basename(file).replace(".csv", "")
        dfs.append(df)
    
    # Combina todos os DataFrames em um único DataFrame
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

        # 4. Top 100 casos com melhores SQI1 e SQI3
        write_line("4. Top 100 casos com melhores SQI1 e SQI3 (incluindo o vídeo):")
        top_sqi1 = df.nlargest(1000, 'SQI1')
        write_line("Top 100 SQI1:")
        write_line(top_sqi1[['Video', 'Metodo', 'Patch', 'Error_BPM_Abs', 'Error_iRPM_Abs', 'SQI1']].to_string(index=False))
        write_line("")
        top_sqi3 = df.nlargest(1000, 'SQI3')
        write_line("Top 100 SQI3:")
        write_line(top_sqi3[['Video', 'Metodo', 'Patch', 'Error_BPM_Abs', 'Error_iRPM_Abs', 'SQI3']].to_string(index=False))
        write_line("")

        # 5. Top 100 casos com menores SQI2 e SQI4
        write_line("5. Top 100 casos com menores SQI2 e SQI4 (incluindo o vídeo):")
        top_sqi2 = df.nsmallest(100, 'SQI2')
        write_line("Top 100 SQI2:")
        write_line(top_sqi2[['Video', 'Metodo', 'Patch', 'Error_BPM_Abs', 'Error_iRPM_Abs', 'SQI2']].to_string(index=False))
        write_line("")
        top_sqi4 = df.nsmallest(100, 'SQI4')
        write_line("Top 100 SQI4:")
        write_line(top_sqi4[['Video', 'Metodo', 'Patch', 'Error_BPM_Abs', 'Error_iRPM_Abs', 'SQI4']].to_string(index=False))
        write_line("")

        # 6. Top 100 combinações de patch e método para menor erro absoluto BPM e iRPM
        write_line("6. Top 100 combinações de Patch e Método para menor erro absoluto BPM e iRPM:")
        top_bpm = df.groupby(['Patch', 'Metodo'])['Error_BPM_Abs'].mean().nsmallest(100)
        write_line("Top 100 BPM:")
        write_line(top_bpm.to_string())
        write_line("")
        top_irpm = df.groupby(['Patch', 'Metodo'])['Error_iRPM_Abs'].mean().nsmallest(100)
        write_line("Top 100 iRPM:")
        write_line(top_irpm.to_string())
        write_line("")

        # 7. Variação do erro com limiares de SQI
        write_line("7. Variação dos erros com limiares de SQI:")
        for sqi in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
            sqi_range = np.linspace(df[sqi].min(), df[sqi].max(), 11)
            write_line(f"{sqi} - Intervalos: {sqi_range}")
            for threshold in sqi_range[1:]:
                filtered_df = df[df[sqi] >= threshold]
                errors_filtered = filtered_df[['Error_BPM_Abs', 'Error_iRPM_Abs']].mean()
                write_line(f"Limiar {threshold} - Erros: {errors_filtered.to_string()}")
            write_line("")

    # Geração de gráficos coletivos
    generate_collective_plots(df, plot_output_folder)


def generate_collective_plots(df, output_folder):
    """Gera gráficos coletivos para todos os vídeos combinados."""
    # Gráficos de dispersão para SQI vs erros
    for col in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
        # Erro BPM
        plt.figure()
        plt.scatter(df[col], df['Error_BPM_Abs'], alpha=0.7)
        plt.title(f'Erro BPM vs {col} - Coletivo')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (bpm)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_bpm.png'))
        plt.close()

        # Erro iRPM
        plt.figure()
        plt.scatter(df[col], df['Error_iRPM_Abs'], alpha=0.7)
        plt.title(f'Erro iRPM vs {col} - Coletivo')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (irpm)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_irpm.png'))
        plt.close()

    # Gráficos de barras para erros por método (BPM)
    plt.figure()
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto BPM por Método - Coletivo')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_bpm.png'))
    plt.close()

    # Gráficos de barras para erros por método (iRPM)
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM por Método - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm.png'))
    plt.close()

    # Gráficos de barras para erros por patch (BPM)
    plt.figure()
    df.groupby('Patch')['Error_BPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto BPM por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (bpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_bpm.png'))
    plt.close()

    # Gráficos de barras para erros por patch (iRPM)
    plt.figure()
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm.png'))
    plt.close()

if __name__ == "__main__":
    folder_path = "06-01-Resultados/Gabriel_init_data"
    output_folder = "06-01-Resultados/Gabriel_init_results"
    os.makedirs(output_folder, exist_ok=True)

    dfs, combined_df = process_csv_files(folder_path)

    # Calcula os erros no DataFrame combinado
    combined_df = calculate_errors(combined_df)

    # Realiza as análises coletivas
    analyze_collective_data(combined_df, output_folder)

    print("Análises coletivas concluídas.")