"""
추론 파이프라인 DAG.

흐름:
  1) predict — Production stage 의 최신 모델 로드 → 배치 추론 실행

기본 schedule 은 매시간. 운영에선 데이터 도착 트리거로 변경.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

ML_PATH = "/opt/dais/ml"
if ML_PATH not in sys.path:
    sys.path.insert(0, ML_PATH)

MODEL_NAME = "iris_rf"
MODEL_URI = f"models:/{MODEL_NAME}/Production"


def _predict(**_) -> None:
    from inference.predict import main  # noqa: WPS433
    main(model_uri=MODEL_URI)


with DAG(
    dag_id="inference_pipeline",
    description="Production 모델로 배치 추론",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["mlops", "inference"],
) as dag:
    PythonOperator(
        task_id="predict",
        python_callable=_predict,
    )
