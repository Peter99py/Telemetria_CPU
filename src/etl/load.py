from src.models import TABLE_NAME

def insert_dataframe(session, df):
    """Insere um DataFrame no banco de dados."""
    
    # Fazendo cópia para não alterar o original que será salvo em CSV
    df_to_load = df.copy()
    if 'time' in df_to_load.columns:
         try:
            # Se for datetime, converte. Se já for string, mantém.
            if not df_to_load['time'].dtype == 'object':
                 df_to_load['time'] = df_to_load['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
         except:
             pass
         df_to_load['time'] = df_to_load['time'].astype(str)

    df_to_load.to_sql(
        TABLE_NAME,
        session.connection(),
        if_exists='append',
        index=False
    )
