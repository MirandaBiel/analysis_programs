import pandas as pd

# Caminho do arquivo de entrada e saída
bvp_input_file = "sinal_filtrado_patch_10.csv"  # Substitua pelo caminho do arquivo BVP original
bvp_output_file = "sinal_filtrado_patch_10_invertido.csv"  # Caminho para salvar o arquivo modificado

# Ler os dados do BVP
bvp_data = pd.read_csv(bvp_input_file)

# Inverter os valores de amplitude
bvp_data["Filtered Signal"] = -1 * bvp_data["Filtered Signal"]

# Salvar os dados modificados em um novo arquivo CSV
bvp_data.to_csv(bvp_output_file, index=False)

print(f"Arquivo com os valores invertidos salvo em: {bvp_output_file}")
