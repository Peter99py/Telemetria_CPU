# Monitoramento de CPU: Dashboard Interativo com Streamlit

## Visão Geral do Projeto

Este projeto implementa um pipeline **ETL (Extract, Transform, Load)** completo para monitorar dados de telemetria da CPU, incluindo **temperatura dos núcleos**, **velocidade de clock** e **consumo de energia**. Os dados são coletados, limpos, transformados, e carregados em um banco de dados **SQLite**. Posteriormente, um dashboard interativo é desenvolvido utilizando **Streamlit** para visualizar e analisar essas métricas importantes da CPU. O objetivo é fornecer uma ferramenta para acompanhar o desempenho e o comportamento térmico e energético do processador. 

**(Dados extraídos via log do [Coretemp](https://www.alcpu.com/CoreTemp/) - [Download da versão utilizada no repositório](https://www.alcpu.com/CoreTemp/oldversions/CT1181.zip) - Há também um arquivo .exe com a versão correta do Coretemp dentro da pasta `raw`)**

## Funcionalidades Principais

*   **Processamento de Dados Automatizado**: Um script Python automatiza a limpeza e organização de arquivos CSV brutos.
*   **Armazenamento de Dados Robustos**: Carregamento dos dados processados em um banco de dados **SQLite**, com tratamento de transações para garantir a integridade dos dados.
*   **Dashboard Interativo com Streamlit**: Uma aplicação Web que oferece as seguintes visualizações dinâmicas:
    *   **Temperatura do Núcleo vs. Velocidade do Núcleo**
    *   **Temperatura do Núcleo ao Longo do Dia**
    *   **Consumo de Energia da CPU ao Longo do Dia**
    *   **Consumo de Energia da CPU vs. Temperatura do Núcleo**

## Estrutura do Projeto

A organização do projeto segue a seguinte estrutura de arquivos:
```
Registros CPU
├── .venv/
├── dashboard/
│   ├── src/
│   │   ├── charts/
│   │   │   └── line_charts.py
│   │   └── queries/
│   │       └── queries.py 
│   ├── app.py
│   └── run_pipeline.py
├──data
│    ├── data_loaded_processed/
│    ├── data_loaded_raw/
│    ├── data_processed/
│    ├── data_raw/
│           └── CoreTemp.exe
├── scripts/
│   ├── load.py
│   ├── main.py
│   └── pipeline.py
├── README.md
├── run_dashboard.bat
└── run_pipeline.bat
```
## Tecnologias Utilizadas

O projeto faz uso das seguintes tecnologias e bibliotecas:

*   **Python**: A linguagem de programação central para todas as etapas do projeto.
*   **Pandas**: Utilizada para manipulação e análise eficiente de DataFrames durante o processamento e leitura de dados.
*   **Streamlit**: Framework para a construção rápida de aplicações web interativas e o dashboard.
*   **Altair**: Biblioteca de visualização usada para criar os gráficos interativos no dashboard.
*   **SQLAlchemy**: Toolkit Python SQL para interação com o banco de dados PostgreSQL.
*   **Psycopg2**: Adaptador PostgreSQL para Python, utilizado pela SQLAlchemy para conexão com o banco de dados.
*   **SQLite**: Banco de dados utilizado para armazenar os dados de telemetria da CPU.

## Dados

Os dados de entrada são arquivos CSV contendo telemetria da CPU. As colunas principais incluem:

*   `time`: Data/hora da coleta.
*   `core_temp_X`: Temperatura atual de cada núcleo (0 a 5) em graus Celsius (°C).
*   `low_temp_X` / `high_temp_X`: Temperaturas mínimas e máximas registradas para cada núcleo.
*   `core_load_X`: Carga de trabalho de cada núcleo (em %).
*   `core_speed_X`: Velocidade de clock de cada núcleo (em MHz).
*   `cpu_power`: Consumo total de energia da CPU.

## Etapas de Transformação dos Dados

Este projeto realiza uma preparação cuidadosa dos dados brutos para garantir **qualidade** e **consistência** na análise. O processo envolve:

- **Leitura dos dados originais** com ajustes de compatibilidade.
- **Limpeza de colunas** irrelevantes ou vazias.
- **Padronização dos horários** e remoção de registros incompletos.
- **Organização e renomeação** das colunas para facilitar consultas.
- **Armazenamento dos dados tratados** e separação dos arquivos já processados.

## Dashboard Interativo

O dashboard exibe visualizações dinâmicas com base em dados consultados diretamente do banco de dados. Os gráficos são gerados com **Altair**, oferecendo uma experiência interativa.

### Visualizações disponíveis:

- **Temperatura vs. Velocidade do Núcleo**  
  Compara a velocidade média, mínima e máxima do núcleo em diferentes faixas de temperatura.

- **Temperatura ao Longo do Dia**  
  Mostra como a temperatura do núcleo varia ao longo do tempo.

- **Consumo de Energia ao Longo do Dia**  
  Apresenta o comportamento energético da CPU em diferentes horários.

- **Energia vs. Temperatura do Núcleo**  
  Relaciona o consumo de energia com a temperatura, revelando padrões de desempenho.

- **Média Diária por Faixa de Temperatura**  
  Indica quanto tempo, em média, o processador opera em cada faixa térmica ao longo do dia.

Essas visualizações ajudam a entender o desempenho térmico e energético do sistema de forma clara e acessível.
    
## Como Executar o Projeto

1.  **Configuração do Ambiente Python**:
    *   Recomendo criar e ativar um ambiente virtual:
        python -m venv .venv
        # Para Windows:
        .venv\Scripts\activate
        # Para macOS/Linux:
        source .venv/bin/activate

    *   Instale as dependências necessárias:
        `pip install -r requirements.txt`

3.  **Execute o arquivo run_pipeline.bat**: 

    **Cria os seguintes diretórios:**

```
    └──data\
        ├──data_raw
        ├──data_loaded_raw
        ├──data_processed
        └──data_loaded_processed

    No fim, este script moverá os arquivos crus de "data_raw" para "data_loaded_raw" 
    e salvará os arquivos processados em "data_processed".
```

4.  **Dados Brutos**: Coloque seus arquivos CSV de telemetria da CPU (extraídos do `coretemp`) dentro da pasta `data_raw`.

5.  **Executar o Dashboard Streamlit**:
    *   Execute o arquivo run_dashboard.bat
        
    *   O dashboard pode ser usado no seu navegador via http://localhost:8501.
    

### Contribuições são bem-vindas!