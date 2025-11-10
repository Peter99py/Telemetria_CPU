# Objetivo: Orquestrar o fluxo ETL:

import os 
import src.scripts.pipeline as pipeline
import src.scripts.load as load

print("---Iniciando aplicação ---")

def files():
    # Garante que as pastas usadas pelo processo existam
    files = ["data/loaded_processed", "data/loaded_raw", "data/processed", "data/raw"]
    for arquivos in files:
        if not os.path.exists(arquivos):  
            os.makedirs(arquivos) 
            print(f'Pasta {arquivos} criada com sucesso!')
        else:
            print(f'Pasta {arquivos} OK!')
    main()  


def main():

    load.ensure_sqlite_database_and_table()

    print('\n--- Executando pipeline ---')
    input("\nPressione Enter para iniciar o processo de ETL.") 
    pipeline.pipeline() 

    input("\nPressione Enter para subir os arquivos para o banco de dados.")
    load.load_data_to_db() 

    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    files()
