.PHONY: help up down logs ps restart clean build init env-check

COMPOSE := docker compose -f infra/docker-compose.yml --env-file .env

help:  ## 사용 가능한 명령 목록
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

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

clean:  ## 컨테이너 + 볼륨 삭제 (데이터 모두 삭제됨, 주의)
	$(COMPOSE) down -v

init:  ## 첫 실행: .env 파일 생성
	@test -f .env && echo ".env 이미 존재" || (cp .env.example .env && echo "✅ .env 생성됨. 값을 채운 뒤 'make up'")
