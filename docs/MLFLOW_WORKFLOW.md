# MLflow 학습 → 등록 → 배포 워크플로

> Phase 3 데모 구현 기준. 실제 모델로 교체하려면 `ml/train/train.py` 와 `ml/inference/predict.py` 만 수정하면 된다.

---

## 1. 전체 흐름

```
[Airflow] train_pipeline DAG (수동 트리거)
   │
   ├─ task: train
   │     └─ ml/train/train.py 실행
   │         · MLflow Tracking : params / metrics 기록
   │         · MLflow Registry : 모델 자동 등록 (registered_model_name="iris_rf")
   │         · Artifact 는 MinIO 의 mlflow-artifacts 버킷에 저장
   │
   └─ task: promote
         └─ 최신 등록 버전 조회 → accuracy ≥ 0.9 면 Production stage 로 승격
            (기존 Production 은 자동으로 Archived)


[Airflow] inference_pipeline DAG (@hourly)
   │
   └─ task: predict
         └─ ml/inference/predict.py 실행
             · models:/iris_rf/Production 로드
             · 배치 추론 → stdout (운영 시 MinIO/DB 적재로 교체)
```

---

## 2. 컴포넌트 매핑

| 단계 | 위치 | 비고 |
|---|---|---|
| 학습 코드 | [ml/train/train.py](../ml/train/train.py) | sklearn Iris + RandomForest (데모) |
| 추론 코드 | [ml/inference/predict.py](../ml/inference/predict.py) | Production 모델 로드 |
| 학습 DAG | [infra/airflow/dags/train_pipeline.py](../infra/airflow/dags/train_pipeline.py) | train → promote |
| 추론 DAG | [infra/airflow/dags/inference_pipeline.py](../infra/airflow/dags/inference_pipeline.py) | @hourly |
| 메타데이터 DB | Postgres `mlflow_db` | run / registry 메타 |
| Artifact | MinIO `mlflow-artifacts` 버킷 | 모델 바이너리 |
| 서빙 (선택) | [ml/serve/README.md](../ml/serve/README.md) | `mlflow models serve` |

---

## 3. 마운트 / 환경변수

Airflow 컨테이너에는 `ml/` 폴더가 `/opt/dais/ml` 로 마운트되어 있다 (read-only). DAG 가 `sys.path.insert(0, "/opt/dais/ml")` 후 학습/추론 모듈을 import.

DAG 가 사용하는 환경변수 (compose 의 `airflow-common-env` 에서 주입):

```
MLFLOW_TRACKING_URI       = http://mlflow:5000
MLFLOW_S3_ENDPOINT_URL    = http://minio:9000
AWS_ACCESS_KEY_ID         = (.env)
AWS_SECRET_ACCESS_KEY     = (.env)
```

---

## 4. 모델 라이프사이클

| Stage | 의미 | 진입 방법 |
|---|---|---|
| None | 등록 직후 | `mlflow.sklearn.log_model(..., registered_model_name=...)` 자동 |
| Staging | 검증 중 | (현재 미사용) |
| Production | 운영 배포 | `train_pipeline` 의 promote task 가 자동 transition |
| Archived | 폐기 | promote 시 `archive_existing_versions=True` 로 자동 |

승격 임계값 (`PROMOTION_THRESHOLD = 0.9`) 은 [train_pipeline.py](../infra/airflow/dags/train_pipeline.py) 상단에서 조정.

> ⚠️ MLflow 2.x 의 `transition_model_version_stage` API 는 deprecated 표시지만 여전히 동작한다.
> 향후 `set_registered_model_alias` (alias 기반) 로 마이그레이션 검토.

---

## 5. 사용 절차 (사용자 검증)

```bash
# 1) 인프라 기동
make up

# 2) Airflow UI 접속 (http://localhost:8080, admin/admin)
#    train_pipeline 활성화 → 수동 트리거

# 3) MLflow UI 접속 (http://localhost:5000)
#    - Experiments → iris_rf 에 run 1개 생성 확인
#    - Models → iris_rf 모델 등록 + Production stage 확인

# 4) MinIO Console 접속 (http://localhost:9001)
#    - mlflow-artifacts 버킷에 모델 파일 업로드 확인

# 5) inference_pipeline 활성화
#    - 다음 시각 자동 실행 또는 수동 트리거
#    - Task log 에서 5개 예측 결과 확인
```

---

## 6. 실제 모델로 교체하는 방법

1. `ml/train/train.py` 의 `main()` 본문에서:
   - `load_iris(...)` → 자체 데이터 로딩 함수
   - `RandomForestClassifier(...)` → 원하는 모델
   - `mlflow.sklearn.log_model` → 모델 종류에 맞는 flavor (e.g. `mlflow.pytorch`)
2. `ml/inference/predict.py` 의 `load_inputs()` / `save_outputs()` 를 실제 입출력 로직으로 교체.
3. DAG 의 `EXPERIMENT`, `MODEL_NAME`, `PROMOTION_THRESHOLD` 조정.
4. `infra/airflow/requirements.txt` 에 추가 패키지가 필요하면 등록 후 `make build && make up`.

---

## 7. TODO

- [ ] Phase 4 이후: Agent 가 train_pipeline 을 트리거하는 Tool 작성
- [ ] alias 기반 모델 라우팅으로 마이그레이션
- [ ] 추론 결과 저장 위치 결정 (현재 stdout)
