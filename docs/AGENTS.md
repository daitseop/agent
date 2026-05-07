# Agents 명세

> 본 문서는 골격이다. Phase 4 에서 본문이 채워지고, Agent 로직 구현 단계에서 입출력 스키마가 확정된다.
> 현재 모든 Agent는 **독립적으로 실행**되며 서로 통신하지 않는다.

---

## 공통 사항

| 항목 | 값 |
|---|---|
| 프레임워크 | LangChain + LangGraph |
| LLM | 8번 서버 (`LLM_BASE_URL`) — OpenAI 호환 endpoint |
| Tracing | LangSmith (`LANGCHAIN_*` 환경변수, 자동 활성화) |
| LLM 클라이언트 | `agents.common.get_llm()` factory (Phase 4 완료) |
| Tracing 헬퍼 | `agents.common.configure_tracing()` |
| API 프레임워크 | FastAPI |
| 통신 | Agent 간 통신 없음. 각자 외부 trigger 로 동작 |

### LLM 호출 예시

```python
from agents.common import get_llm

llm = get_llm()             # .env 의 LLM_* 자동 사용
resp = llm.invoke("hello")  # LangSmith 에 자동 trace 기록
```

---

## 1. Data Agent

| 항목 | 내용 |
|---|---|
| 책임 | TBD — 데이터 관리 (수집/검증/전처리 등) |
| Trigger | TBD (HTTP / 스케줄 / 수동) |
| Input Schema | TBD |
| Output Schema | TBD |
| 외부 시스템 의존 | TBD (Postgres / MinIO / MLflow ?) |
| 포트 | 8001 |

---

## 2. Infra Agent

| 항목 | 내용 |
|---|---|
| 책임 | TBD — 인프라 관리 (컨테이너 상태/리소스/스케줄 등) |
| Trigger | TBD |
| Input Schema | TBD |
| Output Schema | TBD |
| 외부 시스템 의존 | TBD |
| 포트 | 8002 |

---

## 3. Correction Agent

| 항목 | 내용 |
|---|---|
| 책임 | TBD — 사후 보정 (모델 출력 보정/검증/재학습 트리거 등) |
| Trigger | TBD |
| Input Schema | TBD |
| Output Schema | TBD |
| 외부 시스템 의존 | TBD |
| 포트 | 8003 |

---

## 입출력 스키마 작성 규칙 (구체화 시)

각 Agent가 구현 단계에 들어가면 다음을 명시한다.

1. **Trigger 방식**: HTTP / Cron / Event
2. **Input**: Pydantic 모델 (필드명, 타입, 필수 여부, 예시)
3. **Output**: 동일
4. **부수효과 (Side Effects)**: 어떤 외부 시스템을 변경하는가
5. **재시도 정책**: tenacity 등으로 처리할 실패 케이스
6. **LLM 호출 횟수 추정**: 토큰/요청 수 (외부 LLM 서버 부하 관리)
