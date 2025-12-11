from sqlalchemy import Table, Column, Integer, Float, DateTime, MetaData, inspect, Index
from src.database import engine

metadata = MetaData()

TABLE_NAME = "raw_data"

# Definição da tabela
raw_data_table = Table(
    TABLE_NAME,
    metadata,
    Column('time', DateTime, index=True),
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

def ensure_sqlite_database_and_table():
    """Garante que a tabela e índices existam no banco de dados."""
    insp = inspect(engine)

    if not insp.has_table(TABLE_NAME):
        print(f"Tabela '{TABLE_NAME}' não encontrada. Criando estrutura padrão...")
        metadata.create_all(engine)
        print(f"Tabela '{TABLE_NAME}' criada com sucesso.")
    
    # Verifica e cria índice se não existir (para bancos já existentes)
    insp = inspect(engine) # Recarrega inspeção
    indexes = insp.get_indexes(TABLE_NAME)
    
    # Nome padrão que usaremos
    target_index_name = f"ix_{TABLE_NAME}_time"
    
    # Verifica se existe algum índice na coluna 'time'
    has_time_index = False
    for idx in indexes:
        if 'time' in idx.get('column_names', []):
            has_time_index = True
            break

    if not has_time_index:
        print(f"Índice na coluna 'time' não encontrado. Criando índice '{target_index_name}'...")
        # Define a tabela para manipulação do índice (autoload já foi feito via Table definition, 
        # mas aqui usamos a definição explícita acima)
        index = Index(target_index_name, raw_data_table.c.time)
        try:
            index.create(engine)
            print(f"Índice '{target_index_name}' criado com sucesso.")
        except Exception as e:
            print(f"Aviso: Não foi possível criar o índice: {e}")
    else:
        # print("Índice na coluna 'time' já existe.")
        pass
