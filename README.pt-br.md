[🇺🇸 View in English](./README.md)
---
# Pipeline de Dados em Tempo Real da Frota de Ônibus

![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=Apache-Airflow&logoColor=white)
![Spark](https://img.shields.io/badge/Spark-E25A1C?style=for-the-badge&logo=Apache-Spark&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=Apache-Kafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---
![Dashboard Screenshot](img/demo.png)

![Dashboard Screenshot](img/demo1.png)

Este projeto implementa um pipeline de engenharia de dados completo (ponta a ponta) que captura dados de transporte público de São Paulo em tempo real, processa com Spark, armazena em um data lake local e orquestra todo o fluxo com Airflow.

## 🏛️ Arquitetura

O pipeline foi projetado para ser uma plataforma escalável e robusta para lidar com fluxos de dados em tempo real. Os dados passam por diversas etapas, desde a ingestão até o armazenamento e a visualização.

**Fluxo de Dados:**
1.  **Ingestão:** Um script Python (`producer.py`) consome a API oficial [Olho Vivo da SPTrans](https://www.sptrans.com.br/desenvolvedores/) para buscar dados de localização dos ônibus em tempo real.
2.  **Fila de Mensagens:** Os dados coletados são publicados como mensagens em um tópico Kafka, criando um fluxo de dados durável e escalável.
3.  **Processamento de Stream:** Um job Spark Structured Streaming consome os dados do tópico Kafka em tempo real. Ele aplica transformações, limpa os dados e converte os tipos de dados.
4.  **Armazenamento em Data Lake:** Os dados processados são escritos em um Data Lake local no formato colunar de alta eficiência Parquet.
5.  **Orquestração:** Todo o workflow é agendado, monitorado e automatizado pelo Apache Airflow, garantindo que as tarefas rodem na ordem correta e tratando falhas de forma elegante.
6.  **BI & Análise:** Os dados finais armazenados nos arquivos Parquet são conectados ao Power BI para a criação de dashboards interativos e a Jupyter Notebooks para análises aprofundadas com Spark SQL.

## 🛠️ Tecnologias Utilizadas

- **Ingestão de Dados:** Python (`requests`), Apache Kafka
- **Processamento de Dados:** Apache Spark (PySpark)
- **Armazenamento de Dados:** Parquet (Data Lake)
- **Orquestração:** Apache Airflow
- **Containerização:** Docker & Docker Compose
- **BI & Visualização:** Power BI
- **Análise:** Jupyter Notebook, Spark SQL
- **Ambiente:** Python 3.11, Java 17

## 🚀 Configuração e Execução

Siga os passos abaixo para executar o pipeline completo na sua máquina local.

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11
- Um Token de API do [Olho Vivo da SPTrans](https://www.sptrans.com.br/desenvolvedores/).

### Passos
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/](https://github.com/)[SEU_USUARIO]/[SEU_REPOSITORIO].git
    cd [SEU_REPOSITORIO]
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Token da API:**
    *(Este token é necessário para rodar o produtor em tempo real ou o coletor de amostras)*.
    ```bash
    export SPTRANS_API_TOKEN='SEU_TOKEN_AQUI'
    ```
    
5.  **Inicie a Infraestrutura:**
    Este comando irá iniciar os contêineres do Kafka e Zookeeper em segundo plano.
    ```bash
    docker-compose up -d
    ```

6.  **Inicialize e Execute o Airflow:**
    * **Defina o `AIRFLOW_HOME`:**
        ```bash
        export AIRFLOW_HOME=$(pwd)/airflow
        ```
    * **Inicialize o Banco de Dados:**
        ```bash
        airflow db init
        ```
    * **Crie um Usuário Administrador:**
        ```bash
        airflow users create \
            --username admin \
            --firstname SeuNome \
            --lastname SeuSobrenome \
            --role Admin \
            --email seu.email@example.com \
            --password suasenha
        ```
    * **Inicie o Webserver e o Scheduler (em dois terminais separados):**
        ```bash
        # Terminal 1
        airflow webserver
        
        # Terminal 2
        airflow scheduler
        ```

7.  **Execute o Pipeline:**
    * Acesse a interface do Airflow em `http://localhost:8080`.
    * Faça login com as credenciais que você acabou de criar.
    * Encontre a DAG `sptrans_data_pipeline`, ative-a no botão de toggle e a acione usando o botão de play.

## 📊 Dashboard & Análise

O resultado final deste pipeline é um data lake de arquivos Parquet, que pode ser usado para análise.

### Dashboard no Power BI
Um relatório no Power BI foi criado para visualizar os dados coletados, mostrando KPIs, a localização dos ônibus em um mapa e tendências de atividade ao longo do tempo.

![Dashboard Screenshot](img/demo.png)

### Análise com SQL
Os dados também podem ser consultados interativamente usando Spark SQL em um Jupyter Notebook, localizado na pasta `/notebooks`.

## 🔧 Desafios e Aprendizados

A construção deste pipeline ponta a ponta envolveu a superação de diversos desafios reais de engenharia de dados:

-   **Inferno do Ambiente:** O projeto começou com grandes problemas de compatibilidade entre o Spark 4.0, seus conectores e a versão do Java. Isso foi resolvido com o downgrade para as versões estáveis do Spark 3.5.1 e Python 3.11, criando um ambiente limpo e reprodutível.
-   **Conflitos de Dependência:** Os conectores para serviços na nuvem como BigQuery e Delta Lake apresentaram conflitos profundos de dependência (`NoSuchMethodError`, `ClassNotFoundException`). Isso levou a uma decisão estratégica de pivotar para uma solução mais robusta e com dependências isoladas (salvar em Parquet nativo).
-   **Problemas de Rede/Firewall:** O comando `spark-submit --packages` falhou consistentemente em baixar dependências devido a um problema de rede local, reforçando a decisão de usar uma arquitetura que minimizasse downloads externos durante a execução.
-   **Detalhes de Orquestração:** A implementação no Airflow revelou problemas clássicos de orquestração, como condições de corrida (o consumidor Spark iniciando antes do tópico Kafka ser criado) e o tratamento de códigos de saída de comandos shell (`gtimeout` no macOS). Estes foram resolvidos com a adição de tarefas de espera e lógica de tratamento de erro na DAG.

## Melhorias Futuras

-   Fazer o deploy de toda a stack para um provedor de nuvem (GCP ou AWS).
-   Utilizar um serviço gerenciado de Kafka (como o Confluent Cloud) em vez de um contêiner local.
-   Substituir o data lake Parquet por um Data Warehouse gerenciado como BigQuery ou Snowflake assim que os problemas de rede forem resolvidos.
-   Criar dashboards de BI mais complexos e alertas automatizados.

## 👤 Autor

**Vinicius Moreira**

-   [LinkedIn](https://www.linkedin.com/in/vinicius-moreira-806105350)
-   [GitHub](https://github.com/Viniciuss-Moreira)
