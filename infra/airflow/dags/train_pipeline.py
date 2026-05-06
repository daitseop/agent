"""
학습 파이프라인 DAG.

흐름:
  1) train       — ml/train/train.py 실행 → MLflow Tracking + Registry 등록
  2) promote     — 최신 등록 버전의 accuracy 가 임계값 이상이면 Production 승격

수동 트리거 전제 (schedule=None). 운영에서는 `@daily` 등으로 변경.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# ml/ 폴더는 docker-compose 의 마운트로 컨테이너 안에서 /opt/dais/ml 로 접근 가능
ML_PATH = "/opt/dais/ml"
if ML_PATH not in sys.path:
    sys.path.insert(0, ML_PATH)

EXPERIMENT = "iris_rf"
MODEL_NAME = "iris_rf"
PROMOTION_THRESHOLD = 0.9


def _train(**_) -> None:
    from train.train import main  # noqa: WPS433
    main(
        experiment=EXPERIMENT,
        model_name=MODEL_NAME,
        n_estimators=100,
        max_depth=5,
    )


def _promote(**_) -> None:
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if not versions:
        raise RuntimeError(f"등록된 모델 버전 없음: {MODEL_NAME}")

    latest = max(versions, key=lambda v: int(v.version))
    run = client.get_run(latest.run_id)
    accuracy = run.data.metrics.get("accuracy", 0.0)

    if accuracy >= PROMOTION_THRESHOLD:
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=latest.version,
            stage="Production",
            archive_existing_versions=True,
        )
        print(f"✅ promoted v{latest.version} acc={accuracy:.4f}")
    else:
        print(
            f"⏭️  skip promotion v{latest.version} "
            f"acc={accuracy:.4f} < {PROMOTION_THRESHOLD}"
        )


with DAG(
    dag_id="train_pipeline",
    description="Iris RandomForest 학습 → Registry 등록 → 조건부 Production 승격",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["mlops", "train"],
) as dag:
    train_task = PythonOperator(
        task_id="train",
        python_callable=_train,
    )
    promote_task = PythonOperator(
        task_id="promote",
        python_callable=_promote,
    )
    train_task >> promote_task
