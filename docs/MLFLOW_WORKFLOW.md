# MLflow 학습 → 등록 → 배포 워크플로

> 본 문서는 골격이다. **Phase 3** 에서 실제 동작 기준으로 본문이 채워진다.

---

## 1. 전체 흐름 (예정)

```
[1] 학습       ─→  ml/train/ 스크립트 실행
                  MLflow Tracking 으로 param/metric/model 기록
                  artifact 는 MinIO 에 자동 업로드

[2] 등록       ─→  mlflow.register_model() 로 Model Registry 등록
                  버전 자동 증가

[3] 평가/승격  ─→  metric 기준 통과 시 Production stage 로 transition
                  (수동 또는 Airflow 자동)

[4] 배포(서빙) ─→  mlflow models serve  또는 FastAPI 래퍼
                  Production stage 의 최신 버전 사용

[5] 추론       ─→  Airflow inference DAG 가 주기적으로 호출
```

---

## 2. 컴포넌트 매핑

| 단계 | 위치 | 비고 |
|---|---|---|
| 학습 코드 | `ml/train/` | sklearn 등 (Phase 3 결정) |
| 서빙 코드 | `ml/serve/` | 컨테이너화 여부 Phase 3 결정 |
| 학습 DAG | `infra/airflow/dags/train_pipeline.py` | |
| 추론 DAG | `infra/airflow/dags/inference_pipeline.py` | |
| 메타데이터 DB | Postgres `mlflow_db` | |
| Artifact | MinIO `mlflow-artifacts` 버킷 | |

---

## 3. 환경변수 의존성

학습 스크립트가 동작하려면 다음 변수가 필요:

```
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

(Airflow 컨테이너에 모두 주입되어 있음 — Phase 2 에서 docker-compose 로 처리)

---

## 4. 모델 라이프사이클

| Stage | 의미 |
|---|---|
| None | 등록 직후 |
| Staging | 검증 중 |
| Production | 운영 배포 |
| Archived | 폐기 |

승격 정책 / 자동화 여부는 Phase 3 에서 결정.

---

## 5. TODO

- [ ] Phase 3 — 실제 학습 스크립트 작성 후 본 문서 본문 작성
- [ ] Phase 3 — Airflow DAG 명세 (스케줄, 의존성, 실패 시 동작)
- [ ] Phase 3 — 모델 승격 기준 정의
