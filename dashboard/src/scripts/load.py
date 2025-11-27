# Objetivo: Carregar arquivos CSV da pasta data/processed para uma tabela no SQLite, de forma transacional.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, Table, Column, Integer, Float, DateTime, MetaData
import pandas as pd
import os
import shutil


# Configuração de conexão com o banco
db_path = "dashboard/src/queries/data.db"
nome_tabela = "raw_data"

# Pastas de trabalho
data_processed_path = "data/processed"  # origem dos CSVs prontos para carga
data_loaded_processed_path = "data/loaded_processed"  # destino pós-sucesso

# Garante que a pasta de destino exista
os.makedirs(data_loaded_processed_path, exist_ok=True)

def ensure_sqlite_database_and_table():
    # Verifica se o arquivo SQLite existe e se a tabela está criada
    if not os.path.exists(db_path):
        print(f"Arquivo de banco SQLite não encontrado. Será criado: {db_path}")

    metadata = MetaData()
    insp = inspect(engine)

    if not insp.has_table(nome_tabela):
        print(f"Tabela '{nome_tabela}' não encontrada. Criando estrutura padrão...")
        Table(
            nome_tabela,
            metadata,
            Column('time', DateTime),
            Column('core_temp_0', Integer),
            Column('low_temp_0', Integer),
            Column('high_temp_0', Integer),
            Column('core_load_0', Float),
            Column('core_speed_0', Float),

            Column('core_temp_1', Integer),
            Column('low_temp_1', Integer),
            Column('high_temp_1', Integer),
            Column('core_load_1', Float),
            Column('core_speed_1', Float),

            Column('core_temp_2', Integer),
            Column('low_temp_2', Integer),
            Column('high_temp_2', Integer),
            Column('core_load_2', Float),
            Column('core_speed_2', Float),

            Column('core_temp_3', Integer),
            Column('low_temp_3', Integer),
            Column('high_temp_3', Integer),
            Column('core_load_3', Float),
            Column('core_speed_3', Float),

            Column('core_temp_4', Integer),
            Column('low_temp_4', Integer),
            Column('high_temp_4', Integer),
            Column('core_load_4', Float),
            Column('core_speed_4', Float),

            Column('core_temp_5', Integer),
            Column('low_temp_5', Integer),
            Column('high_temp_5', Integer),
            Column('core_load_5', Float),
            Column('core_speed_5', Float),

            Column('cpu_power', Float)
        )
        metadata.create_all(engine)
        print(f"Tabela '{nome_tabela}' criada com sucesso.")


def get_engine():

    url = f"sqlite:///{db_path}"

    return create_engine(url)

# Recursos globais de conexão e configuração
engine = get_engine()
Session = sessionmaker(bind=engine)


def load_data_to_db():
    # Carrega todos os CSVs de data/processed para o SQLite de forma transacional. 
    # Em caso de sucesso, move cada arquivo para data/loaded_processed.
    # Em caso de erro em qualquer arquivo, faz rollback e não move nenhum arquivo.

    print("\n--- Iniciando o processo de carregamento de dados para o SQLite... ---")

    # Coleta apenas arquivos .csv na pasta de processados
    files_to_load = [f for f in os.listdir(data_processed_path) if f.endswith('.csv')]

    # Se não houver arquivos, encerra.
    if not files_to_load:
        print("\nNenhum arquivo .csv encontrado na pasta 'data/processed'.")
        raise

    print(f"\nEncontrados {len(files_to_load)} arquivos para carregar.")

    # Contador agregado de linhas carregadas.
    total_rows_processed = 0

    # Abre uma sessão transacional
    with Session() as session:
        successfully_processed_file_paths = []  # manterá (origem, destino) para mover após commit
        try:
            # Itera sobre cada arquivo a ser carregado
            for file_name in files_to_load:
                file_path = os.path.join(data_processed_path, file_name)  # caminho completo de origem
                destination_file_path = os.path.join(data_loaded_processed_path, file_name)  # destino
                print(f"\n--- Processando e Carregando: {file_name} ---")

                try:
                    # Lê o CSV; 'parse_dates' converte a coluna 'time' para datetime
                    dados = pd.read_csv(file_path, parse_dates=['time'])  # type: ignore
                    dados['time'] = dados['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    dados['time'] = dados['time'].astype(str)

                    # Número de linhas do arquivo atual
                    num_rows = len(dados)

                    # Insere em modo append na tabela alvo dentro da transação da sessão
                    dados.to_sql(
                        nome_tabela,
                        session.connection(),
                        if_exists='append',
                        index=False
                    )

                    print(f"\nDados do arquivo '{file_name}' adicionados à transação do banco de dados.")

                    # Registra o par (origem, destino) para mover apenas se tudo der certo
                    successfully_processed_file_paths.append((file_path, destination_file_path))  # type: ignore
                    # Atualiza contadores e logs
                    total_rows_processed += num_rows
                    print(f"Total de linhas processadas deste arquivo: {num_rows}")
                    print(f"Total de linhas processadas até agora: {total_rows_processed}")

                except Exception as e:
                    # Qualquer erro no processamento de UM arquivo invalida toda a carga
                    print(f"!!! ERRO ao processar o arquivo {file_name}: {e}")
                    print("!!! Este arquivo causou uma falha. Toda a transação será revertida.")
                    raise  # propaga para o bloco externo fazer rollback

            # Caso toda a iteração tenha sido bem-sucedida, confirma a transação
            session.commit()
            print("\n--- Todos os dados foram carregados com sucesso no banco de dados! ---")

            # Move os arquivos SOMENTE após o commit bem-sucedido
            for original_path, dest_path in successfully_processed_file_paths:  # type: ignore
                shutil.move(original_path, dest_path)  # type: ignore
                print(f"Arquivo original '{os.path.basename(original_path)}' movido para: {dest_path}")  # type: ignore

        except Exception as e:
            # Reverte qualquer alteração no banco caso algo tenha falhado
            session.rollback()
            print(f"\n!!! ERRO FATAL no processo de carregamento: {e}")
            print("!!! O processo foi abortado. Todas as alterações no banco de dados foram revertidas.")
            print("!!! Nenhum arquivo foi movido para a pasta 'data/loaded_processed'.")
            raise

    print("\n--- Processo de carregamento finalizado! ---")