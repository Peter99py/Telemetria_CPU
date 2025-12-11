from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_CONNECTION_STRING

def get_engine():
    return create_engine(DB_CONNECTION_STRING)

# Instância global do engine e Session para ser importada
engine = get_engine()
Session = sessionmaker(bind=engine)
