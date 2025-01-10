import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unidecode import unidecode
import glob

def calculate_errors(df):
    """Calcula erros absolutos e relativos. PPG_iRPM_1,PPG_iRPM_2,PPG_iRPM_3"""
    df['Error_iRPM_1_Abs'] = np.abs(df['PPG_iRPM_1'] - df['PRE_iRPM'])
    df['Error_iRPM_1_Rel'] = df['Error_iRPM_1_Abs'] / df['PRE_iRPM'] * 100
    df['Error_iRPM_2_Abs'] = np.abs(df['PPG_iRPM_2'] - df['PRE_iRPM'])
    df['Error_iRPM_2_Rel'] = df['Error_iRPM_2_Abs'] / df['PRE_iRPM'] * 100
    df['Error_iRPM_3_Abs'] = np.abs(df['PPG_iRPM_3'] - df['PRE_iRPM'])
    df['Error_iRPM_3_Rel'] = df['Error_iRPM_3_Abs'] / df['PRE_iRPM'] * 100
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
        errors_global = df[['Error_iRPM_1_Abs', 'Error_iRPM_1_Rel', 'Error_iRPM_2_Abs', 'Error_iRPM_2_Rel', 'Error_iRPM_3_Abs', 'Error_iRPM_3_Rel']].mean()
        write_line(errors_global.to_string())
        write_line("")

        # 2. Erros por método
        write_line("2. Erros por Método:")
        for method, group in df.groupby('Metodo'):
            errors_method = group[['Error_iRPM_1_Abs', 'Error_iRPM_1_Rel', 'Error_iRPM_2_Abs', 'Error_iRPM_2_Rel', 'Error_iRPM_3_Abs', 'Error_iRPM_3_Rel']].mean()
            write_line(f"Metodo: {method}")
            write_line(errors_method.to_string())
            write_line("")

        # 3. Erros por patch
        write_line("3. Erros por Patch:")
        for patch, group in df.groupby('Patch'):
            errors_patch = group[['Error_iRPM_1_Abs', 'Error_iRPM_1_Rel', 'Error_iRPM_2_Abs', 'Error_iRPM_2_Rel', 'Error_iRPM_3_Abs', 'Error_iRPM_3_Rel']].mean()
            write_line(f"Patch: {patch}")
            write_line(errors_patch.to_string())
            write_line("")

        # 4. Top 100 casos com melhores SQI1 e SQI3
        write_line("4. Top 100 casos com melhores SQI1 e SQI3 (incluindo o vídeo):")
        top_irpm1_b = df.nsmallest(200, 'Error_iRPM_1_Abs')
        write_line("Top 200 Error_iRPM_1_Abs:")
        write_line(top_irpm1_b[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI1', 'SQI3']].to_string(index=False))
        write_line("")
        top_irpm2_b = df.nsmallest(200, 'Error_iRPM_2_Abs')
        write_line("Top 200 Error_iRPM_2_Abs:")
        write_line(top_irpm2_b[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI1', 'SQI3']].to_string(index=False))
        write_line("")
        top_irpm3_b = df.nsmallest(200, 'Error_iRPM_3_Abs')
        write_line("Top 200 Error_iRPM_3_Abs:")
        write_line(top_irpm3_b[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI1', 'SQI3']].to_string(index=False))
        write_line("")

        # 5. Top 100 casos com menores SQI2 e SQI4
        write_line("5. Top 100 casos com menores SQI2 e SQI4 (incluindo o vídeo):")
        top_irpm1_s = df.nsmallest(200, 'Error_iRPM_1_Abs')
        write_line("Top 200 Error_iRPM_1_Abs:")
        write_line(top_irpm1_s[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI2', 'SQI4']].to_string(index=False))
        write_line("")
        top_irpm2_s = df.nsmallest(200, 'Error_iRPM_2_Abs')
        write_line("Top 200 Error_iRPM_2_Abs:")
        write_line(top_irpm2_s[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI2', 'SQI4']].to_string(index=False))
        write_line("")
        top_irpm3_s = df.nsmallest(200, 'Error_iRPM_3_Abs')
        write_line("Top 200 Error_iRPM_3_Abs:")
        write_line(top_irpm3_s[['Video', 'Metodo', 'Patch', 'Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs', 'SQI2', 'SQI4']].to_string(index=False))
        write_line("")

        # 6. Top 30 combinações de patch e método para menor erro absoluto BPM e iRPM
        write_line("6. Top 30 combinações de Patch e Método para menor erro absoluto BPM e iRPM:")
        top_irpm1 = df.groupby(['Patch', 'Metodo'])['Error_iRPM_1_Abs'].mean().nsmallest(30)
        write_line("Top 30 iRPM1:")
        write_line(top_irpm1.to_string())
        write_line("")
        top_irpm2 = df.groupby(['Patch', 'Metodo'])['Error_iRPM_2_Abs'].mean().nsmallest(30)
        write_line("Top 30 iRPM2:")
        write_line(top_irpm2.to_string())
        write_line("")
        top_irpm3 = df.groupby(['Patch', 'Metodo'])['Error_iRPM_3_Abs'].mean().nsmallest(30)
        write_line("Top 30 iRPM3:")
        write_line(top_irpm3.to_string())
        write_line("")

        # 7. Variação do erro com limiares de SQI
        write_line("7. Variação dos erros com limiares de SQI:")
        for sqi in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
            sqi_range = np.linspace(df[sqi].min(), df[sqi].max(), 11)
            write_line(f"{sqi} - Intervalos: {sqi_range}")
            for threshold in sqi_range[1:]:
                filtered_df = df[df[sqi] >= threshold]
                errors_filtered = filtered_df[['Error_iRPM_1_Abs', 'Error_iRPM_2_Abs', 'Error_iRPM_3_Abs']].mean()
                write_line(f"Limiar {threshold} - Erros: {errors_filtered.to_string()}")
            write_line("")

    # Geração de gráficos coletivos
    generate_collective_plots(df, plot_output_folder)


def generate_collective_plots(df, output_folder):
    """Gera gráficos coletivos para todos os vídeos combinados."""
    # Gráficos de dispersão para SQI vs erros
    for col in ['SQI1', 'SQI2', 'SQI3', 'SQI4']:
        # Erro IRPM1
        plt.figure()
        plt.scatter(df[col], df['Error_iRPM_1_Abs'], alpha=0.7)
        plt.title(f'Erro iRPM_1 vs {col} - Coletivo')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (irpm1)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_irpm1.png'))
        plt.close()

        # Erro IRPM2
        plt.figure()
        plt.scatter(df[col], df['Error_iRPM_2_Abs'], alpha=0.7)
        plt.title(f'Erro iRPM_2 vs {col} - Coletivo')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (irpm1)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_irpm2.png'))
        plt.close()

        # Erro IRPM10
        plt.figure()
        plt.scatter(df[col], df['Error_iRPM_3_Abs'], alpha=0.7)
        plt.title(f'Erro iRPM_3 vs {col} - Coletivo')
        plt.xlabel(col)
        plt.ylabel('Erro Absoluto (irpm1)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{col}_vs_Erro_irpm3.png'))
        plt.close()

    # Gráficos de barras para erros por método (IRPM1)
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_1_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM1 por Método - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm1.png'))
    plt.close()

    # Gráficos de barras para erros por método (IRPM2)
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_2_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM2 por Método - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm2.png'))
    plt.close()

    # Gráficos de barras para erros por método (IRPM3)
    plt.figure()
    df.groupby('Metodo')['Error_iRPM_3_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM3 por Método - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_metodo_irpm3.png'))
    plt.close()

    # Gráficos de barras para erros por patch (IRPM1)
    plt.figure()
    df.groupby('Patch')['Error_iRPM_1_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM1 por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm1.png'))
    plt.close()

    # Gráficos de barras para erros por patch (IRPM2)
    plt.figure()
    df.groupby('Patch')['Error_iRPM_2_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM2 por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm2.png'))
    plt.close()

    # Gráficos de barras para erros por patch (IRPM20)
    plt.figure()
    df.groupby('Patch')['Error_iRPM_3_Abs'].mean().plot(kind='bar')
    plt.title('Erro Absoluto iRPM3 por Patch - Coletivo')
    plt.ylabel('Erro Absoluto (irpm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'Erro_por_patch_irpm3.png'))
    plt.close()

if __name__ == "__main__":
    folder_path = "06-01-Resultados/Gustavo_sincronizacao_resp_test"
    output_folder = "06-01-Resultados/Gustavo_sincronizacao_Resp_results_test"
    os.makedirs(output_folder, exist_ok=True)

    dfs, combined_df = process_csv_files(folder_path)

    # Calcula os erros no DataFrame combinado
    combined_df = calculate_errors(combined_df)

    # Realiza as análises coletivas
    analyze_collective_data(combined_df, output_folder)

    print("Análises coletivas concluídas.")