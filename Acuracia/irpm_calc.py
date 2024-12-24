import pandas as pd
from numpy.fft import fft, fftfreq
import numpy as np

# Função para gerar o gráfico da FFT com limite de frequência
def calc_irpm(csv_file, total_time):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(csv_file, delimiter=',')
        
        # Exibir as colunas do arquivo para depuração
        #print("Colunas do arquivo CSV:", df.columns.tolist())

        # Remover espaços extras nos nomes das colunas, caso existam
        df.columns = df.columns.str.strip()

        # Verificar se as colunas necessárias estão no arquivo
        if 'Timestamp' not in df.columns or 'PressureValue' not in df.columns:
            print("Erro: O arquivo CSV deve conter as colunas 'Timestamp' e 'PressureValue'.")
            return

        # Converter a coluna 'Timestamp' para segundos
        time = df['Timestamp'].values / 1000.0
        data = df['PressureValue'].values
        time = time - time[0]
        limited_data = [d for t, d in zip(time, data) if t <= total_time]
        
        # Calcular a frequência de amostragem
        fs = len(limited_data) / total_time
        #print(f"Frequência de amostragem (fs): {fs:.2f} Hz")

        # Calcular a FFT
        n_fft = len(limited_data)
        fft_result = fft(limited_data, n=n_fft)
        spectrum = np.abs(fft_result[:n_fft // 2])
        freqs = fftfreq(len(fft_result), d=1/fs)[:n_fft // 2]

        # Limitar o espectro ao intervalo desejado
        freq_min, freq_max = 0.1, 0.5
        mask = (freqs >= freq_min) & (freqs <= freq_max)
        filtered_freqs = freqs[mask]
        filtered_spectrum = spectrum[mask]

        # Identificar a frequência dominante no intervalo
        if len(filtered_freqs) > 0:
            dominant_freq = filtered_freqs[np.argmax(filtered_spectrum)]
            return dominant_freq * 60
        else:
            print(f"Nenhuma frequência encontrada no intervalo [{freq_min}, {freq_max}] Hz.")
            return 0


    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_file}' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")


# Exemplo de uso
if __name__ == "__main__":
    csv_file = 'Pressure\\Gustavo\\16-12-2024\\pressure_data_10_gustavo.csv'  # Substitua pelo caminho do seu arquivo
    calc_irpm(csv_file)
