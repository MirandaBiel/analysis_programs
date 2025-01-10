from scipy.signal import find_peaks
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Função para ler o arquivo CSV e gerar o gráfico
def calc_bpm(csv_file, total_time=30):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(csv_file, delimiter=',')
        
        # Exibir as colunas do arquivo para depuração
        #print("Colunas do arquivo CSV:", df.columns.tolist())

        # Remover espaços extras nos nomes das colunas, caso existam
        df.columns = df.columns.str.strip()

        # Verificar se as colunas necessárias estão no arquivo
        if 'Timestamp' not in df.columns or 'ECGValue' not in df.columns:
            print("Erro: O arquivo CSV deve conter as colunas 'Timestamp' e 'ECGValue'.")
            return

        # Converter a coluna 'Timestamp' para segundos
        time = df['Timestamp'].values / 1000.0
        data = df['ECGValue'].values
        time = time - time[0]
        
        # Limita os dados para o tempo de aquisição da PPG
        limited_data = np.array([d for t, d in zip(time, data) if t <= total_time])
        limited_time = np.array([t for t in time if t <= total_time])
        
        fs = len(limited_data) / limited_time[-1]

        peaks, _ = find_peaks(limited_data, height=400, distance=fs/1.5)

        if len(peaks) < 2:
            print("Não foram encontrados picos R suficientes.")
            return 0

        rr_intervals_samples = np.diff(peaks)
        rr_intervals_seconds = rr_intervals_samples / fs
        heart_rate = 60 / rr_intervals_seconds
        mean_heart_rate = np.mean(heart_rate)
        
        # plt.figure(figsize=(12, 6))
        # plt.plot(limited_data, label='Sinal Original', linewidth=0.7)  # Linha mais fina para o sinal original
        # plt.plot(peaks, limited_data[peaks], "x", color="red", label='Picos Detectados', markersize=8) #picos pretos e maiores
        # plt.xlabel('Amostras')
        # plt.ylabel('Valor do ECG')
        # plt.title('Detecção de Picos com Média Móvel')
        # plt.legend()
        # plt.grid(True, linestyle='--', alpha=0.6) #adicionado grid
        # plt.tight_layout() #melhora o espaçamento do plot
        # plt.show()

        
        return mean_heart_rate


    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_file}' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")


# Exemplo de uso
if __name__ == "__main__":
    # Informe o caminho do arquivo CSV
    csv_file = 'ECGs\Gustavo_second\ecg_data_18.csv'  # Substitua pelo caminho do seu arquivo
    calc_bpm(csv_file)
