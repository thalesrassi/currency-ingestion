# Pipeline ELT de Ingestão de Dados de Câmbio

Pipeline de ingestão horária de cotações de moedas via [FreeCurrency API](https://freecurrencyapi.com/), armazenando os dados em formato Parquet no MinIO (S3-compatible). Orquestrado pelo Apache Airflow e totalmente containerizado com Docker.

Este é a **primeira fase** de uma stack de engenharia de dados end-to-end:

| Fase | Descrição | Status |
|---------|-----------|--------|
| **1. Ingestão** | Coleta e armazena cotações em Parquet no MinIO | ✅ |
| 2. Modelagem | Transformação com dbt sobre os dados ingeridos | 🔜 |
| 3. Medallion | Camadas bronze/silver/gold com Databricks e PySpark | 🔜 |

---

## Stack

- **[dlthub](https://dlthub.com/)** - framework de ingestão de dados
- **[Apache Airflow](https://airflow.apache.org/)** - orquestração (agendamento horário)
- **[MinIO](https://min.io/)** - armazenamento de objetos S3-compatible (destino dos Parquets)
- **[Docker + Docker Compose](https://docs.docker.com/compose/)** - containerização completa do ambiente
- **[uv](https://github.com/astral-sh/uv)** - gerenciamento de dependências Python

---

## Estrutura

```
.
├── dags/
│   └── currency_dag.py       # DAG do Airflow (agendamento horário)
├── ingestion/
│   ├── source.py             # Source dlt: chama a FreeCurrency API
│   └── pipeline.py           # Pipeline dlt: configura e executa a ingestão
├── scripts/
│   └── read_parquet.py       # Utilitário local para ler os Parquets do MinIO
├── Dockerfile                # Imagem Airflow + dependências do projeto
├── docker-compose.yaml       # Serviços: Airflow, MinIO, Postgres
├── pyproject.toml            # Dependências do projeto
└── .env.example              # Template de variáveis de ambiente
```

---

## Como rodar

### Pré-requisitos

- Docker e Docker Compose instalados

### 1. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Preencha o `.env` com suas credenciais:

```env
API_KEY=           # Chave da FreeCurrency API (gratuita em freecurrencyapi.com)
MINIO_ROOT_USER=   # Usuário do MinIO
MINIO_ROOT_PASSWORD=  # Senha do MinIO (mín. 8 caracteres)
MINIO_BUCKET_URL=s3://currency-rates
MINIO_ENDPOINT_URL=http://localhost:9000
```

### 2. Suba o ambiente

```bash
docker compose up -d
```

Isso inicializa o MinIO, o Postgres, o Airflow e cria o bucket automaticamente.

### 3. Acesse os serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | admin / admin |
| MinIO Console | http://localhost:9001 | suas credenciais do `.env` |

### 4. Ative a DAG

No Airflow UI, ative a DAG `freecurrency_hourly_ingestion`. O primeiro run dispara automaticamente e os seguintes rodam todo início de hora.

---

## Dados gerados

Cada execução grava um arquivo Parquet em:

```
s3://currency-rates/latest/latest_rates/<load_id>.parquet
```

Com o schema:

| Campo | Descrição |
|-------|-----------|
| `base_currency` | Moeda base (BRL) |
| `target_currency` | Moeda alvo (USD, EUR, GBP, JPY) |
| `rate` | Taxa de câmbio |
| `extracted_at` | Timestamp da coleta |
