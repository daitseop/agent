"""
MLflow Registry 의 Production stage 모델로 배치 추론.

`inference_pipeline` DAG 에서 주기적으로 호출된다.
실제 운영 시 `load_inputs()` 와 `save_outputs()` 를 교체해서 사용.
"""
from __future__ import annotations

import argparse
from typing import Iterable

import mlflow
import mlflow.pyfunc
import numpy as np
from sklearn.datasets import load_iris


def load_inputs() -> np.ndarray:
    # 데모용: Iris 의 첫 5 행을 추론 입력으로 사용
    X, _ = load_iris(return_X_y=True)
    return X[:5]


def save_outputs(predictions: Iterable) -> None:
    # 데모용: stdout 출력만. 운영에서는 MinIO 또는 DB 적재로 교체.
    for i, p in enumerate(predictions):
        print(f"  [{i}] -> class {p}")


def main(model_uri: str) -> None:
    print(f"loading model: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)

    inputs = load_inputs()
    print(f"inputs shape: {inputs.shape}")

    predictions = model.predict(inputs)
    save_outputs(predictions)
    print("✅ inference complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-uri", default="models:/iris_rf/Production")
    args = parser.parse_args()
    main(model_uri=args.model_uri)
