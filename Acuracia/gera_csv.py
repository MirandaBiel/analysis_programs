import process_functions as pf
import irpm_calc as pressure
import signal_quality as sq
import numpy as np
import ecg_calc
import csv
import os

def registrar_dados_csv(metodo, patch, ppg_bpm, ecg_bpm, ppg_irpm, pre_irpm, video_numero, fs, sec, sqi1, sqi2, nome_participante):
    """
    Registra os valores fornecidos em um arquivo CSV em uma estrutura de pastas específica.

    Parâmetros:
        metodo (str): Método utilizado.
        patch (str): Identificação do patch.
        ppg_bpm (float): Batimentos por minuto obtidos via PPG.
        ecg_bpm (float): Batimentos por minuto obtidos via ECG.
        ppg_irpm (float): Respirações por minuto estimadas via PPG.
        pre_irpm (float): Respirações por minuto estimadas via PRE.
        nome_participante (str): Nome do participante.
        video_numero (int): Número do vídeo sendo analisado.
        fs (float): FS do vídeo sendo analisado.
        sec (float): Tempo em segundos desde o início do vídeo.
    """
    # Construir o caminho do arquivo
    pasta_destino = os.path.join("csv_outputs", nome_participante)
    arquivo_csv = os.path.join(pasta_destino, f"video_{video_numero}_resultados.csv")

    # Criar os diretórios, se não existirem
    os.makedirs(pasta_destino, exist_ok=True)

    # Definir os headers do CSV
    headers = ["Metodo", "Patch", "PPG_BPM", "ECG_BPM", "PPG_iRPM", "PRE_iRPM", "FS", "Tempo", "SQI1", "SQI2"]

    # Verificar se o arquivo já existe
    try:
        arquivo_existe = False
        with open(arquivo_csv, mode='r', newline='', encoding='utf-8') as arquivo:
            arquivo_existe = True
    except FileNotFoundError:
        pass

    # Abrir o arquivo em modo append para adicionar a linha
    with open(arquivo_csv, mode='a', newline='', encoding='utf-8') as arquivo:
        escritor_csv = csv.writer(arquivo)

        # Escrever os headers se o arquivo não existia
        if not arquivo_existe:
            escritor_csv.writerow(headers)

        # Escrever os valores na linha
        escritor_csv.writerow([metodo, patch, ppg_bpm, ecg_bpm, ppg_irpm, pre_irpm, fs, sec, sqi1, sqi2])


def ecg_pre_aquisition(ecg_folder, pre_folder, numbers):
    # Cria o padrão do nome do arquivo a partir de `numbers`
    file_pattern = f"{numbers[0]}_{numbers[1]}.csv"
    found = False

    # Ler os dados do ECG
    for root, dirs, files in os.walk(ecg_folder):
        for file in files:
            # Verifica se o arquivo termina com o padrão esperado
            if file.endswith(file_pattern):
                # Caminho completo do arquivo encontrado
                file_path = os.path.join(root, file)
                ecg_bpm = ecg_calc.calc_bpm(file_path, int(numbers[1].split('-')[1]))
                found = True
                break
        if found:
            break
    
    found = False
    # Ler os dados da pressão
    for root, dirs, files in os.walk(pre_folder):
        for file in files:
            # Verifica se o arquivo termina com o padrão esperado
            if file.endswith(file_pattern):
                # Caminho completo do arquivo encontrado
                file_path = os.path.join(root, file)
                pre_irpm = pressure.calc_irpm(file_path, int(numbers[1].split('-')[1]))
                found = True
                break
        if found:
            break

    return ecg_bpm, pre_irpm


def process_patch(base_folder, ecg_folder, pre_folder):
    # Verifica se o caminho inicial é uma pasta
    if os.path.exists(base_folder):
    # Lista todas as pastas dos metodos no diretório base
        for video_name in os.listdir(base_folder):
            for method_name in os.listdir(os.path.join(base_folder, video_name)):
                # Lista todos os patchs
                for pacth_name in os.listdir(os.path.join(base_folder, video_name, method_name)):
                    # Filtra pastas que começam com "patch_"
                    if pacth_name.startswith("patch_"):
                        try:
                            # Extrai o número x após "patch_"
                            pacth_number = int(pacth_name.split("_")[1])
                            
                            #========== Extrai os dados do CSV ===========#
                            patch_folder_path = os.path.join(base_folder, video_name, method_name, pacth_name)
                            spectrum_path = os.path.join(patch_folder_path, f"espectro_frequencia_patch_{pacth_number}.csv")
                            raw_signal_path = os.path.join(patch_folder_path, f"sinal_bruto_patch_{pacth_number}.csv")
                            filtered_signal_path = os.path.join(patch_folder_path, f"sinal_filtrado_patch_{pacth_number}.csv")

                            spectrum_data = []
                            freq_data = []
                            raw_signal_data = []
                            time = []
                            filtered_data = []

                            # Lê os dados do espectro da frequencia
                            if os.path.exists(spectrum_path):
                                with open(spectrum_path, mode='r') as spectrum_file:
                                    reader = csv.DictReader(spectrum_file)
                                    for row in reader:
                                        spectrum_data.append(float(row["Amplitude"]))
                                        freq_data.append(float(row["Frequency (Hz)"]))
                            else:
                                print(f"Arquivo {spectrum_path} não encontrado na pasta {pacth_name}.")

                            # Lê os dados do sinal bruto
                            if os.path.exists(raw_signal_path):
                                with open(raw_signal_path, 'r') as signal_file:
                                    reader = csv.DictReader(signal_file)
                                    for row in reader:
                                        raw_signal_data.append(float(row["Raw Signal"]))
                                        time.append(float(row["Time (s)"]))
                            else:
                                print(f"Arquivo {raw_signal_path} não encontrado na pasta {pacth_name}.")

                            # Lê os dados do sinal filtrado
                            if os.path.exists(filtered_signal_path):
                                with open(filtered_signal_path, 'r') as signal_file:
                                    reader = csv.DictReader(signal_file)
                                    for row in reader:
                                        filtered_data.append(float(row["Filtered Signal"]))
                            else:
                                print(f"Arquivo {raw_signal_path} não encontrado na pasta {pacth_name}.")

                            #============= Calcula FC e FR ==============#
                            fs = len(raw_signal_data) / time[-1]
                            ppg_bpm = pf.calc_frequencia_cardiaca(np.array(spectrum_data), np.array(freq_data))
                            ppg_irpm = pf.calc_frequencia_respiratoria(raw_signal_data, fs)

                            #============= Calculo com Pressao e ECG ==============#
                            # Extrai o nome da última pasta no caminho
                            folder_name = os.path.basename(video_name)

                            # Divide o nome pelo caractere '_'
                            parts = folder_name.split("_")

                            # Extrai os números
                            numbers = [parts[-2], parts[-1].split(".")[0]]  # Terceiro de trás para frente
                            ecg_bpm, pre_irpm = ecg_pre_aquisition(ecg_folder, pre_folder, numbers)
                            sec = numbers[1].split('-')[1]
                            video_number = int(numbers[0])

                            #============= Calculo dos SQIs ==============#
                            sqi1 = pf.analyze_signal_spectrum(np.array(spectrum_data), np.array(freq_data))
                            #sqis = sq.PPG_analysis(signal_hf, fs, 5)['LSQI']
                            sqi2 = sq.PPG_analysis(filtered_data, fs, 5)['LSQI']


                            print(f"Analise video {int(numbers[0])}/{method_name}/patch_{pacth_number}:") 
                            print(f"irpm: {round(ppg_irpm, 4)}, {round(pre_irpm, 4)}, bpm: {round(ppg_bpm, 4)}, {round(ecg_bpm, 4)}, SQI1: {round(sqi1, 4)}, SQI2: {sqi2}")
                            
                            
                            #============= Registra os dados no CSV ==============#                        
                            registrar_dados_csv(
                                method_name,
                                pacth_number,
                                round(ppg_bpm, 4),
                                round(ecg_bpm, 4),
                                round(ppg_irpm, 4),
                                round(pre_irpm, 4),
                                video_number,
                                fs,
                                sec,
                                sqi1,
                                sqi2,
                                "Gustavo"
                            )

                        except (IndexError, ValueError):
                            print(f"Pasta {pacth_name} não segue o padrão esperado.")
        else:
            print(f"Caminho {base_folder} não encontrado.")


if __name__ == '__main__':
    # Caminho da pasta dos dados brutos
    csv_folder = "csv_outputs/17-12-2024/Gustavo"
    ecg_folder = "ECGs/Gustavo/17-12-2024"
    pre_folder = "Pressure/Gustavo/17-12-2024"
    process_patch(csv_folder, ecg_folder, pre_folder)

    
