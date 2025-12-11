# Monitoramento de CPU: Dashboard Interativo com Streamlit

## Visão Geral do Projeto

Este projeto implementa um pipeline **ETL (Extract, Transform, Load)** completo para monitorar dados de telemetria da CPU, incluindo **temperatura dos núcleos**, **velocidade de clock** e **consumo de energia**. Os dados são coletados, limpos, transformados, e carregados diretamente em um banco de dados **SQLite**, mantendo um histórico dos arquivos originais e processados. Posteriormente, um dashboard interativo é desenvolvido utilizando **Streamlit** para visualizar e analisar essas métricas importantes da CPU. O objetivo é fornecer uma ferramenta para acompanhar o desempenho e o comportamento térmico e energético do processador. 

**(Dados extraídos via log do [Coretemp](https://www.alcpu.com/CoreTemp/) - [Download da versão utilizada no repositório](https://www.alcpu.com/CoreTemp/oldversions/CT1181.zip) - Há também um arquivo .exe com a versão correta do Coretemp dentro da pasta `raw`)**

## Funcionalidades Principais

*   **Processamento de Dados Otimizado**: Script Python que lê, processa em memória e carrega dados diretamente no banco, evitando passos intermediários desnecessários em disco.
*   **Armazenamento de Dados Robustos**: Carregamento transacional em banco de dados **SQLite**, garantindo que apenas dados válidos sejam persistidos.
*   **Dashboard Interativo com Streamlit**: Uma aplicação Web que oferece as seguintes visualizações dinâmicas:
    *   **Temperatura do Núcleo vs. Velocidade do Núcleo**
    *   **Temperatura do Núcleo ao Longo do Dia**
    *   **Consumo de Energia da CPU ao Longo do Dia**
    *   **Consumo de Energia da CPU vs. Temperatura do Núcleo**

## Estrutura do Projeto

A organização do projeto segue a seguinte estrutura de arquivos:
```
Telemetria_CPU/
├── data/                 # Armazenamento de dados
│   ├── raw/              # Arquivos CSV brutos (entrada)
│   ├── loaded_raw/       # Arquivos brutos arquivados após carga
│   ├── loaded_processed/ # Arquivos transformados arquivados (backup)
│   └── telemetria.db     # Banco de Dados SQLite
├── src/                  # Código Fonte Principal
│   ├── database.py       # Configuração da conexão com Banco de Dados
│   ├── models.py         # Definição do Esquema do Banco
│   ├── etl/              # Scripts de ETL
│   │   ├── pipeline.py   # Orquestrador do fluxo
│   │   └── load.py       # Utilitários de carga
│   └── ui/               # Interface do Usuário (Streamlit)
│       ├── charts.py     # Componentes de gráficos
│       └── queries.py    # Consultas SQL
├── app.py                # Ponto de entrada do Dashboard
├── run_pipeline.py       # Ponto de entrada do Pipeline ETL
├── config.py             # Configurações centrais
├── requirements.txt
├── run_dashboard.bat
├── run_pipeline.bat
└── README.md
```
## Tecnologias Utilizadas

O projeto faz uso das seguintes tecnologias e bibliotecas:

*   **Python**: A linguagem de programação central para todas as etapas do projeto.
*   **Pandas**: Utilizada para manipulação e análise eficiente de DataFrames durante o processamento.
*   **Streamlit**: Framework para a construção rápida de aplicações web interativas e o dashboard.
*   **Altair**: Biblioteca de visualização usada para criar os gráficos interativos.
*   **SQLAlchemy**: Toolkit SQL para interação eficiente e pythonica com o banco de dados.
*   **SQLite**: Banco de dados leve e embarcado utilizado para armazenar os dados de telemetria.

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

- **Leitura e Validação**: Leitura dos arquivos brutos com detecção automática de formato.
- **Processamento em Memória**: Limpeza, tipagem e padronização dos dados sem necessidade de arquivos intermediários no disco.
- **Carga Transacional**: Inserção segura no banco de dados SQLite.
- **Arquivamento**: Salvamento de cópias de segurança dos arquivos processados e movimentação dos originais para pastas de histórico (`loaded_raw`).

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

3.  **Executar o Pipeline de Dados**: 
    *   Coloque seus arquivos CSV de telemetria da CPU na pasta `data/raw`.
    *   Execute: `python run_pipeline.py`
    *   O script processará os arquivos, carregará no banco e moverá os originais para `data/loaded_raw`.

4.  **Executar o Dashboard Streamlit**:
    *   Execute: `streamlit run app.py` (ou use o arquivo `run_dashboard.bat` se atualizado)
    *   O dashboard pode ser usado no seu navegador via http://localhost:8501.

### Contribuições são bem-vindas!