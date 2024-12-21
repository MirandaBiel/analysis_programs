import matplotlib.pyplot as plt
import csv
import os

def process_and_save_csv_graphs(input_dir, output_dir):
    """
    Lê arquivos CSV em uma estrutura de pastas, gera gráficos e os salva em pastas separadas.
    As pastas são organizadas por tipo de gráfico: sinal bruto, sinal filtrado e espectro de frequência.

    Parâmetros:
    - input_dir: Diretório raiz onde os arquivos CSV estão armazenados.
    - output_dir: Diretório raiz onde os gráficos serão organizados.
    """
    # Define as pastas de saída
    raw_signal_dir = os.path.join(output_dir, "sinal_bruto")
    filtered_signal_dir = os.path.join(output_dir, "sinal_filtrado")
    frequency_spectrum_dir = os.path.join(output_dir, "espectro_frequencia")

    # Cria as pastas, se não existirem
    os.makedirs(raw_signal_dir, exist_ok=True)
    os.makedirs(filtered_signal_dir, exist_ok=True)
    os.makedirs(frequency_spectrum_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_path = os.path.join(root, file)
                
                # Extrai informações do caminho e do nome do arquivo
                relative_path = os.path.relpath(csv_path, input_dir)  # Caminho relativo do arquivo
                path_parts = relative_path.split(os.sep)
                
                video_name = path_parts[0] if len(path_parts) > 0 else "UnknownVideo"
                method = path_parts[1] if len(path_parts) > 1 else "UnknownMethod"
                patch = path_parts[2] if len(path_parts) > 2 else "UnknownPatch"
                signal_type = os.path.splitext(file)[0]  # Nome do arquivo sem extensão

                # Lê o cabeçalho para identificar o tipo do gráfico
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.reader(csv_file)
                    headers = next(reader)  # Lê o cabeçalho
                    
                    if headers == ["Time (s)", "Raw Signal"]:
                        graph_type = "sinal_bruto"
                        x_label, y_label, title_label = "Tempo (s)", "Amplitude", "Sinal Bruto"
                        save_dir = raw_signal_dir
                    elif headers == ["Time (s)", "Filtered Signal"]:
                        graph_type = "sinal_filtrado"
                        x_label, y_label, title_label = "Tempo (s)", "Amplitude", "Sinal Filtrado"
                        save_dir = filtered_signal_dir
                    elif headers == ["Frequency (Hz)", "Amplitude"]:
                        graph_type = "espectro_frequencia"
                        x_label, y_label, title_label = "Frequência (Hz)", "Amplitude", "Espectro de Frequência"
                        save_dir = frequency_spectrum_dir
                    else:
                        print(f"Arquivo ignorado (formato desconhecido): {csv_path}")
                        continue

                # Lê os dados do arquivo CSV
                x_values, y_values = [], []
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader)  # Pula o cabeçalho
                    for row in reader:
                        try:
                            x_values.append(float(row[0]))
                            y_values.append(float(row[1]))
                        except ValueError:
                            print(f"Erro ao processar linha: {row}")
                            continue

                # Tratamento especial para o espectro de frequência: Filtra o eixo x entre 20 e 200 Hz
                if graph_type == "espectro_frequencia":
                    filtered_x = []
                    filtered_y = []
                    for x, y in zip(x_values, y_values):
                        if 20 <= x <= 200:  # Mantém apenas as frequências entre 20 e 200 Hz
                            filtered_x.append(x)
                            filtered_y.append(y)
                    x_values = filtered_x
                    y_values = filtered_y

                # Plota o gráfico
                plt.figure(figsize=(10, 6))
                plt.plot(x_values, y_values, color='b', label=title_label)
                plt.title(f"{title_label} - {video_name} - {method} - {patch}")
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                plt.legend()
                plt.grid(True)

                # Gera o nome do gráfico e o caminho de salvamento
                graph_name = f"{video_name}_{method}_{patch}_{graph_type}.png"
                save_path = os.path.join(save_dir, graph_name)

                # Salva o gráfico
                plt.savefig(save_path)
                print(f"Gráfico salvo: {save_path}")
                plt.close()

if __name__ == "__main__":
    # Diretórios de entrada e saída
    input_dir = input("Digite o diretório raiz dos arquivos CSV: ").strip()
    output_dir = input("Digite o diretório onde os gráficos serão organizados: ").strip()

    # Processa os arquivos e salva os gráficos
    process_and_save_csv_graphs(input_dir, output_dir)
