# Objetivo: Executar o ETL dos CSVs brutos localizados em data/raw:
#   - Ler e preparar os dados (limpeza, seleção e renomeação de colunas)
#   - Salvar CSVs processados em data/processed
#   - Mover os arquivos brutos para data/loaded_raw após sucesso

import pandas as pd
import os
import shutil
import re
import sys

# Pastas de entrada/saída do processo
raw_data_path = "data/raw"
loaded_data_path = "data/loaded_raw"
processed_data_path = "data/processed"

# Garante que diretórios-alvo existam
os.makedirs(loaded_data_path, exist_ok=True)
os.makedirs(processed_data_path, exist_ok=True)
        

# Processa um arquivo CSV individualmente
def process_file(file_path, output_path):
    
    print(f"\nLendo o arquivo: {os.path.basename(file_path)}")

    datetime_sniffer = pd.read_csv(file_path, encoding="latin1", nrows=0).columns.tolist()

    first_value = datetime_sniffer[0]

    time_pattern = r'^\d{2}:\d{2}:\d{2}'

    data = None

    if re.match(time_pattern, first_value):
        data = pd.read_csv(file_path, encoding="latin1", header=None)
        data = data.dropna(axis=1, how='all')
        data = data.dropna(axis=0, how='all')
        data.columns =  ['Time', 'Core 0 Temp. (°)', 'Core 1 Temp. (°)', 'Core 2 Temp. (°)',
                        'Core 3 Temp. (°)', 'Core 4 Temp. (°)', 'Core 5 Temp. (°)',
                        'Low temp. (°)', 'High temp. (°)', 'Core load (%)', 'Core speed (MHz)',
                        'Low temp. (°).1', 'High temp. (°).1', 'Core load (%).1',
                        'Core speed (MHz).1', 'Low temp. (°).2', 'High temp. (°).2',
                        'Core load (%).2', 'Core speed (MHz).2', 'Low temp. (°).3',
                        'High temp. (°).3', 'Core load (%).3', 'Core speed (MHz).3',
                        'Low temp. (°).4', 'High temp. (°).4', 'Core load (%).4',
                        'Core speed (MHz).4', 'Low temp. (°).5', 'High temp. (°).5',
                        'Core load (%).5', 'Core speed (MHz).5', 'CPU 0 Power']

    else:
        data = pd.read_csv(file_path, encoding="latin1", skiprows=7)
        data = data.dropna(axis=1, how='all')
        data = data.dropna(axis=0, how='all')

    initial_rows = len(data)
    print(f"\nQtd. linhas antes do processamento: {initial_rows}")

    data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S %m/%d/%y", errors="coerce")
    data = data.dropna(subset=["Time"])


    # Mapeia nomes originais para nomes padronizados em snake_case
    
    try:
        # Reordena um conjunto específico de colunas
        data = data[['Time',
                     'Core 0 Temp. (°)', 'Core load (%)', 'Core speed (MHz)',
                     'Core 1 Temp. (°)', 'Core load (%).1', 'Core speed (MHz).1',
                     'Core 2 Temp. (°)', 'Core load (%).2', 'Core speed (MHz).2',
                     'Core 3 Temp. (°)', 'Core load (%).3', 'Core speed (MHz).3',
                     'Core 4 Temp. (°)', 'Core load (%).4', 'Core speed (MHz).4',
                     'Core 5 Temp. (°)', 'Core load (%).5', 'Core speed (MHz).5',
                     'CPU 0 Power']]
    except KeyError as e:
        # Se o layout variar e alguma coluna faltar, apenas informa e segue com o que existir
        print(f" Aviso: Coluna não encontrada durante a reordenação: {e}. O arquivo pode ter um formato diferente.")
        input("Pressione Enter para sair.")
        sys.exit()

    rename_columns = {
        "Time": "time",
        "Core 0 Temp. (°)": "core_temp_0", "Core load (%)": "core_load_0", "Core speed (MHz)": "core_speed_0",
        "Core 1 Temp. (°)": "core_temp_1", "Core load (%).1": "core_load_1", "Core speed (MHz).1": "core_speed_1",
        "Core 2 Temp. (°)": "core_temp_2", "Core load (%).2": "core_load_2", "Core speed (MHz).2": "core_speed_2",
        "Core 3 Temp. (°)": "core_temp_3", "Core load (%).3": "core_load_3", "Core speed (MHz).3": "core_speed_3",
        "Core 4 Temp. (°)": "core_temp_4", "Core load (%).4": "core_load_4", "Core speed (MHz).4": "core_speed_4",
        "Core 5 Temp. (°)": "core_temp_5", "Core load (%).5": "core_load_5", "Core speed (MHz).5": "core_speed_5",
        "CPU 0 Power": "cpu_power"
    }
    data.rename(columns=rename_columns, inplace=True)

    final_rows = len(data)
    print(f"\nLinhas após o processamento: {final_rows} (removidas {initial_rows - final_rows} linhas)")

    # Salva o CSV processado sem índice
    data.to_csv(output_path, index=False)
    print(f"\nArquivo processado e salvo em: {output_path}")


def pipeline():
    # Orquestra o processamento de todos os arquivos em data/raw
    print("\n--- Iniciando o processo de ETL para os arquivos CSV ---")

    # Coleta apenas arquivos .csv na pasta de origem
    files_to_process = [f for f in os.listdir(raw_data_path) if f.endswith('.csv')]

    # Encerra antes se não houver o que processar
    if not files_to_process:
        print("\nNenhum arquivo .csv encontrado na pasta 'data/raw'.")
        return

    print(f"Encontrados {len(files_to_process)} arquivos para processar.")

    # Processa cada arquivo individualmente
    for file_name in files_to_process:
        source_file_path = os.path.join(raw_data_path, file_name)               # caminho do arquivo bruto
        destination_file_path = os.path.join(loaded_data_path, file_name)       # destino do bruto após sucesso
        output_file_path = os.path.join(processed_data_path, file_name)         # saída do CSV processado
        print(f"\n--- Processando: {file_name} ---")
        try:
            # Processa e grava o CSV
            process_file(source_file_path, output_file_path)

            # Move o arquivo original para loaded_raw apenas após processamento bem-sucedido
            shutil.move(source_file_path, destination_file_path)
            print(f"Arquivo original movido para: {destination_file_path}")

        except Exception as e:
            # Em caso de erro, reporta e encerra o pipeline
            print(f"!!! ERRO ao processar o arquivo {file_name}: {e}")
            print("!!! O arquivo não será movido.")
            return  # encerra o pipeline na primeira falha

    # Conclusão do processo (executa somente se todos os arquivos forem processados sem erros)
    print("\n--- Processo finalizado! ---")