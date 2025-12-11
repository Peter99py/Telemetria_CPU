import pandas as pd
import os
import shutil
import re
from config import RAW_DIR, LOADED_RAW_DIR, LOADED_PROCESSED_DIR
from src.database import Session
from src.etl.load import insert_dataframe

# Garante que diretórios-alvo existam
os.makedirs(LOADED_RAW_DIR, exist_ok=True)
os.makedirs(LOADED_PROCESSED_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def process_file_to_df(file_path):
    """Lê e processa um arquivo CSV, retornando um DataFrame limpo."""
    
    datetime_sniffer = pd.read_csv(file_path, encoding="latin1", nrows=0).columns.tolist()
    first_value = datetime_sniffer[0]
    time_pattern = r'^\d{2}:\d{2}:\d{2}'
    data = None

    if re.match(time_pattern, first_value):
        data = pd.read_csv(file_path, encoding="latin1", header=None)
        data = data.dropna(axis=1, how='all')
        data = data.dropna(axis=0, how='all')
        
        cols = ['Time', 'Core 0 Temp. (°)', 'Core 1 Temp. (°)', 'Core 2 Temp. (°)',
                'Core 3 Temp. (°)', 'Core 4 Temp. (°)', 'Core 5 Temp. (°)',
                'Low temp. (°)', 'High temp. (°)', 'Core load (%)', 'Core speed (MHz)',
                'Low temp. (°).1', 'High temp. (°).1', 'Core load (%).1',
                'Core speed (MHz).1', 'Low temp. (°).2', 'High temp. (°).2',
                'Core load (%).2', 'Core speed (MHz).2', 'Low temp. (°).3',
                'High temp. (°).3', 'Core load (%).3', 'Core speed (MHz).3',
                'Low temp. (°).4', 'High temp. (°).4', 'Core load (%).4',
                'Core speed (MHz).4', 'Low temp. (°).5', 'High temp. (°).5',
                'Core load (%).5', 'Core speed (MHz).5', 'CPU 0 Power']
        
        # Ajuste preventivo para mismatch de colunas
        if data.shape[1] == len(cols):
            data.columns = cols
        else:
             # Tenta atribuir mesmo assim, ou ajusta o slicing
             data.columns = cols[:data.shape[1]]

    else:
        data = pd.read_csv(file_path, encoding="latin1", skiprows=7)
        data = data.dropna(axis=1, how='all')
        data = data.dropna(axis=0, how='all')

    initial_rows = len(data)
    print(f"   -> Linhas lidas: {initial_rows}")

    data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S %m/%d/%y", errors="coerce")
    data = data.dropna(subset=["Time"]) 

    # Seleção e Renomeação
    columns_to_keep = [
            'Time',
            'Core 0 Temp. (°)', 'Core load (%)', 'Core speed (MHz)',
            'Core 1 Temp. (°)', 'Core load (%).1', 'Core speed (MHz).1',
            'Core 2 Temp. (°)', 'Core load (%).2', 'Core speed (MHz).2',
            'Core 3 Temp. (°)', 'Core load (%).3', 'Core speed (MHz).3',
            'Core 4 Temp. (°)', 'Core load (%).4', 'Core speed (MHz).4',
            'Core 5 Temp. (°)', 'Core load (%).5', 'Core speed (MHz).5',
            'CPU 0 Power'
    ]
    
    # Filtra colunas existentes
    valid_cols = [c for c in columns_to_keep if c in data.columns]
    data = data[valid_cols]

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
    print(f"   -> Linhas após limpeza: {final_rows}")
    
    return data


def run_etl():
    print("\n--- Iniciando Pipeline de Dados (Memória -> Banco -> Arquivo) ---")

    if not os.path.exists(RAW_DIR):
         print(f"Diretório {RAW_DIR} não encontrado.")
         return

    files_to_process = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]

    if not files_to_process:
        print(f"\nNenhum arquivo .csv encontrado na pasta '{RAW_DIR}'.")
        return

    print(f"Encontrados {len(files_to_process)} arquivos para processar.")
    
    # Lista de ações para efetivar no final (File Moves)
    file_moves = [] # (origem, destino)

    with Session() as session:
        try:
            for file_name in files_to_process:
                source_path = os.path.join(RAW_DIR, file_name)
                loaded_raw_path = os.path.join(LOADED_RAW_DIR, file_name)
                loaded_processed_path = os.path.join(LOADED_PROCESSED_DIR, file_name)
                
                print(f"\n--- Processando: {file_name} ---")
                
                # 1. Processamento em Memória
                df = process_file_to_df(source_path)
                
                # 2. Inserção no Banco (Transacional)
                insert_dataframe(session, df)
                print("   -> Dados inseridos na sessão do banco.")
                
                # 3. Salvar CSV Processado (Arquivo)
                df.to_csv(loaded_processed_path, index=False)
                print(f"   -> CSV processado salvo em: {loaded_processed_path}")
                
                # Adiciona à lista de movimentos para executar APÓS commit
                file_moves.append((source_path, loaded_raw_path))

            # Commit da transação
            session.commit()
            print("\n--- Transação concluída com sucesso no Banco de Dados! ---")
            
            # 4. Mover arquivos originais (apenas se DB commitou)
            for src, dst in file_moves:
                shutil.move(src, dst)
                print(f"Arquivo original movido para: {dst}")

        except Exception as e:
            session.rollback()
            print(f"\n!!! ERRO FATAL no Pipeline: {e}")
            print("!!! Rollback executado. Nenhuma alteração no banco foi salva.")
            # Arquivos não são movidos, CSVs processados podem ter sido criados mas serão sobrescritos na próxima ou podem ser limpos manualmente se crítico.
            # Como loaded_processed não é transacional (sistema de arquivos), eles ficam lá. 
            # Idealmente limparíamos os arquivos criados nessa run em caso de erro, mas para simplicidade vamos manter assim.
            raise e

    print("\n--- Ciclo ETL finalizado! ---")
