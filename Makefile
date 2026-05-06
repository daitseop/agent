.PHONY: help up down logs ps restart clean build init env-check psql airflow-shell mlflow-logs

# .env 가 있으면 모든 변수를 Makefile 에 자동 로딩 (psql 등 헬퍼에서 사용)
ifneq (,$(wildcard .env))
include .env
export
endif

COMPOSE := docker compose -f infra/docker-compose.yml --env-file .env

help:  ## 사용 가능한 명령 목록
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

env-check:  ## .env 파일 존재 확인
	@test -f .env || (echo "❌ .env 가 없습니다.  cp .env.example .env  먼저 실행하세요." && exit 1)
	@echo "✅ .env OK"

up: env-check  ## 전체 스택 기동
	$(COMPOSE) up -d

down:  ## 전체 스택 종료
	$(COMPOSE) down

logs:  ## 로그 follow
	$(COMPOSE) logs -f

ps:  ## 컨테이너 상태
	$(COMPOSE) ps

restart:  ## 재시작
	$(COMPOSE) restart

build:  ## 이미지 빌드
	$(COMPOSE) build

clean:  ## 컨테이너 + 볼륨 모두 삭제 (데이터 영구 손실, 주의)
	$(COMPOSE) down -v

reset-postgres:  ## postgres 볼륨만 삭제 후 재기동 (.env 의 USER/PW 변경 시 사용)
	$(COMPOSE) down
	docker volume rm dais_postgres_data || true
	$(COMPOSE) up -d

init:  ## 첫 실행: .env 파일 생성
	@test -f .env && echo ".env 이미 존재" || (cp .env.example .env && echo "✅ .env 생성됨. 값을 채운 뒤 'make up'")

psql:  ## postgres 셸 접속 (.env 의 POSTGRES_USER 자동 사용)
	$(COMPOSE) exec postgres psql -U $(POSTGRES_USER) -d postgres

airflow-shell:  ## airflow webserver 컨테이너 셸
	$(COMPOSE) exec airflow-webserver bash

mlflow-logs:  ## mlflow 로그만 보기
	$(COMPOSE) logs -f mlflow
