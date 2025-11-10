# App Streamlit: Monitoramento do Processador
# Construção do Dashboard com filtros (ano/mês/dia), séries temporais e relações

import streamlit as st
from src.charts.charts import line_chart, column_chart
from src.queries.queries import time_vs_temp, temp_vs_speed, time_vs_power, temp_vs_power, temp_ranges, years_available, months_available, days_available, temp_summary

st.set_page_config(page_title="Meu Processador", layout="wide")

st.markdown("<h1 style='text-align: center; color: black;'>Meu Processador</h1>", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.header("Filtros de Data")

    years = years_available()
    sel_year = st.selectbox(
        "Ano",
        options=["Todos"] + years,
        index=0,
        help="Selecione um ano para habilitar o filtro de mês e dia."
    )

    year_val = None if sel_year == "Todos" else int(sel_year)

    # Opções de mês condicionadas ao ano
    months = months_available(year=year_val)
    sel_month = st.selectbox(
        "Mês",
        options=["Todos"] + months if months else ["Todos"],
        index=0,
        help="Selecione um mês (opcional)."
    )
    month_val = None if sel_month == "Todos" else int(sel_month)

    # Opções de dia condicionadas a ano/mês
    days = days_available(year=year_val, month=month_val)
    sel_day = st.selectbox(
        "Dia",
        options=["Todos"] + days if days else ["Todos"],
        index=0,
        help="Selecione um dia (opcional, depende do mês)."
    )
    day_val = None if sel_day == "Todos" else int(sel_day)


# Carregando dataframes
df_temp_ranges = temp_ranges(year=year_val, month=month_val, day=day_val)
df_temp_vs_speed = temp_vs_speed(year=year_val, month=month_val, day=day_val)
df_time_vs_temp = time_vs_temp(year=year_val, month=month_val, day=day_val)
df_time_vs_power = time_vs_power(year=year_val, month=month_val, day=day_val)
df_temp_vs_power = temp_vs_power(year=year_val, month=month_val, day=day_val)
df_temp_summary = temp_summary(year=year_val, month=month_val, day=day_val)


# Layout principal
summary_tab, series_tab, relations_tab = st.tabs(["Resumo", "Séries por Hora", "Relações"])

# Aba "Resumo": visão geral e distribuição de faixas de temperatura
with summary_tab:

    col1, col2 = st.columns([1, 2])  # esquerda menor, direita maior

    # Coluna 1: cartões de métricas
    with col1: 
        st.subheader("Visão geral de temperaturas")

        max_val = df_temp_summary["core temp"].max()
        min_val = df_temp_summary["core temp"].min()
        avg_val = df_temp_summary["core temp"].mean()
        median_value = df_temp_summary["core temp"].median()

        st.metric(label="🌡️ Máxima", value=f"{max_val:.2f} ºC") # Aqui descobri que dava pra usar emoticon dentro de código
        st.metric(label="❄️ Mínima", value=f"{min_val:.2f} ºC")
        st.metric(label="📊 Média", value=f"{avg_val:.2f} ºC")
        st.metric(label="⚖️ Mediana", value=f"{median_value:.2f} ºC")

    # Coluna 2: gráfico de linhas com nível de detalhe (Dia/Mês/Ano)
    with col2:
        st.subheader("Evolução da Temperatura ao Longo do Tempo")
        st.markdown("""<style>div[data-baseweb="select"] {max-width: 150px;}</style>""", unsafe_allow_html=True)

        # Controle de granularidade do gráfico
        level = st.selectbox("Nível de detalhe", ["Dia", "Mês", "Ano"])

        # Agrega máximo por dia e tipo
        if level == "Dia":
            df_plot = df_temp_summary.groupby(["dia", "type"], as_index=False)["core temp"].max()
            x_col = "dia"
        # Agrega máximo por mês e tipo
        elif level == "Mês":
            df_plot = df_temp_summary.groupby(["mes", "type"], as_index=False)["core temp"].max()
            x_col = "mes"
        # Caso padrão: agrega máximo por ano e tipo
        else: 
            df_plot = df_temp_summary.groupby(["ano", "type"], as_index=False)["core temp"].max()
            x_col = "ano"

        chart = line_chart(
            df_plot,
            x_column=x_col,
            y_column="core temp",
            category_column="type",
            title="Temperatura do Núcleo(ºC) ao Longo do Tempo"
        )
        st.altair_chart(chart, use_container_width=True)

# Separador visual
    st.markdown("---")
    # Barras: média diária de minutos por faixa de temperatura
    chart_col = column_chart(
        df_temp_ranges,
        x_column="categoria",
        y_column="media diaria",
        title="Média Diária de Minutos por Faixa de Temperatura(ºC)",
        show_labels=True,
        label_position="fora",
        label_color="black"
    )
    st.altair_chart(chart_col, use_container_width=True)

    st.caption("Quanto tempo, em média por dia, o processador ficou em cada faixa de temperatura.")

# Aba "Séries por Hora": padrões ao longo do dia
with series_tab:
    st.subheader("Padrões ao longo do dia")
    # Duas colunas: Gráficos de linhas
    col1, col2 = st.columns(2, gap="medium")

    # Série temporal: temperatura ao longo do dia
    with col1:
        chart = line_chart(
            df_time_vs_temp,
            x_column="time of day",
            y_column="core temp",
            category_column="type",
            title="Temperatura do Núcleo(ºC) ao Longo do Dia"
        )
        st.altair_chart(chart, use_container_width=True)

    # Coluna 2: gráfico de linhas com nível de detalhe (Dia/Mês/Ano)
    # Série temporal: energia do CPU ao longo do dia
    with col2:
        chart = line_chart(
            df_time_vs_power,
            x_column="time of day",
            y_column="cpu power",
            category_column="type",
            title="Energia do CPU ao Longo do Dia"
        )
        st.altair_chart(chart, use_container_width=True)

    st.caption("Padrões da temperatura e consumo de energia durante o dia.")


# Aba "Relações": correlação visual entre variáveis
with relations_tab:
    st.subheader("Relações entre variáveis")
    # Duas colunas: Gráficos de linhas
    col1, col2 = st.columns(2, gap="medium")

    # Relação temperatura vs velocidade do núcleo
    with col1:

        chart = line_chart(
            df_temp_vs_speed,
            x_column="core temp",
            y_column="core speed",
            category_column="type",
            title="Temperatura do Núcleo(ºC) vs Velocidade do Núcleo"
        )
        st.altair_chart(chart, use_container_width=True)

    # Relação temperatura vs energia do CPU
    with col2:

        chart = line_chart(
            df_temp_vs_power,
            x_column="core temp",
            y_column="cpu power",
            category_column="type",
            title="Temperatura do Núcleo(ºC) vs Energia do CPU"
        )
        st.altair_chart(chart, use_container_width=True)

    st.caption("Variações da velocidade e energia do CPU em relação à temperatura.")