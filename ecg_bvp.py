import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

# Função para normalizar os valores entre 0 e 1
def normalize(signal):
    return (signal - np.min(signal)) / (np.max(signal) - np.min(signal))

# Carregar os dados do ECG e BVP
ecg_file = "ecg_data_5.csv"  # Substitua pelo caminho do arquivo ECG
bvp_file = "sinal_filtrado_patch_10.csv"  # Substitua pelo caminho do arquivo BVP


# Ler os dados do ECG
ecg_data = pd.read_csv(ecg_file)
ecg_data["Timestamp"] = (ecg_data["Timestamp"] - ecg_data["Timestamp"].iloc[0]) / 1000.0  # Converter milissegundos para segundos
ecg_time = ecg_data["Timestamp"]
ecg_signal = normalize(ecg_data["ECGValue"])

# Ler os dados do BVP
bvp_data = pd.read_csv(bvp_file)
bvp_time = bvp_data["Time (s)"]
bvp_signal = normalize(bvp_data["Filtered Signal"])

# Configurações iniciais para o gráfico
window_size = 10  # Tamanho da janela em segundos
start_time = 0  # Tempo inicial da visualização

# Função para atualizar o gráfico com base na posição do slider
def update(val):
    start = slider.val
    end = start + window_size
    ax.clear()
    # Filtrar os dados para o intervalo de tempo selecionado
    ecg_mask = (ecg_time >= start) & (ecg_time <= end)
    bvp_mask = (bvp_time >= start) & (bvp_time <= end)
    ax.plot(ecg_time[ecg_mask], ecg_signal[ecg_mask], label="ECG", color="blue", linewidth=2)
    ax.plot(bvp_time[bvp_mask], bvp_signal[bvp_mask], label="BVP", color="green", linewidth=2)
    ax.set_title("Comparação entre ECG e BVP", fontsize=14)
    ax.set_xlabel("Tempo (s)", fontsize=12)
    ax.set_ylabel("Amplitude Normalizada", fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True)
    fig.canvas.draw_idle()

# Configuração inicial da figura e do gráfico
fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)  # Ajustar espaço para o slider

# Adicionar o slider
ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])  # Posição do slider [esquerda, baixo, largura, altura]
slider = Slider(ax_slider, "Início (s)", 0, max(ecg_time.max(), bvp_time.max()) - window_size, valinit=start_time, valstep=0.1)

# Plot inicial
update(start_time)

# Vincular o slider à função de atualização
slider.on_changed(update)

# Mostrar o gráfico
plt.show()
