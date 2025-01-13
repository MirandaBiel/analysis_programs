import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Dados fornecidos
# Organizar em um dataframe
data = {
    "Group": ["G1"] * 11 + ["G2"] * 9 + ["G3"] * 22 + ["G4"] * 9,
    "Erro_BPM": [
        0.553489, 0.077071, 0.399708, 1.344602, 0.562776, 0.276335, 0.029701, 0.800403, 7.138121, 0.305029, 1.00396, 9.878783, 2.3327, 0.42192, 2.76318, 0.154729, 0.265027, 0.000187, 0.701844, 1.330309,
        0.979791, 1.395378, 0.039783, 0.302042, 0.368684, 0.653914, 1.0041, 0.587084, 0.5712, 0.519505, 0.512808,
        0.6478, 1.478314, 0.979129, 0.491855, 0.491252, 0.266336, 0.678883, 0.778583, 0.501043, 0.284173, 2.974061,
        0.402873, 0.266816, 0.185208, 0.119866, 0.362578, 0.867806, 0.045194, 0.109084, 1.551564
    ],
    "Erro_iRPM": [
        0.419612, 5.685912, 0.262258, 0.209806, 0.273973, 0.297483, 0.297483, 0.273973, 6.334471, 4.344828, 0.380623, 0.266361, 4.342857, 4.385321, 0.285714, 1.595376, 4.442396, 4.442396, 1.743119, 2.344828,
        9.790194, 0.409091, 1.580388, 7.726027, 0.382253, 0.570771, 7.790194, 5.595376, 3.614679, 9.799544, 7.743119,
        3.56701, 7.762014, 7.761092, 3.514451, 0.589862, 7.762014, 5.678899, 9.762014, 7.733639, 0.513761, 3.636364,
        2.015979, 5.098143, 0.26158, 6.719424, 3.355372, 6.096286, 3.78022, 2.535666, 5.251337
    ],
    "SQI1": [
        0.834841, 0.838353, 0.805147, 0.710042, 0.708821, 0.815558, 0.786159, 0.782306, 0.706741, 0.752931, 0.668625, 0.631162, 0.631977, 0.759821, 0.764515, 0.832172, 0.777544, 0.825765, 0.832266, 0.789796,
        0.845774, 0.875863, 0.849046, 0.850434, 0.85254, 0.85827, 0.861447, 0.870529, 0.85903, 0.847721, 0.871547,
        0.861463, 0.855576, 0.854149, 0.845787, 0.847007, 0.853077, 0.859076, 0.847772, 0.818235, 0.829551, 0.815197,
        0.793201, 0.855734, 0.809723, 0.811737, 0.726788, 0.831125, 0.782709, 0.835791, 0.780282
    ]
}

data_df = pd.DataFrame(data)

# Ordenar os dados pelo SQI1
data_df = data_df.sort_values(by="SQI1", ascending=True).reset_index(drop=True)

# Listas para armazenar resultados
thresholds = []
mean_error_bpm = []
mean_error_irpm = []
num_videos = []

# Calcular erro médio conforme o limiar de SQI1 aumenta
for threshold in np.linspace(data_df["SQI1"].min(), data_df["SQI1"].max(), 100):
    filtered_data = data_df[data_df["SQI1"] >= threshold]
    if len(filtered_data) > 0:
        thresholds.append(threshold)
        mean_error_bpm.append(filtered_data["Erro_BPM"].mean())
        mean_error_irpm.append(filtered_data["Erro_iRPM"].mean())
        num_videos.append(len(filtered_data))

# Exibir valores numéricos
results_df = pd.DataFrame({
    "Threshold_SQI1": thresholds,
    "Mean_Error_BPM": mean_error_bpm,
    "Mean_Error_iRPM": mean_error_irpm,
    "Num_Videos": num_videos
})

print("Resultados numéricos:")
print(results_df)

# Gráficos
plt.figure(figsize=(14, 7))

# Gráfico para erro BPM
plt.subplot(1, 2, 1)
plt.plot(thresholds, mean_error_bpm, color="blue")
plt.xlabel("Limiar SQI1")
plt.ylabel("Erro Absoluto Médio (bpm)")
plt.title("")
#plt.xlim(0.6, 0.83)  # Limite do eixo X
plt.grid(True)
plt.legend()

# Gráfico para erro iRPM
plt.subplot(1, 2, 2)
plt.plot(thresholds, mean_error_irpm, label="Erro Médio iRPM", color="green")
plt.xlabel("Limiar SQI1")
plt.ylabel("Erro Médio iRPM")
plt.title("")
#plt.xlim(0.6, 0.83)  # Limite do eixo X
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
