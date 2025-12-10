# Consultas ao banco (SQLite) para o app
# Descrição: funções de conexão, montagem de filtros e consultas agregadas.

from sqlalchemy import create_engine, text
import pandas as pd
import os
import streamlit as st
from datetime import datetime, timedelta


# Conexão com SQLite
@st.cache_resource
def get_engine():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # pasta onde está queries.py
    db_path = os.path.join(base_dir, "data.db")
    return create_engine(f"sqlite:///{db_path}")


# Montagem de WHERE e parâmetros para ano/mês/dia
def date_filters(year=None, month=None, day=None):

    conds = []
    params = {}

    # Se informado, filtra por ano (EXTRACT YEAR)
    if year is not None:
        y = int(year)
        if month is not None:
            m = int(month)
            if day is not None:
                d = int(day)
                # Filtro por dia específico: time >= YYYY-MM-DD 00:00:00 AND time < YYYY-MM-(DD+1) 00:00:00
                start_date = datetime(y, m, d)
                end_date = start_date + timedelta(days=1)
                conds.append("time >= :start_date AND time < :end_date")
                params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
                params["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Filtro por mês específico: time >= YYYY-MM-01 00:00:00 AND time < YYYY-(MM+1)-01 00:00:00
                start_date = datetime(y, m, 1)
                if m == 12:
                    end_date = datetime(y + 1, 1, 1)
                else:
                    end_date = datetime(y, m + 1, 1)
                conds.append("time >= :start_date AND time < :end_date")
                params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
                params["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
             # Filtro por ano específico: time >= YYYY-01-01 00:00:00 AND time < (YYYY+1)-01-01 00:00:00
            start_date = datetime(y, 1, 1)
            end_date = datetime(y + 1, 1, 1)
            conds.append("time >= :start_date AND time < :end_date")
            params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
            params["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # Fallback para casos onde year é None mas outros filtros existem
    elif month is not None or day is not None:
         # Se informado, filtra por mês (EXTRACT MONTH)
        if month is not None:
            conds.append("strftime('%m', time) = :month")
            params["month"] = f"{int(month):02d}"
            
        # Se informado, filtra por dia (EXTRACT DAY)
        if day is not None:
            conds.append("strftime('%d', time) = :day")
            params["day"] = f"{int(day):02d}"

    # Gera WHERE ... AND ... quando existirem condições, caso contrário vazio
    where_sql = f"WHERE {' AND '.join(conds)}" if conds else ""
    return where_sql, params


# Dimensão de tempo: anos disponíveis nos dados
@st.cache_data
def years_available():

    engine = get_engine()
    query = """
        SELECT DISTINCT strftime('%Y', time) AS year 
        FROM raw_data ORDER BY year
        """
    
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)

    
    return df["year"].tolist()


# Dimensão de tempo: meses disponíveis (opcionalmente filtrados por ano)
@st.cache_data
def months_available(year=None):

    engine = get_engine()
    # Consulta base para DISTINCT, WHERE será anexado conforme filtros
    base = """
        SELECT DISTINCT CAST(strftime('%m', time) AS INTEGER) AS month 
        FROM raw_data
        """
    
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year=year)
    query = f"""
        {base}
        {where_sql}
        ORDER BY month
        """
    
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    
    return df["month"].tolist()


# Dimensão de tempo: dias disponíveis (opcionalmente filtrados por ano/mês)
@st.cache_data
def days_available(year=None, month=None):

    engine = get_engine()
    # Consulta base para DISTINCT; WHERE será anexado conforme filtros
    base = """
        SELECT DISTINCT CAST(strftime('%d', time) AS INTEGER) AS day 
        FROM raw_data
        """
    
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year=year, month=month)
    query = f"""
        {base}
        {where_sql}
        ORDER BY day
    """

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    # Retorna a lista simples (anos/meses/dias) para popular selects no app
    return df["day"].tolist()

# Resumo diário (MIN/AVG/MAX) da temperatura por dia
@st.cache_data
def temp_summary(year=None, month=None, day=None):

    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)

    query = f"""
        WITH filtrado AS (
            SELECT DATE(time) AS time, core_temp_0
            FROM raw_data
            {where_sql}
        )

        SELECT 
            CAST(strftime('%Y', time) AS INTEGER) AS "ano",
            CAST(strftime('%m', time) AS INTEGER) AS "mes",
            CAST(strftime('%d', time) AS INTEGER) AS "dia",
            MIN(core_temp_0) AS "core temp",
            'MIN' AS "type"
        FROM filtrado
        GROUP BY ano, mes, dia

        UNION ALL

        SELECT 
            CAST(strftime('%Y', time) AS INTEGER) AS "ano",
            CAST(strftime('%m', time) AS INTEGER) AS "mes",
            CAST(strftime('%d', time) AS INTEGER) AS "dia",
            CAST(AVG(core_temp_0) AS INTEGER) AS "core temp",
            'AVG' AS "type"
        FROM filtrado
        GROUP BY ano, mes, dia

        UNION ALL

        SELECT 
            CAST(strftime('%Y', time) AS INTEGER) AS "ano",
            CAST(strftime('%m', time) AS INTEGER) AS "mes",
            CAST(strftime('%d', time) AS INTEGER) AS "dia",
            MAX(core_temp_0) AS "core temp",
            'MAX' AS "type"
        FROM filtrado
        GROUP BY ano, mes, dia
        """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    except Exception as e:
        print(f"Erro ao executar a consulta temp_summary: {e}")
        return None


# Relaciona temperatura (X) vs velocidade do núcleo (Y) por faixa (MIN/AVG/MAX)
@st.cache_data
def temp_vs_speed(year=None, month=None, day=None):

    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)

    query = f"""
        WITH filtrado AS (
            SELECT time, core_temp_0, core_speed_0
            FROM raw_data
            {where_sql}
        )
        SELECT
            core_temp_0 AS "core temp",
            CAST(MIN(core_speed_0) AS INTEGER) AS "core speed",
            'MIN' AS "type"
        FROM filtrado
        GROUP BY core_temp_0

        UNION ALL

        SELECT
            core_temp_0 AS "core temp",
            CAST(AVG(core_speed_0) AS INTEGER) AS "core speed",
            'AVG' AS "type"
        FROM filtrado
        GROUP BY core_temp_0

        UNION ALL

        SELECT
            core_temp_0 AS "core temp",
            CAST(MAX(core_speed_0) AS INTEGER) AS "core speed",
            'MAX' AS "type"
        FROM filtrado
        GROUP BY core_temp_0
        """
    try:

        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    except Exception as e:
        print(f"Erro ao executar a consulta temp_vs_speed: {e}")
        return None


# Temperatura por hora do dia (MIN/AVG/MAX)
@st.cache_data
def time_vs_temp(year=None, month=None, day=None):

    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)
    query = f"""
        WITH filtrado AS (
            SELECT CAST(strftime('%H', time) AS INTEGER) AS hora, core_temp_0
            FROM raw_data
            {where_sql}
        )
        SELECT
            hora AS "time of day",
            MIN(core_temp_0) AS "core temp",
            'MIN' AS "type"
        FROM filtrado
        GROUP BY hora

        UNION ALL

        SELECT
            hora AS "time of day",
            CAST(AVG(core_temp_0) AS INTEGER) AS "core temp",
            'AVG' AS "type"
        FROM filtrado
        GROUP BY hora

        UNION ALL

        SELECT
            hora AS "time of day",
            MAX(core_temp_0) AS "core temp",
            'MAX' AS "type"
        FROM filtrado
        GROUP BY hora
        """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df

    except Exception as e:
        print(f"Erro ao executar a consulta time_vs_temp: {e}")
        return None


# Energia do CPU por hora do dia (MIN/AVG/MAX)
@st.cache_data
def time_vs_power(year=None, month=None, day=None):

    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)
    query = f"""
        WITH filtrado AS (
            SELECT CAST(strftime('%H', time) AS INTEGER) AS hora, cpu_power
            FROM raw_data
            {where_sql}
        )
        SELECT
            hora AS "time of day",
            CAST(MIN(cpu_power) AS INTEGER) AS "cpu power",
            'MIN' AS "type"
        FROM filtrado
        GROUP BY hora

        UNION ALL

        SELECT
            hora AS "time of day",
            CAST(AVG(cpu_power) AS INTEGER) AS "cpu power",
            'AVG' AS "type"
        FROM filtrado
        GROUP BY hora

        UNION ALL

        SELECT
            hora AS "time of day",
            CAST(MAX(cpu_power) AS INTEGER) AS "cpu power",
            'MAX' AS "type"
        FROM filtrado
        GROUP BY hora
        """
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df
    # Em caso de falha
    except Exception as e:
        print(f"Erro ao executar a consulta time_vs_power: {e}")
        return None


# Relaciona temperatura (X) vs energia do CPU (Y) por faixa (MIN/AVG/MAX)
@st.cache_data
def temp_vs_power(year=None, month=None, day=None):
    # Obtém Engine compartilhado para executar a consulta
    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)
    query = f"""
        WITH filtrado AS (
            SELECT core_temp_0, cpu_power
            FROM raw_data
            {where_sql}
        )
        SELECT
            core_temp_0 AS "core temp",
            CAST(MIN(cpu_power) AS INTEGER) AS "cpu power",
            'MIN' AS "type"
        FROM filtrado
        GROUP BY core_temp_0

        UNION ALL

        SELECT
            core_temp_0 AS "core temp",
            CAST(AVG(cpu_power) AS INTEGER) AS "cpu power",
            'AVG' AS "type"
        FROM filtrado
        GROUP BY core_temp_0

        UNION ALL

        SELECT
            core_temp_0 AS "core temp",
            CAST(MAX(cpu_power) AS INTEGER) AS "cpu power",
            'MAX' AS "type"
        FROM filtrado
        GROUP BY core_temp_0
        """
    try:
        # Abre conexão temporária e traz resultado em DataFrame
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)  # type: ignore
        return df
    # Em caso de falha
    except Exception as e:
        print(f"Erro ao executar a consulta temp_vs_power: {e}")
        return None


# Média diária de minutos por faixa de temperatura
@st.cache_data
def temp_ranges(year=None, month=None, day=None):
    # Obtém Engine compartilhado para executar a consulta
    engine = get_engine()
    # Monta WHERE/params de acordo com os filtros (None => ignora)
    where_sql, params = date_filters(year, month, day)
    query = f"""
        WITH filtrado AS (
            SELECT time, core_temp_0
            FROM raw_data
            {where_sql}
        ),
        minutos_por_dia AS (
            SELECT DATE(time) AS dia, COUNT(time) / 6.0 AS minutos, '<60' AS categoria
            FROM filtrado
            WHERE core_temp_0 < 60
            GROUP BY DATE(time)
            UNION ALL
            SELECT DATE(time) AS dia, COUNT(time) / 6.0 AS minutos, '>=60 & <70' AS categoria
            FROM filtrado
            WHERE core_temp_0 >= 60 AND core_temp_0 < 70
            GROUP BY DATE(time)
            UNION ALL
            SELECT DATE(time) AS dia, COUNT(time) / 6.0 AS minutos, '>=70 & <80' AS categoria
            FROM filtrado
            WHERE core_temp_0 >= 70 AND core_temp_0 < 80
            GROUP BY DATE(time)
            UNION ALL
            SELECT DATE(time) AS dia, COUNT(time) / 6.0 AS minutos, '>=80 & <90' AS categoria
            FROM filtrado
            WHERE core_temp_0 >= 80 AND core_temp_0 < 90
            GROUP BY DATE(time)
            UNION ALL
            SELECT DATE(time) AS dia, COUNT(time) / 6.0 AS minutos, '>=90' AS categoria
            FROM filtrado
            WHERE core_temp_0 > 90
            GROUP BY DATE(time)
        )
        SELECT
            ROUND(AVG(minutos)) AS "media diaria",
            categoria,
            CASE
                WHEN categoria = '<60' THEN 1
                WHEN categoria = '>=60 & <70' THEN 2
                WHEN categoria = '>=70 & <80' THEN 3
                WHEN categoria = '>=80 & <90' THEN 4
                WHEN categoria = '>=90' THEN 5
            END AS ordernar
        FROM minutos_por_dia
        GROUP BY categoria
        ORDER BY ordernar
        """
    try:
        # Abre conexão temporária e traz resultado em DataFrame
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        return df
    # Em caso de falha
    except Exception as e:
        print(f"Erro ao executar a consulta temp_ranges: {e}")
        return None