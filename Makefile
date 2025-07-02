# =============================================================================
# Chat Service Makefile
# =============================================================================

.PHONY: help setup start stop restart clean logs test lint migrate seed backup restore

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
SCRIPT_DIR := scripts

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
	@command -v node >/dev/null 2>&1 || (echo "$(RED)Node.js がインストールされていません$(RESET)" && exit 1)
	@command -v python3 >/dev/null 2>&1 || (echo "$(RED)Python 3 がインストールされていません$(RESET)" && exit 1)
	@echo "$(GREEN)前提条件チェック完了$(RESET)"

# 初期セットアップ
setup: check-prerequisites ## 初期セットアップを実行
	@echo "$(BLUE)初期セットアップを開始します...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh setup
	@echo "$(GREEN)セットアップが完了しました$(RESET)"

# 開発環境起動
start: ## 開発環境を起動
	@echo "$(BLUE)開発環境を起動しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh start

# 開発環境停止
stop: ## 開発環境を停止
	@echo "$(BLUE)開発環境を停止しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh stop

# 開発環境再起動
restart: ## 開発環境を再起動
	@echo "$(BLUE)開発環境を再起動しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh restart

# クリーンアップ
clean: ## クリーンアップを実行
	@echo "$(YELLOW)クリーンアップを実行します$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh clean

# ログ表示
logs: ## ログを表示
	@./$(SCRIPT_DIR)/dev.sh logs

logs-backend: ## バックエンドログを表示
	@./$(SCRIPT_DIR)/dev.sh logs backend

logs-frontend: ## フロントエンドログを表示
	@./$(SCRIPT_DIR)/dev.sh logs frontend

logs-docker: ## Dockerログを表示
	@./$(SCRIPT_DIR)/dev.sh logs docker

# テスト関連
test: ## 全テストを実行
	@echo "$(BLUE)テストを実行しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh test

test-backend: ## バックエンドテストのみ実行
	@echo "$(BLUE)バックエンドテストを実行しています...$(RESET)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && pytest

test-frontend: ## フロントエンドテストのみ実行
	@echo "$(BLUE)フロントエンドテストを実行しています...$(RESET)"
	@cd $(FRONTEND_DIR) && npm test -- --watchAll=false

test-e2e: ## E2Eテストを実行
	@echo "$(BLUE)E2Eテストを実行しています...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run test:e2e

# コード品質チェック
lint: ## コード品質チェックを実行
	@echo "$(BLUE)コード品質チェックを実行しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh lint

lint-backend: ## バックエンドのリントのみ実行
	@echo "$(BLUE)バックエンドのリントを実行しています...$(RESET)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && black app/ && isort app/ && flake8 app/ && mypy app/

lint-frontend: ## フロントエンドのリントのみ実行
	@echo "$(BLUE)フロントエンドのリントを実行しています...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run lint:fix && npm run format && npm run type-check

# データベース関連
migrate: ## データベースマイグレーションを実行
	@./$(SCRIPT_DIR)/dev.sh migrate upgrade

migrate-create: ## 新しいマイグレーションファイルを作成
	@./$(SCRIPT_DIR)/dev.sh migrate create

migrate-downgrade: ## マイグレーションを1つ戻す
	@./$(SCRIPT_DIR)/dev.sh migrate downgrade

migrate-history: ## マイグレーション履歴を表示
	@./$(SCRIPT_DIR)/dev.sh migrate history

seed: ## テストデータを投入
	@echo "$(BLUE)テストデータを投入しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh seed

# バックアップ・リストア
backup: ## データベースバックアップを作成
	@echo "$(BLUE)データベースバックアップを作成しています...$(RESET)"
	@./$(SCRIPT_DIR)/dev.sh backup

restore: ## データベースを復元（要バックアップファイル指定）
	@echo "$(YELLOW)使用方法: make restore FILE=path/to/backup.sql$(RESET)"
	@if [ -z "$(FILE)" ]; then echo "$(RED)バックアップファイルを指定してください$(RESET)"; exit 1; fi
	@./$(SCRIPT_DIR)/dev.sh restore $(FILE)

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
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt

install-frontend: ## フロントエンド依存関係をインストール
	@echo "$(BLUE)フロントエンド依存関係をインストールしています...$(RESET)"
	@cd $(FRONTEND_DIR) && npm install

update-deps: ## 依存関係を更新
	@echo "$(BLUE)依存関係を更新しています...$(RESET)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && pip-compile requirements.in && pip-compile requirements-dev.in
	@cd $(FRONTEND_DIR) && npm update

# 本番用コマンド
build-prod: ## 本番用ビルドを実行
	@echo "$(BLUE)本番用ビルドを実行しています...$(RESET)"
	@docker-compose -f docker-compose.prod.yml build

deploy-prod: ## 本番環境にデプロイ
	@echo "$(BLUE)本番環境にデプロイしています...$(RESET)"
	@docker-compose -f docker-compose.prod.yml up -d

# セキュリティ
security-check: ## セキュリティチェックを実行
	@echo "$(BLUE)セキュリティチェックを実行しています...$(RESET)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && safety check
	@cd $(FRONTEND_DIR) && npm audit

# ドキュメント生成
docs: ## ドキュメントを生成
	@echo "$(BLUE)ドキュメントを生成しています...$(RESET)"
	@cd $(BACKEND_DIR) && source venv/bin/activate && sphinx-build -b html docs docs/_build

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
	@cd $(BACKEND_DIR) && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start-frontend: ## フロントエンドのみ起動
	@echo "$(BLUE)フロントエンドを起動しています...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run dev

# 便利なエイリアス
dev: start ## 開発環境を起動（startのエイリアス）
down: stop ## 開発環境を停止（stopのエイリアス）
reset: clean setup ## 環境をリセット
full-test: lint test ## 全品質チェックとテストを実行