# dais_agent 프로젝트 계획서

> 이 문서는 프로젝트의 **single source of truth**이다.
> 모든 작업은 이 계획서의 단계 순서를 따른다.
> 결정이 바뀌면 이 문서를 먼저 수정한 뒤 코드를 변경한다.

---

## 1. 프로젝트 개요

최소한의 MLOps 환경 위에서 동작하는 **독립 Agent들**을 개발하는 플랫폼.
MLOps 자체가 목적이 아니라, Agent가 동작할 수 있는 환경을 제공하는 것이 목적.

### 구성 요소
- **MLflow**: 모델 학습/등록/배포 관리
- **Airflow**: 모델 학습/추론 파이프라인 자동화
- **Grafana + Prometheus**: 실시간 모니터링
- **MinIO**: MLflow Artifact Storage (S3 호환)
- **PostgreSQL**: MLflow / Airflow 메타데이터 (DB 분리)
- **Agent**: LangChain + LangGraph 기반 (데이터/인프라/사후보정)

### 외부 LLM
- 8번 서버 OpenAI 호환 endpoint를 사용한다.
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`은 `.env`로만 관리한다.
- 코드에 하드코딩 금지. 모든 호출은 `agents/common/llm_client.py`(추후 작성)를 거친다.

---

## 2. 확정된 결정사항

| 항목 | 결정 | 비고 |
|---|---|---|
| MLflow Artifact Storage | **MinIO** | S3 호환, 컨테이너로 띄움 |
| Docker Network | **단일 network** (`dais_network`) | 단순성 우선 |
| DB 분리 | mlflow_db / airflow_db (같은 Postgres 인스턴스, DB만 분리) | 초기 단계에선 인스턴스 하나로 충분 |
| Agent 간 통신 | **없음** (독립 실행) | 각 Agent는 자체 entrypoint를 가짐 |
| Agent Tracing | **LangSmith** | `LANGCHAIN_*` 환경변수로 활성화 |
| 코드 작성 범위 (현재) | 인프라 + Agent 환경 구축까지 | Agent 로직 코드는 다음 단계에서 |

---

## 3. 파일 구조

```
dais_agent/
├── CLAUDE.md                    # 본 계획서 (single source of truth)
├── README.md                    # 5분 안에 실행 가능한 진입점
├── Makefile                     # make up / down / logs / ps 등
├── .env.example                 # 환경변수 템플릿 (실제 .env는 gitignore)
├── .gitignore
├── pyproject.toml               # Agent 의존성 (uv 권장)
│
├── infra/                       # MLOps 인프라 정의
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml   # 개발용 오버라이드 (포트 노출 등)
│   ├── postgres/
│   │   └── init/
│   │       └── 01-create-databases.sh   # mlflow_db, airflow_db 생성
│   ├── mlflow/
│   │   └── Dockerfile           # MLflow + boto3 (MinIO 연동)
│   ├── airflow/
│   │   ├── Dockerfile
│   │   ├── dags/                # 호스트 마운트
│   │   └── requirements.txt
│   ├── minio/
│   │   └── init.sh              # mlflow-artifacts 버킷 자동 생성
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── provisioning/
│           ├── datasources/     # Prometheus 자동 등록
│           └── dashboards/
│
├── ml/                          # MLflow 학습/배포 예시
│   ├── train/                   # 학습 스크립트 (train.py)
│   ├── inference/               # 배치 추론 스크립트 (predict.py)
│   ├── serve/                   # 모델 서빙 가이드 (별도 컨테이너 X)
│   └── notebooks/               # 실험용 (선택)
│
├── agents/                      # Agent 코드 (현재 단계에선 골격만)
│   ├── common/
│   │   ├── __init__.py
│   │   ├── llm_client.py        # ← Phase 4에서 채움
│   │   ├── tracing.py           # ← LangSmith 설정
│   │   ├── prompts/
│   │   └── tools/
│   ├── data_agent/
│   │   ├── __init__.py
│   │   ├── graph.py             # 빈 파일
│   │   └── api.py               # 빈 파일
│   ├── infra_agent/
│   │   └── (동일 구조)
│   └── correction_agent/
│       └── (동일 구조)
│
├── tests/
│   ├── unit/
│   └── integration/
│       └── test_llm_connectivity.py   # LLM endpoint 연결 확인용
│
├── scripts/                     # 운영 스크립트
│   └── healthcheck.sh
│
└── docs/
    ├── ARCHITECTURE.md          # 전체 그림 + Mermaid 다이어그램
    ├── PORTS.md                 # 포트 정리
    ├── SETUP.md                 # 상세 설치 가이드
    ├── AGENTS.md                # 각 Agent의 책임/입출력 (구체화는 다음 단계)
    └── MLFLOW_WORKFLOW.md       # 학습 → 등록 → 배포 흐름
```

### 분리 원칙
- `infra/` = 인프라 정의만. Agent 코드 없음.
- `agents/` = Agent 로직만. 인프라 설정 없음.
- `ml/` = MLflow 학습/배포 코드. Agent와 독립.
- `docs/` = 사람이 읽는 문서. 자동 생성 X.

---

## 4. 포트 할당 (`docs/PORTS.md`에도 동일하게 기록)

| 서비스 | 호스트 포트 | 컨테이너 포트 | 외부 노출 | 비고 |
|---|---|---|---|---|
| MLflow UI | 5000 | 5000 | O | |
| Airflow Webserver | 8080 | 8080 | O | |
| Grafana | 3000 | 3000 | O | |
| Prometheus | 9090 | 9090 | O | |
| MinIO API | 9000 | 9000 | O | |
| MinIO Console | 9001 | 9001 | O | |
| PostgreSQL | 5432 | 5432 | △ (dev only) | prod에선 노출 X |
| **Agent API Gateway** | 8000 | 8000 | O | 추후 사용 예약 |
| Data Agent | 8001 | - | X | 내부, 추후 사용 예약 |
| Infra Agent | 8002 | - | X | 내부, 추후 사용 예약 |
| Correction Agent | 8003 | - | X | 내부, 추후 사용 예약 |

**규칙**: 새 서비스를 추가할 때는 반드시 이 표를 먼저 갱신한다. 8080은 Airflow 점유 → Agent는 8000번대를 쓰되 8080 회피.

---

## 5. 단계별 실행 계획

> 각 Phase가 완료되면 해당 체크리스트의 모든 항목이 ✅ 되어야 다음 Phase로 이동.

---

### Phase 1: 프로젝트 스켈레톤 만들기 ✅ 완료

**목표**: 빈 폴더 구조와 협업 기반 문서를 갖춘다. 아직 아무것도 동작하지 않아도 됨.

- [x] 위 "3. 파일 구조"의 디렉토리/빈 파일 생성
- [x] `.gitignore` 작성 (Python, Docker, .env, __pycache__, MLflow artifacts 로컬 캐시 등)
- [x] `.env.example` 작성 — 모든 환경변수 키만 (값은 placeholder)
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`
  - `MLFLOW_TRACKING_URI`
  - `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET`
  - `AIRFLOW_*`
  - `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
  - `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`
- [x] `README.md` 작성 — Quick Start (clone → cp .env.example .env → make up → 접속 URL 표)
- [x] `Makefile` 작성 — `up`, `down`, `logs`, `ps`, `restart`, `clean` 타겟
- [x] `docs/PORTS.md` 작성 (위 표 그대로)
- [x] `docs/ARCHITECTURE.md` 골격 (Mermaid 다이어그램 포함)
- [x] `docs/AGENTS.md` 골격 (각 Agent의 책임/입출력은 TBD로 표시)
- [x] `docs/MLFLOW_WORKFLOW.md` 골격
- [x] `docs/SETUP.md` 골격

**완료 기준**: 신규 팀원이 README만 보고 어디에 무엇이 있는지 파악 가능.

---

### Phase 2: MLOps 인프라 구축 ✅ 완료 (2026-05-06 사용자 검증 완료)

**목표**: `make up` 한 번으로 모든 서비스가 뜨고, 각 UI 접속이 가능하다.

- [x] `infra/postgres/init/01-create-databases.sh` — mlflow_db, airflow_db 생성
- [x] MinIO 버킷 자동 생성 — compose 의 `minio-init` 서비스가 mc 로 생성 (별도 init.sh 불필요)
- [x] `infra/mlflow/Dockerfile` — MLflow 2.18.0 + psycopg2-binary + boto3
- [x] `infra/airflow/Dockerfile` — Airflow 2.10.3 + mlflow + boto3
- [x] `infra/prometheus/prometheus.yml` — self-scrape (Phase 3 에서 target 확장)
- [x] `infra/grafana/provisioning/datasources/prometheus.yml` — Prometheus 자동 등록
- [x] `infra/grafana/provisioning/dashboards/dashboards.yml` — 대시보드 provider 등록
- [x] `infra/docker-compose.yml` 작성
  - 단일 network: `dais_network` ✅
  - 서비스: postgres / minio / minio-init / mlflow / airflow-init / airflow-webserver / airflow-scheduler / prometheus / grafana ✅
  - 모든 서비스에 `healthcheck` 정의 (init 컨테이너 제외) ✅
  - `depends_on: condition: service_healthy / service_completed_successfully` 사용 ✅
- [x] `infra/docker-compose.dev.yml` — Postgres 호스트 노출 등 dev 오버라이드
- [x] **볼륨/마운트 정의** (compose 하단 주석 참고):
  - `postgres_data` → `/var/lib/postgresql/data` ✅
  - `minio_data` → `/data` ✅
  - `mlflow_artifacts` → MinIO 위임 (별도 볼륨 없음) ✅
  - `./infra/airflow/dags` → `/opt/airflow/dags` (호스트 마운트) ✅
  - `airflow_logs` → `/opt/airflow/logs` ✅
  - `prometheus_data` → `/prometheus` ✅
  - `grafana_data` → `/var/lib/grafana` ✅
- [x] **(사용자 검증)** `make up` 으로 전체 기동 확인
- [x] **(사용자 검증)** 접속 확인: MLflow(5000), Airflow(8080), Grafana(3000), MinIO Console(9001)

**검증 절차** (사용자 환경에서):
```bash
make init                    # .env 생성
# .env 에서 비밀번호와 AIRFLOW__CORE__FERNET_KEY 채우기
#   FERNET_KEY 생성: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
make up
make ps                      # 모든 서비스 healthy 확인
# 브라우저로 5000, 8080, 3000, 9001 접속
```

**완료 기준**: 모든 UI 접속 가능 + MLflow에서 더미 run 1개 기록 시 MinIO에 artifact 저장 확인.

---

### Phase 3: MLflow 학습 → 배포 워크플로 🟡 코드 작성 완료 / 사용자 검증 필요

**목표**: 실제 모델을 학습→등록→배포(서빙)하는 흐름을 파이프라인으로 만든다.

- [x] `ml/train/train.py` — sklearn Iris + RandomForest (데모)
  - MLflow Tracking 으로 metric/param/model 기록 ✅
  - `registered_model_name` 으로 Registry 자동 등록 ✅
- [x] `ml/inference/predict.py` — Production 모델 로드 + 배치 추론
- [x] `ml/serve/README.md` — `mlflow models serve` 가이드 (별도 컨테이너는 미생성)
- [x] `infra/airflow/dags/train_pipeline.py` — train → promote (acc ≥ 0.9 시 자동 승격)
- [x] `infra/airflow/dags/inference_pipeline.py` — @hourly Production 모델로 추론
- [x] `infra/airflow/requirements.txt` — scikit-learn 1.5.2 추가
- [x] `infra/docker-compose.yml` — `../ml:/opt/dais/ml:ro` 마운트 추가 (3개 airflow 서비스)
- [x] `docs/MLFLOW_WORKFLOW.md` 본문 작성

**검증 절차** (사용자 환경에서):
```bash
make build && make up                   # airflow에 sklearn 추가됐으니 재빌드
# 1) Airflow UI 에서 train_pipeline 활성화 + 수동 트리거
# 2) MLflow UI: iris_rf 실험에 run 생성 + Models 에서 Production stage 확인
# 3) MinIO Console: mlflow-artifacts 버킷에 모델 파일 확인
# 4) inference_pipeline 활성화 + 트리거 → task log 에서 예측 결과 확인
```

**완료 기준**: Airflow에서 학습 DAG 트리거 → MLflow Registry에 모델 등록 → 추론 DAG가 그 모델을 가져다 사용.

---

### Phase 4: Agent 개발 환경 구축 (⚠️ Agent 로직 코드 작성 X)

**목표**: Agent 코드를 바로 작성할 수 있는 골격과 의존성, LLM 연결을 준비한다.
**작성하지 않는 것**: 각 Agent의 LangGraph 노드/도구/프롬프트 로직.

- [ ] `pyproject.toml` 작성 — 의존성:
  - `langchain`, `langchain-openai`, `langgraph`, `langsmith`
  - `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`
  - `httpx`, `tenacity`
  - dev: `ruff`, `mypy`, `pytest`, `pytest-asyncio`
- [ ] `agents/common/__init__.py`
- [ ] `agents/common/llm_client.py` — **최소한만**:
  - `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` 환경변수를 읽어 `ChatOpenAI` 인스턴스를 반환하는 factory 함수 1개
  - 그 외 로직 X
- [ ] `agents/common/tracing.py` — LangSmith 활성화 헬퍼 (env 기반)
- [ ] 각 Agent 폴더에 빈 `graph.py`, `api.py`, `__init__.py` (placeholder만)
- [ ] `tests/integration/test_llm_connectivity.py` — 8번 서버 LLM 호출이 성공하는지만 확인
- [ ] `agents/common/prompts/`, `agents/common/tools/` 빈 디렉토리 (`.gitkeep`)
- [ ] `docs/AGENTS.md` 본문 작성 — 각 Agent의 책임/trigger/입출력 스키마 (TBD 해소)

**완료 기준**:
1. `uv sync` (또는 `pip install -e .`) 성공
2. `pytest tests/integration/test_llm_connectivity.py` 통과 (LLM 응답 받음)
3. LangSmith에 trace 1건 기록 확인

---

## 6. 다음 단계 (이 계획서의 범위 밖)

Phase 4 완료 후 사용자가 직접 시작할 작업:
- 각 Agent의 LangGraph 그래프 설계 및 노드 구현
- Agent별 Tool (MLflow API 호출, DB 조회, Airflow 트리거 등) 작성
- Agent별 FastAPI 엔드포인트 구현
- Agent를 컨테이너화하여 `infra/docker-compose.yml`에 통합

---

## 7. 작업 규칙 (Claude Code에게)

- **Phase 순서 엄수**: Phase 1이 끝나기 전에 Phase 2를 시작하지 않는다.
- **체크리스트 갱신**: 한 항목이 끝날 때마다 이 문서의 `[ ]`를 `[x]`로 바꾼다.
- **결정 변경 시**: 코드보다 이 문서를 먼저 수정. "2. 확정된 결정사항" 표를 갱신.
- **Agent 로직 작성 금지**: Phase 4 범위는 *환경 구축*까지. 사용자가 명시적으로 요청하기 전까지 LangGraph 노드/프롬프트/도구 구현 X.
- **포트 추가 시**: `docs/PORTS.md`와 본 문서 4번 표를 동시 갱신.
- **Secret**: `.env`는 절대 커밋 금지. 새 환경변수는 반드시 `.env.example`에도 추가.
