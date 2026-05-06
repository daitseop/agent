# dais_agent

최소한의 MLOps 환경 위에서 동작하는 **Agent 플랫폼**.
MLflow / Airflow / Grafana / MinIO 인프라와 LangChain·LangGraph 기반 Agent를 함께 제공한다.

> 프로젝트 전체 계획은 [CLAUDE.md](CLAUDE.md) 를 먼저 읽을 것. **Single source of truth**.

---

## Quick Start (5분 안에 실행)

```bash
# 1) 저장소 받기
git clone <repo-url> dais_agent
cd dais_agent

# 2) 환경변수 준비
make init          # .env 생성
# .env 파일을 열어 비밀번호/키 채우기

# 3) 전체 스택 기동
make up

# 4) 상태 확인
make ps
make logs
```

기동 후 접속 URL:

| 서비스 | URL | 비고 |
|---|---|---|
| MLflow UI | http://203.250.72.36:5000 | 모델 학습/등록 |
| Airflow | http://203.250.72.36:8080 | 파이프라인 |
| Grafana | http://203.250.72.36:3000 | 모니터링 |
| Prometheus | http://203.250.72.36:9090 | 메트릭 수집 |
| MinIO Console | http://203.250.72.36:9001 | Artifact Storage |

> **포트 전체 정리**: [docs/PORTS.md](docs/PORTS.md)

---

## 디렉토리 구조

```
dais_agent/
├── CLAUDE.md         # 프로젝트 single source of truth
├── README.md         # 진입점 (현재 파일)
├── Makefile          # 단축 명령
├── .env.example      # 환경변수 템플릿
│
├── infra/            # MLOps 인프라 (Docker Compose)
├── ml/               # MLflow 학습/배포 코드
├── agents/           # LangChain/LangGraph Agent
│   ├── common/       # 공용 LLM 클라이언트, 프롬프트, 도구
│   ├── data_agent/
│   ├── infra_agent/
│   └── correction_agent/
├── tests/
├── scripts/
└── docs/             # 아키텍처 / 포트 / 워크플로 문서
```

**분리 원칙**
- `infra/` = 인프라 정의만
- `agents/` = Agent 로직만
- `ml/` = MLflow 학습/배포 코드
- `docs/` = 사람이 읽는 문서

---

## 문서

| 문서 | 내용 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 프로젝트 계획서 (Phase 진행상황) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 시스템 아키텍처 |
| [docs/PORTS.md](docs/PORTS.md) | 포트 할당 정리 |
| [docs/SETUP.md](docs/SETUP.md) | 상세 설치 가이드 |
| [docs/MLFLOW_WORKFLOW.md](docs/MLFLOW_WORKFLOW.md) | 학습 → 등록 → 배포 흐름 |
| [docs/AGENTS.md](docs/AGENTS.md) | 각 Agent의 책임/입출력 |

---

## 자주 쓰는 명령

```bash
make help       # 전체 명령 목록
make up         # 기동
make down       # 종료
make logs       # 로그
make ps         # 상태
make clean      # 볼륨 포함 완전 삭제 (주의)
```

---

## 진행 상황

현재 **Phase 1: 프로젝트 스켈레톤** 완료.
다음 Phase는 [CLAUDE.md](CLAUDE.md) 의 "5. 단계별 실행 계획" 참고.
