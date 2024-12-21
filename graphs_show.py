import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_csv_files_in_patches(base_folder):
    try:
        # Verificar se a pasta base existe
        if not os.path.exists(base_folder):
            print(f"Erro: Pasta '{base_folder}' não encontrada.")
            return

        # Listar todas as subpastas dentro da pasta base
        patch_folders = [os.path.join(base_folder, d) for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]

        # Iterar sobre cada pasta "patch_x"
        for patch_folder in patch_folders:
            patch_name = os.path.basename(patch_folder)
            print(f"Processando: {patch_name}")

            # Caminhos para os arquivos CSV
            raw_signal_file = os.path.join(patch_folder, f"sinal_bruto_{patch_name}.csv")
            filtered_signal_file = os.path.join(patch_folder, f"sinal_filtrado_{patch_name}.csv")
            frequency_spectrum_file = os.path.join(patch_folder, f"espectro_frequencia_{patch_name}.csv")

            # Verificar se os arquivos existem
            if not all(os.path.exists(file) for file in [raw_signal_file, filtered_signal_file, frequency_spectrum_file]):
                print(f"Arquivos CSV ausentes em {patch_name}. Pulando...")
                continue

            # Ler os arquivos CSV
            raw_signal_data = pd.read_csv(raw_signal_file)
            filtered_signal_data = pd.read_csv(filtered_signal_file)
            frequency_spectrum_data = pd.read_csv(frequency_spectrum_file)

            # Criar o gráfico
            fig, axes = plt.subplots(2, 1, figsize=(10, 12), sharex=False)

            # Gráfico do sinal bruto
            axes[0].plot(raw_signal_data["Time (s)"], raw_signal_data["Raw Signal"], color="blue", label="Sinal Bruto")
            axes[0].set_title(f"Sinal Bruto - {patch_name}")
            axes[0].set_xlabel("Tempo (s)")
            axes[0].set_ylabel("Amplitude")
            axes[0].grid(True)
            axes[0].legend()

            # Gráfico do sinal filtrado
            axes[1].plot(filtered_signal_data["Time (s)"], filtered_signal_data["Filtered Signal"], color="green", label="Sinal Filtrado")
            axes[1].set_title(f"Sinal Filtrado - {patch_name}")
            axes[1].set_xlabel("Tempo (s)")
            axes[1].set_ylabel("Amplitude")
            axes[1].grid(True)
            axes[1].legend()

            # Gráfico do espectro de frequência
            # axes[2].plot(frequency_spectrum_data["Frequency (Hz)"], frequency_spectrum_data["Amplitude"], color="red", label="Espectro de Frequência")
            # axes[2].set_title(f"Espectro de Frequência - {patch_name}")
            # axes[2].set_xlabel("Frequência (Hz)")
            # axes[2].set_ylabel("Amplitude")
            # axes[2].grid(True)
            # axes[2].legend()

            # Ajustar o layout
            plt.tight_layout()

            # Mostrar o gráfico
            plt.show()

    except Exception as e:
        print(f"Erro: {e}")

# Caminho base para os arquivos CSV
base_folder = r"csv_outputs\\16-12-2024-gustavo_2.h264\\CHROM"

# Executar o programa
plot_csv_files_in_patches(base_folder)
