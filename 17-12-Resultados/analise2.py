import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

def analyze_and_save_results(df, output_file):
    """Realiza as análises e salva os resultados em um arquivo de texto."""
    with open(output_file, 'w') as f:
        # 1. Erros globais
        errors_global = df[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
        f.write("Erros globais:\n")
        f.write(errors_global.to_string())
        f.write("\n\n")

        # 2. Erros por método
        f.write("Erros por método:\n")
        for method, group in df.groupby('Metodo'):
            errors_method = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            f.write(f"Método: {method}\n")
            f.write(errors_method.to_string())
            f.write("\n\n")

        # 3. Erros por patch
        f.write("Erros por patch:\n")
        for patch, group in df.groupby('Patch'):
            errors_patch = group[['Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].mean()
            f.write(f"Patch: {patch}\n")
            f.write(errors_patch.to_string())
            f.write("\n\n")

        # 4. Menores erros por combinação de método e patch
        f.write("Menores erros por combinação de método e patch:\n")
        grouped = df.groupby(['Metodo', 'Patch'])[['Error_BPM_Abs', 'Error_iRPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Rel']].mean()
        min_errors_abs = grouped[['Error_BPM_Abs', 'Error_iRPM_Abs']].idxmin()
        min_errors_rel = grouped[['Error_BPM_Rel', 'Error_iRPM_Rel']].idxmin()
        f.write("Menores erros absolutos:\n")
        f.write(grouped.loc[min_errors_abs].to_string())
        f.write("\n\n")
        f.write("Menores erros relativos:\n")
        f.write(grouped.loc[min_errors_rel].to_string())
        f.write("\n\n")

        # 5. Impacto de excluir dados com SQI1 abaixo de um limiar
        for threshold in [0.5, 0.7, 1.0]:
            filtered = df[df['SQI1'] >= threshold]
            errors_filtered = filtered[['Error_BPM_Abs', 'Error_iRPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Rel']].mean()
            f.write(f"Erro após excluir SQI1 < {threshold}:\n")
            f.write(errors_filtered.to_string())
            f.write("\n\n")

        # 6. Impacto de excluir dados com SQI2 abaixo de um limiar
        for threshold in [0.5, 0.7, 1.0]:
            filtered = df[df['SQI2'] >= threshold]
            errors_filtered = filtered[['Error_BPM_Abs', 'Error_iRPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Rel']].mean()
            f.write(f"Erro após excluir SQI2 < {threshold}:\n")
            f.write(errors_filtered.to_string())
            f.write("\n\n")

        # 7. Lista ordenada dos 200 maiores valores de SQI1
        top_sqi1 = df.nlargest(200, 'SQI1')
        f.write("200 maiores valores de SQI1:\n")
        f.write(top_sqi1[['Video', 'Metodo', 'Patch', 'SQI1', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].to_string(index=False))
        f.write("\n\n")

        # 8. Lista ordenada dos 500 menores erros absolutos BPM
        top_lowest_errors = df.nsmallest(5000, 'Error_BPM_Abs')
        f.write("500 menores erros absolutos BPM:\n")
        f.write(top_lowest_errors[['Video', 'Metodo', 'Patch', 'SQI1', 'Error_BPM_Abs', 'Error_BPM_Rel', 'Error_iRPM_Abs', 'Error_iRPM_Rel']].to_string(index=False))
        f.write("\n\n")

    print(f"Resultados salvos em {output_file}")

def generate_plots(df, output_folder):
    """Gera gráficos para análises gerais."""
    # Gráfico de erros absolutos BPM por método
    plt.figure()
    df.groupby('Metodo')['Error_BPM_Abs'].mean().plot(kind='bar', title='Erro Absoluto BPM por Método')
    plt.ylabel('Erro Absoluto BPM')
    plt.savefig(os.path.join(output_folder, 'erro_bpm_por_metodo.png'))

    # Gráfico de erros absolutos iRPM por patch
    plt.figure()
    df.groupby('Patch')['Error_iRPM_Abs'].mean().plot(kind='bar', title='Erro Absoluto iRPM por Patch')
    plt.ylabel('Erro Absoluto iRPM')
    plt.savefig(os.path.join(output_folder, 'erro_irpm_por_patch.png'))

    # Gráfico de impacto de SQI1
    plt.figure()
    thresholds = [0.5, 0.7, 1.0]
    errors_sqi1 = [df[df['SQI1'] >= t]['Error_BPM_Abs'].mean() for t in thresholds]
    plt.plot(thresholds, errors_sqi1, marker='o')
    plt.title('Impacto de SQI1 nos Erros')
    plt.xlabel('Limiar SQI1')
    plt.ylabel('Erro Absoluto BPM')
    plt.savefig(os.path.join(output_folder, 'impacto_sqi1.png'))

    # Gráfico de impacto de SQI2
    plt.figure()
    errors_sqi2 = [df[df['SQI2'] >= t]['Error_BPM_Abs'].mean() for t in thresholds]
    plt.plot(thresholds, errors_sqi2, marker='o')
    plt.title('Impacto de SQI2 nos Erros')
    plt.xlabel('Limiar SQI2')
    plt.ylabel('Erro Absoluto BPM')
    plt.savefig(os.path.join(output_folder, 'impacto_sqi2.png'))

    print(f"Gráficos salvos em {output_folder}")

if __name__ == '__main__':
    folder_path = "17-12-Resultados/Gustavo"
    output_file = "17-12-Resultados/Gustavo_results.txt"
    output_folder = "17-12-Resultados/Gustavo_results"

    os.makedirs(output_folder, exist_ok=True)

    data = process_csv_files(folder_path)
    data = calculate_errors(data)
    analyze_and_save_results(data, output_file)
    generate_plots(data, output_folder)

