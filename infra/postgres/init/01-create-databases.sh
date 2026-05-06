#!/bin/bash
# Postgres 컨테이너 최초 기동 시 1회만 실행됨.
# MLflow, Airflow 가 사용할 두 개의 DB 를 분리 생성한다.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE mlflow_db;
    CREATE DATABASE airflow_db;
    GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON DATABASE airflow_db TO "$POSTGRES_USER";
EOSQL

echo "✅ mlflow_db, airflow_db 생성 완료"
