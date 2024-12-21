import pandas as pd
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq
import numpy as np
from matplotlib.widgets import Slider

# Função para gerar o gráfico da FFT com limite de frequência
def plot_fft_with_limited_frequency(csv_file):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(csv_file, delimiter=',')
        
        # Exibir as colunas do arquivo para depuração
        print("Colunas do arquivo CSV:", df.columns.tolist())

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
        # Calcular a frequência de amostragem
        fs = len(data) / time[-1]
        print(f"Frequência de amostragem (fs): {fs:.2f} Hz")

        # Calcular a FFT
        n_fft = len(data)
        fft_result = fft(data, n=n_fft)
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
            dominant_power = filtered_spectrum[np.argmax(filtered_spectrum)]
            print(f"Frequência dominante: {dominant_freq:.2f} Hz (ou {dominant_freq * 60:.2f} iRPM)")
        else:
            print(f"Nenhuma frequência encontrada no intervalo [{freq_min}, {freq_max}] Hz.")
            return

        # Criar o gráfico da FFT
        # fig, ax = plt.subplots(figsize=(10, 6))
        # ax.plot(freqs, spectrum, color='blue', label='Espectro de Potência', alpha=0.7)
        # ax.scatter(dominant_freq, dominant_power, color='red', label='Frequência Dominante', zorder=5)
        # ax.set_title("Espectro de Potência (FFT)")
        # ax.set_xlabel("Frequência (Hz)")
        # ax.set_ylabel("Amplitude")
        # ax.set_xlim(freq_min - 0.05, freq_max + 0.05)
        # ax.grid(True)
        # ax.legend()

        # # Mostrar o gráfico
        # plt.tight_layout()
        # plt.show()

    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_file}' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")

# Função para plotar o gráfico do sinal original com slider
def plot_signal_with_slider(csv_file):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(csv_file, delimiter=',')
        
        # Exibir as colunas do arquivo para depuração
        print("Colunas do arquivo CSV:", df.columns.tolist())

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
        print("Tempo total: ", time[-1])
        # Definir os limites do gráfico
        total_time = time[-1]
        window_size = 10  # Tamanho da janela em segundos

        # Criar a figura e os eixos
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.25)  # Espaço para o slider
        ax.set_title("Sinal com Barra Deslizante")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("PressureValue")

        # Plotar o sinal inicial (primeira janela)
        start_time = 0
        end_time = start_time + window_size
        mask = (time >= start_time) & (time <= end_time)
        line, = ax.plot(time[mask], data[mask], color='green')

        ax.set_xlim(start_time, end_time)
        ax.set_ylim(data.min(), data.max())

        # Adicionar o slider
        ax_slider = plt.axes([0.15, 0.1, 0.7, 0.03], facecolor='lightgray')
        slider = Slider(ax_slider, 'Tempo (s)', 0, total_time - window_size, valinit=0)

        # Atualizar o gráfico ao mover o slider
        def update(val):
            start_time = slider.val
            end_time = start_time + window_size
            mask = (time >= start_time) & (time <= end_time)
            line.set_xdata(time[mask])
            line.set_ydata(data[mask])
            ax.set_xlim(start_time, end_time)
            fig.canvas.draw_idle()

        slider.on_changed(update)

        # Mostrar o gráfico
        plt.show()

    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_file}' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")

# Exemplo de uso
if __name__ == "__main__":
    csv_file = 'Pressure\\Gustavo\\16-12-2024\\pressure_data_10_gustavo.csv'  # Substitua pelo caminho do seu arquivo
    plot_fft_with_limited_frequency(csv_file)
    plot_signal_with_slider(csv_file)
