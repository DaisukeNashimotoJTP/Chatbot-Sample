# =============================================================================
# Chat Service Makefile
# =============================================================================

.PHONY: help setup start stop restart clean logs test lint migrate seed backup restore set-env unset-env

# デフォルトターゲット
.DEFAULT_GOAL := help

# カラー定義
RED    := \033[31m
GREEN  := \033[32m
YELLOW := \033[33m
BLUE   := \033[34m
RESET  := \033[0m

# 変数
BACKEND_DIR := backend
FRONTEND_DIR := frontend
COMPOSE_FILE := docker-compose.yml

# ヘルプ表示
help: ## このヘルプメッセージを表示
	@echo "$(BLUE)Chat Service Development Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "$(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(RESET)"
	@echo "  make setup     # 初期セットアップ"
	@echo "  make start     # 開発環境起動"
	@echo "  make test      # テスト実行"
	@echo ""

# 前提条件チェック
check-prerequisites: ## 前提条件をチェック
	@echo "$(BLUE)前提条件をチェックしています...$(RESET)"
	@command -v docker >/dev/null 2>&1 || (echo "$(RED)Docker がインストールされていません$(RESET)" && exit 1)
	@command -v docker-compose >/dev/null 2>&1 || (echo "$(RED)Docker Compose がインストールされていません$(RESET)" && exit 1)
	@echo "$(GREEN)前提条件チェック完了$(RESET)"

# 初期セットアップ
setup: check-prerequisites ## 初期セットアップを実行
	@echo "$(BLUE)初期セットアップを開始します...$(RESET)"
	@echo "$(BLUE)Dockerネットワークを作成しています...$(RESET)"
	@docker network create chat_network 2>/dev/null || echo "$(YELLOW)ネットワークは既に存在します$(RESET)"
	@echo "$(BLUE)Dockerイメージをビルドしています...$(RESET)"
	@docker-compose build
	@echo "$(BLUE)データベースとRedisを起動しています...$(RESET)"
	@docker-compose up -d postgres redis
	@echo "$(BLUE)データベースの起動を待機しています...$(RESET)"
	@sleep 15
	@echo "$(BLUE)データベースマイグレーションを実行しています...$(RESET)"
	@docker-compose run --rm backend alembic upgrade head
	@echo "$(BLUE)テストデータを投入しています...$(RESET)"
	@docker-compose run --rm backend python scripts/seed_data.py
	@echo "$(GREEN)セットアップが完了しました$(RESET)"
	@echo "$(YELLOW)開発を開始するには: make start$(RESET)"

# 開発環境起動
start: ## 開発環境を起動
	@echo "$(BLUE)開発環境を起動しています...$(RESET)"
	@docker-compose up -d
	@echo "$(GREEN)開発環境が起動しました$(RESET)"
	@echo "$(YELLOW)フロントエンド: http://localhost:3000$(RESET)"
	@echo "$(YELLOW)バックエンドAPI: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)API ドキュメント: http://localhost:8000/v1/docs$(RESET)"

# 開発環境停止
stop: ## 開発環境を停止
	@echo "$(BLUE)開発環境を停止しています...$(RESET)"
	@docker-compose down
	@echo "$(GREEN)開発環境を停止しました$(RESET)"

# 開発環境再起動
restart: ## 開発環境を再起動
	@echo "$(BLUE)開発環境を再起動しています...$(RESET)"
	@docker-compose restart
	@echo "$(GREEN)開発環境を再起動しました$(RESET)"

# クリーンアップ
clean: ## クリーンアップを実行
	@echo "$(YELLOW)クリーンアップを実行します（データが削除される可能性があります）$(RESET)"
	@read -p "続行しますか？ (y/N): " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)クリーンアップを開始します...$(RESET)"; \
		docker-compose down -v --remove-orphans; \
		docker system prune -f; \
		echo "$(GREEN)クリーンアップが完了しました$(RESET)"; \
	else \
		echo "$(YELLOW)クリーンアップをキャンセルしました$(RESET)"; \
	fi

# ログ表示
logs: ## ログを表示
	@docker-compose logs -f

logs-backend: ## バックエンドログを表示
	@docker-compose logs -f backend

logs-frontend: ## フロントエンドログを表示
	@docker-compose logs -f frontend

logs-docker: ## Dockerログを表示
	@docker-compose logs -f

# テスト関連
test: ## 全テストを実行
	@echo "$(BLUE)テストを実行しています...$(RESET)"
	@docker-compose run --rm backend pytest --cov=app --cov-report=html
	@docker-compose run --rm frontend npm test -- --coverage --watchAll=false
	@echo "$(GREEN)全テストが完了しました$(RESET)"

test-backend: ## バックエンドテストのみ実行
	@echo "$(BLUE)バックエンドテストを実行しています...$(RESET)"
	@docker-compose run --rm backend pytest --cov=app --cov-report=html

test-frontend: ## フロントエンドテストのみ実行
	@echo "$(BLUE)フロントエンドテストを実行しています...$(RESET)"
	@docker-compose run --rm frontend npm test -- --watchAll=false

test-e2e: ## E2Eテストを実行
	@echo "$(BLUE)E2Eテストを実行しています...$(RESET)"
	@docker-compose run --rm frontend npm run test:e2e

# コード品質チェック
lint: ## コード品質チェックを実行
	@echo "$(BLUE)コード品質チェックを実行しています...$(RESET)"
	@docker-compose run --rm backend black app/ && \
		docker-compose run --rm backend isort app/ && \
		docker-compose run --rm backend flake8 app/ && \
		docker-compose run --rm backend mypy app/
	@docker-compose run --rm frontend npm run lint:fix && \
		docker-compose run --rm frontend npm run format && \
		docker-compose run --rm frontend npm run type-check
	@echo "$(GREEN)コード品質チェックが完了しました$(RESET)"

lint-backend: ## バックエンドのリントのみ実行
	@echo "$(BLUE)バックエンドのリントを実行しています...$(RESET)"
	@docker-compose run --rm backend black app/
	@docker-compose run --rm backend isort app/
	@docker-compose run --rm backend flake8 app/
	@docker-compose run --rm backend mypy app/

lint-frontend: ## フロントエンドのリントのみ実行
	@echo "$(BLUE)フロントエンドのリントを実行しています...$(RESET)"
	@docker-compose run --rm frontend npm run lint:fix
	@docker-compose run --rm frontend npm run format
	@docker-compose run --rm frontend npm run type-check

# データベース関連
migrate: ## データベースマイグレーションを実行
	@echo "$(BLUE)データベースマイグレーションを実行しています...$(RESET)"
	@docker-compose run --rm backend alembic upgrade head

migrate-create: ## 新しいマイグレーションファイルを作成
	@echo "$(BLUE)新しいマイグレーションファイルを作成しています...$(RESET)"
	@read -p "マイグレーション名を入力してください: " migration_name; \
		docker-compose run --rm backend alembic revision --autogenerate -m "$$migration_name"

migrate-downgrade: ## マイグレーションを1つ戻す
	@echo "$(BLUE)マイグレーションを1つ戻しています...$(RESET)"
	@docker-compose run --rm backend alembic downgrade -1

migrate-history: ## マイグレーション履歴を表示
	@docker-compose run --rm backend alembic history

seed: ## テストデータを投入
	@echo "$(BLUE)テストデータを投入しています...$(RESET)"
	@docker-compose run --rm backend python scripts/seed_data.py

# バックアップ・リストア
backup: ## データベースバックアップを作成
	@echo "$(BLUE)データベースバックアップを作成しています...$(RESET)"
	@mkdir -p backups
	@timestamp=$$(date +"%Y%m%d_%H%M%S"); \
		backup_file="backups/chat_db_backup_$$timestamp.sql"; \
		docker-compose exec postgres pg_dump -U chat_user chat_db > $$backup_file; \
		echo "$(GREEN)バックアップを作成しました: $$backup_file$(RESET)"

restore: ## データベースを復元（要バックアップファイル指定）
	@echo "$(YELLOW)使用方法: make restore FILE=path/to/backup.sql$(RESET)"
	@if [ -z "$(FILE)" ]; then echo "$(RED)バックアップファイルを指定してください$(RESET)"; exit 1; fi
	@if [ ! -f "$(FILE)" ]; then echo "$(RED)バックアップファイルが見つかりません: $(FILE)$(RESET)"; exit 1; fi
	@echo "$(YELLOW)データベースを復元します（既存のデータは削除されます）$(RESET)"
	@read -p "続行しますか？ (y/N): " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)データベースを復元しています...$(RESET)"; \
		docker-compose exec postgres dropdb -U chat_user chat_db; \
		docker-compose exec postgres createdb -U chat_user chat_db; \
		docker-compose exec -T postgres psql -U chat_user chat_db < $(FILE); \
		echo "$(GREEN)データベースの復元が完了しました$(RESET)"; \
	else \
		echo "$(YELLOW)復元をキャンセルしました$(RESET)"; \
	fi

# Docker関連
docker-build: ## Dockerイメージをビルド
	@echo "$(BLUE)Dockerイメージをビルドしています...$(RESET)"
	@docker-compose build

docker-pull: ## Dockerイメージをプル
	@echo "$(BLUE)Dockerイメージをプルしています...$(RESET)"
	@docker-compose pull

docker-ps: ## Dockerコンテナの状態を表示
	@docker-compose ps

docker-clean: ## 未使用のDockerリソースを削除
	@echo "$(BLUE)未使用のDockerリソースを削除しています...$(RESET)"
	@docker system prune -f

# データベース接続
db-connect: ## PostgreSQLに接続
	@echo "$(BLUE)PostgreSQLに接続しています...$(RESET)"
	@docker-compose exec postgres psql -U chat_user -d chat_db

redis-connect: ## Redisに接続
	@echo "$(BLUE)Redisに接続しています...$(RESET)"
	@docker-compose exec redis redis-cli

# 開発用ユーティリティ
install-backend: ## バックエンド依存関係をインストール
	@echo "$(BLUE)バックエンド依存関係をインストールしています...$(RESET)"
	@docker-compose run --rm backend pip install -r requirements.txt -r requirements-dev.txt

install-frontend: ## フロントエンド依存関係をインストール
	@echo "$(BLUE)フロントエンド依存関係をインストールしています...$(RESET)"
	@docker-compose run --rm frontend npm install

update-deps: ## 依存関係を更新
	@echo "$(BLUE)依存関係を更新しています...$(RESET)"
	@docker-compose run --rm backend pip-compile requirements.in && pip-compile requirements-dev.in
	@docker-compose run --rm frontend npm update

# 本番用コマンド
build-prod: ## 本番用ビルドを実行
	@echo "$(BLUE)本番用ビルドを実行しています...$(RESET)"
	@docker-compose -f docker-compose.prod.yml build

deploy-prod: ## 本番環境にデプロイ
	@echo "$(BLUE)本番環境にデプロイしています...$(RESET)"
	@if [ ! -f ".env.prod" ]; then echo "$(RED).env.prodファイルが見つかりません。.env.prod.exampleを参考に作成してください$(RESET)"; exit 1; fi
	@docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

start-prod: ## 本番環境を起動
	@echo "$(BLUE)本番環境を起動しています...$(RESET)"
	@if [ ! -f ".env.prod" ]; then echo "$(RED).env.prodファイルが見つかりません。.env.prod.exampleを参考に作成してください$(RESET)"; exit 1; fi
	@docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

stop-prod: ## 本番環境を停止
	@echo "$(BLUE)本番環境を停止しています...$(RESET)"
	@docker-compose -f docker-compose.prod.yml down

# セキュリティ
security-check: ## セキュリティチェックを実行
	@echo "$(BLUE)セキュリティチェックを実行しています...$(RESET)"
	@docker-compose run --rm backend safety check
	@docker-compose run --rm frontend npm audit

# ドキュメント生成
docs: ## ドキュメントを生成
	@echo "$(BLUE)ドキュメントを生成しています...$(RESET)"
	@docker-compose run --rm backend sphinx-build -b html docs docs/_build

# 環境情報表示
info: ## 環境情報を表示
	@echo "$(BLUE)=== 環境情報 ===$(RESET)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "Node.js: $$(node --version)"
	@echo "npm: $$(npm --version)"
	@echo "Python: $$(python3 --version)"
	@echo ""
	@echo "$(BLUE)=== サービス状態 ===$(RESET)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)=== ディスク使用量 ===$(RESET)"
	@docker system df

# 開発サーバー個別起動
start-db: ## データベースのみ起動
	@echo "$(BLUE)データベースを起動しています...$(RESET)"
	@docker-compose up -d postgres redis

start-backend: ## バックエンドのみ起動
	@echo "$(BLUE)バックエンドを起動しています...$(RESET)"
	@docker-compose up -d backend

start-frontend: ## フロントエンドのみ起動
	@echo "$(BLUE)フロントエンドを起動しています...$(RESET)"
	@docker-compose up -d frontend

# 便利なエイリアス
dev: start ## 開発環境を起動（startのエイリアス）
down: stop ## 開発環境を停止（stopのエイリアス）
reset: clean setup ## 環境をリセット
full-test: lint test ## 全品質チェックとテストを実行