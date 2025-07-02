#!/bin/bash

# =============================================================================
# Chat Service Development Scripts
# =============================================================================

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ヘルプ表示
show_help() {
    echo "Chat Service Development Scripts"
    echo ""
    echo "Usage: ./scripts/dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup         - 初期セットアップ"
    echo "  start         - 開発環境起動"
    echo "  stop          - 開発環境停止"
    echo "  restart       - 開発環境再起動"
    echo "  clean         - クリーンアップ"
    echo "  logs          - ログ表示"
    echo "  test          - テスト実行"
    echo "  lint          - コード品質チェック"
    echo "  migrate       - データベースマイグレーション"
    echo "  seed          - テストデータ投入"
    echo "  backup        - データベースバックアップ"
    echo "  restore       - データベースリストア"
    echo "  help          - ヘルプ表示"
    echo ""
}

# 前提条件チェック
check_prerequisites() {
    log_info "前提条件をチェックしています..."
    
    # Docker チェック
    if ! command -v docker &> /dev/null; then
        log_error "Docker がインストールされていません"
        exit 1
    fi
    
    # Docker Compose チェック
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose がインストールされていません"
        exit 1
    fi
    
    # Node.js チェック
    if ! command -v node &> /dev/null; then
        log_error "Node.js がインストールされていません"
        exit 1
    fi
    
    # Python チェック
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 がインストールされていません"
        exit 1
    fi
    
    log_success "前提条件チェック完了"
}

# 初期セットアップ
setup() {
    log_info "初期セットアップを開始します..."
    
    check_prerequisites
    
    # 環境変数ファイルのコピー
    if [ ! -f .env ]; then
        log_info "環境変数ファイルをコピーしています..."
        cp .env.example .env
        log_success "環境変数ファイルをコピーしました"
        log_warning "必要に応じて .env ファイルを編集してください"
    fi
    
    # フロントエンド環境変数ファイルのコピー
    if [ ! -f frontend/.env.local ]; then
        log_info "フロントエンド環境変数ファイルをコピーしています..."
        cp .env.example frontend/.env.local
        log_success "フロントエンド環境変数ファイルをコピーしました"
    fi
    
    # Dockerネットワーク作成
    log_info "Dockerネットワークを作成しています..."
    docker network create chat_network 2>/dev/null || log_warning "ネットワークは既に存在します"
    
    # データベース起動
    log_info "データベースを起動しています..."
    docker-compose up -d postgres redis
    
    # データベース起動待機
    log_info "データベースの起動を待機しています..."
    sleep 10
    
    # バックエンドセットアップ
    if [ -d "backend" ]; then
        log_info "バックエンドをセットアップしています..."
        cd backend
        
        # 仮想環境作成
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            log_success "Python仮想環境を作成しました"
        fi
        
        # 仮想環境有効化
        source venv/bin/activate
        
        # 依存関係インストール
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        log_success "Python依存関係をインストールしました"
        
        # マイグレーション実行
        alembic upgrade head
        log_success "データベースマイグレーションを実行しました"
        
        cd ..
    fi
    
    # フロントエンドセットアップ
    if [ -d "frontend" ]; then
        log_info "フロントエンドをセットアップしています..."
        cd frontend
        
        # 依存関係インストール
        npm install
        log_success "Node.js依存関係をインストールしました"
        
        cd ..
    fi
    
    log_success "初期セットアップが完了しました"
    log_info "開発を開始するには: ./scripts/dev.sh start"
}

# 開発環境起動
start() {
    log_info "開発環境を起動しています..."
    
    # ポート3000が使用されているかチェック
    if ss -tulpn | grep ":3000.*LISTEN" >/dev/null 2>&1; then
        log_warning "ポート3000は既に使用されています。既存のプロセスを停止します..."
        pkill -f "next dev" || true
        pkill -f "next-server" || true
        sleep 2
    fi
    
    # データベース起動
    docker-compose up -d postgres redis
    
    # バックエンド起動（バックグラウンド）
    if [ -d "backend" ]; then
        log_info "バックエンドを起動しています..."
        cd backend
        source venv/bin/activate
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
        echo $! > ../logs/backend.pid
        cd ..
        log_success "バックエンドを起動しました (PID: $(cat logs/backend.pid))"
    fi
    
    # フロントエンド起動（バックグラウンド）
    if [ -d "frontend" ]; then
        log_info "フロントエンドを起動しています..."
        cd frontend
        # ポート3000を明示的に指定
        nohup npx next dev -p 3000 > ../logs/frontend.log 2>&1 &
        echo $! > ../logs/frontend.pid
        cd ..
        log_success "フロントエンドを起動しました (PID: $(cat logs/frontend.pid))"
    fi
    
    log_success "開発環境の起動が完了しました"
    log_info "フロントエンド: http://localhost:3000"
    log_info "バックエンドAPI: http://localhost:8000"
    log_info "API ドキュメント: http://localhost:8000/v1/docs"
}

# 開発環境停止
stop() {
    log_info "開発環境を停止しています..."
    
    # プロセス停止
    if [ -f "logs/backend.pid" ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm -f logs/backend.pid
        log_success "バックエンドを停止しました"
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm -f logs/frontend.pid
        log_success "フロントエンドを停止しました"
    fi
    
    # 残っているNext.jsプロセスを強制終了
    log_info "残存するNext.jsプロセスをチェックしています..."
    if pgrep -f "next dev" > /dev/null 2>&1; then
        pkill -f "next dev" || true
        log_success "Next.js開発サーバーを停止しました"
    fi
    
    if pgrep -f "next-server" > /dev/null 2>&1; then
        pkill -f "next-server" || true
        log_success "Next.jsサーバープロセスを停止しました"
    fi
    
    # Node.jsプロセスもチェック（frontend ディレクトリから起動されたもの）
    if pgrep -f "node.*frontend.*next" > /dev/null 2>&1; then
        pkill -f "node.*frontend.*next" || true
        log_success "フロントエンドNode.jsプロセスを停止しました"
    fi
    
    # Docker サービス停止
    docker-compose down
    log_success "Dockerサービスを停止しました"
}

# 開発環境再起動
restart() {
    log_info "開発環境を再起動しています..."
    stop
    sleep 3
    start
}

# クリーンアップ
clean() {
    log_warning "クリーンアップを実行します（データが削除される可能性があります）"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "クリーンアップを開始します..."
        
        stop
        
        # Docker リソース削除
        docker-compose down -v --remove-orphans
        docker system prune -f
        
        # ログファイル削除
        rm -rf logs/*
        
        # キャッシュ削除
        if [ -d "backend/__pycache__" ]; then
            find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        fi
        
        if [ -d "frontend/.next" ]; then
            rm -rf frontend/.next
        fi
        
        if [ -d "frontend/node_modules/.cache" ]; then
            rm -rf frontend/node_modules/.cache
        fi
        
        log_success "クリーンアップが完了しました"
    else
        log_info "クリーンアップをキャンセルしました"
    fi
}

# ログ表示
logs() {
    log_info "ログを表示します..."
    
    case "${2:-all}" in
        backend)
            tail -f logs/backend.log
            ;;
        frontend)
            tail -f logs/frontend.log
            ;;
        docker)
            docker-compose logs -f
            ;;
        all|*)
            log_info "全てのログを表示します (Ctrl+C で終了)"
            (trap 'kill 0' SIGINT; 
             tail -f logs/backend.log 2>/dev/null & 
             tail -f logs/frontend.log 2>/dev/null & 
             docker-compose logs -f & 
             wait)
            ;;
    esac
}

# テスト実行
test() {
    log_info "テストを実行しています..."
    
    # バックエンドテスト
    if [ -d "backend" ]; then
        log_info "バックエンドテストを実行しています..."
        cd backend
        source venv/bin/activate
        pytest --cov=app --cov-report=html
        cd ..
        log_success "バックエンドテストが完了しました"
    fi
    
    # フロントエンドテスト
    if [ -d "frontend" ]; then
        log_info "フロントエンドテストを実行しています..."
        cd frontend
        npm test -- --coverage --watchAll=false
        cd ..
        log_success "フロントエンドテストが完了しました"
    fi
}

# コード品質チェック
lint() {
    log_info "コード品質チェックを実行しています..."
    
    # バックエンド
    if [ -d "backend" ]; then
        log_info "バックエンドのリントを実行しています..."
        cd backend
        source venv/bin/activate
        black app/
        isort app/
        flake8 app/
        mypy app/
        cd ..
        log_success "バックエンドのリントが完了しました"
    fi
    
    # フロントエンド
    if [ -d "frontend" ]; then
        log_info "フロントエンドのリントを実行しています..."
        cd frontend
        npm run lint:fix
        npm run format
        npm run type-check
        cd ..
        log_success "フロントエンドのリントが完了しました"
    fi
}

# データベースマイグレーション
migrate() {
    log_info "データベースマイグレーションを実行しています..."
    
    if [ -d "backend" ]; then
        cd backend
        source venv/bin/activate
        
        case "${2:-upgrade}" in
            create)
                read -p "マイグレーション名を入力してください: " migration_name
                alembic revision --autogenerate -m "$migration_name"
                ;;
            upgrade)
                alembic upgrade head
                ;;
            downgrade)
                alembic downgrade -1
                ;;
            history)
                alembic history
                ;;
            *)
                log_error "無効なマイグレーションコマンドです"
                echo "使用可能: create, upgrade, downgrade, history"
                ;;
        esac
        
        cd ..
        log_success "マイグレーションが完了しました"
    fi
}

# テストデータ投入
seed() {
    log_info "テストデータを投入しています..."
    
    if [ -d "backend" ]; then
        cd backend
        source venv/bin/activate
        python scripts/seed_data.py
        cd ..
        log_success "テストデータの投入が完了しました"
    fi
}

# データベースバックアップ
backup() {
    log_info "データベースバックアップを作成しています..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backups/chat_db_backup_$timestamp.sql"
    
    mkdir -p backups
    
    docker-compose exec postgres pg_dump -U chat_user chat_db > $backup_file
    
    log_success "バックアップを作成しました: $backup_file"
}

# データベースリストア
restore() {
    if [ -z "$2" ]; then
        log_error "バックアップファイルを指定してください"
        echo "使用例: ./scripts/dev.sh restore backups/chat_db_backup_20240101_120000.sql"
        exit 1
    fi
    
    backup_file="$2"
    
    if [ ! -f "$backup_file" ]; then
        log_error "バックアップファイルが見つかりません: $backup_file"
        exit 1
    fi
    
    log_warning "データベースを復元します（既存のデータは削除されます）"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "データベースを復元しています..."
        
        # データベース再作成
        docker-compose exec postgres dropdb -U chat_user chat_db
        docker-compose exec postgres createdb -U chat_user chat_db
        
        # バックアップ復元
        docker-compose exec -T postgres psql -U chat_user chat_db < $backup_file
        
        log_success "データベースの復元が完了しました"
    else
        log_info "復元をキャンセルしました"
    fi
}

# ログディレクトリ作成
mkdir -p logs

# メイン処理
case "${1:-help}" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    clean)
        clean
        ;;
    logs)
        logs "$@"
        ;;
    test)
        test
        ;;
    lint)
        lint
        ;;
    migrate)
        migrate "$@"
        ;;
    seed)
        seed
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$@"
        ;;
    help|*)
        show_help
        ;;
esac