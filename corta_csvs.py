import os
import pandas as pd

# Dicionário com os índices de corte para cada vídeo
corte_dados = {
    "video_face_32": 125,
    "video_face_34": 118,
    "video_face_35": 139,
    "video_face_36": 174,
    "video_face_37": 150,
    "video_face_38": 148,
    "video_face_39": 139,
    "video_face_41": 128,
    "video_face_42": 121,
}

# Função para cortar os CSVs
def cortar_csv(diretorio_base, diretorio_saida):
    for video, indice_corte in corte_dados.items():
        video_dir = os.path.join(diretorio_base, video)
        metodo_dirs = [d for d in os.listdir(video_dir) if os.path.isdir(os.path.join(video_dir, d))]

        for metodo in metodo_dirs:
            metodo_dir = os.path.join(video_dir, metodo)
            patch_dirs = [d for d in os.listdir(metodo_dir) if os.path.isdir(os.path.join(metodo_dir, d))]

            for patch in patch_dirs:
                patch_dir = os.path.join(metodo_dir, patch)
                sinal_bruto_path = os.path.join(patch_dir, f"sinal_bruto_patch_{patch}.csv")
                sinal_filtrado_path = os.path.join(patch_dir, f"sinal_filtrado_patch_{patch}.csv")

                for sinal_path in [sinal_bruto_path, sinal_filtrado_path]:
                    if os.path.exists(sinal_path):
                        # Ler o CSV
                        df = pd.read_csv(sinal_path)
                        
                        # Cortar os dados a partir do índice
                        df_cortado = df.iloc[indice_corte:].copy()
                        
                        # Ajustar o tempo para começar em 0
                        df_cortado["Time (s)"] -= df_cortado["Time (s)"].iloc[0]
                        
                        # Criar o diretório de saída correspondente
                        saida_patch_dir = patch_dir.replace(diretorio_base, diretorio_saida)
                        os.makedirs(saida_patch_dir, exist_ok=True)
                        
                        # Salvar o CSV cortado
                        saida_path = os.path.join(saida_patch_dir, os.path.basename(sinal_path))
                        df_cortado.to_csv(saida_path, index=False)
                        print(f"Arquivo salvo: {saida_path}")

# Caminhos de entrada e saída
diretorio_base = "csv_outputs/Gustavo_sincronizacao"
diretorio_saida = "csv_outputs/Gustavo_sincronizacao_cortados"

# Cortar os arquivos CSV
if __name__ == "__main__":
    cortar_csv(diretorio_base, diretorio_saida)
