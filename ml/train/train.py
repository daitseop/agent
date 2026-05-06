"""
Iris 데이터셋으로 RandomForestClassifier 학습 → MLflow Tracking + Model Registry 등록.

이 스크립트는 Airflow `train_pipeline` DAG 에서 호출되며,
실제 모델로 교체할 때는 `main()` 의 학습 로직만 수정하면 된다.
"""
from __future__ import annotations

import argparse

import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split


def main(
    experiment: str,
    model_name: str,
    n_estimators: int,
    max_depth: int,
) -> dict[str, float]:
    mlflow.set_experiment(experiment)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run() as run:
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "test_size": 0.2,
        })

        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
        )
        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "f1": f1_score(y_test, preds, average="weighted"),
        }
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(
            sk_model=clf,
            artifact_path="model",
            registered_model_name=model_name,
        )

        print(
            f"run_id={run.info.run_id} "
            f"acc={metrics['accuracy']:.4f} f1={metrics['f1']:.4f}"
        )
        return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", default="iris_rf")
    parser.add_argument("--model-name", default="iris_rf")
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args()
    main(
        experiment=args.experiment,
        model_name=args.model_name,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
    )
