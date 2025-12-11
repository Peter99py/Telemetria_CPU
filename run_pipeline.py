# Objetivo: Orquestrar o fluxo ETL:

import src.etl.pipeline as pipeline
from src.models import ensure_sqlite_database_and_table

print("---Iniciando aplicação ---")

def main():
    try:
        # Garante a estrutura do banco de dados
        ensure_sqlite_database_and_table()

        print('\n--- Executando pipeline ---') 
    
        # Executa todo o ciclo (Extract -> Transform -> Load -> Archive)
        pipeline.run_etl() 

        print("\nCiclo ETL concluído com sucesso.")
        input("\nPressione Enter para sair...") 

    except Exception as e:
        print(f"!!! ERRO fatal durante a execução: {e}")
        input("Pressione Enter para sair.")

if __name__ == "__main__":
    main()
