
import os

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para dados
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
LOADED_RAW_DIR = os.path.join(DATA_DIR, "loaded_raw")
LOADED_PROCESSED_DIR = os.path.join(DATA_DIR, "loaded_processed")

# Caminho do Banco de Dados
DB_NAME = "telemetria.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)
DB_CONNECTION_STRING = f"sqlite:///{DB_PATH}"