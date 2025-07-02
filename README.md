# Chat Service

Slackライクなリアルタイムチャットサービス

## 🚀 プロジェクト概要

リアルタイムでのメッセージングとチームコラボレーションを支援するWebベースのチャットサービスです。

### 技術スタック
- **バックエンド**: Python 3.11+ / FastAPI / PostgreSQL
- **フロントエンド**: Next.js 14+ / TypeScript / Tailwind CSS
- **インフラ**: Docker / AWS

## 📁 プロジェクト構成

```
chat_system/
├── backend/          # FastAPI アプリケーション
├── frontend/         # Next.js アプリケーション
├── doc/              # ドキュメント
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🛠️ 開発環境セットアップ

### 前提条件

以下のソフトウェアがインストールされている必要があります：

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- [Node.js](https://nodejs.org/) (18.0+)
- [Python](https://www.python.org/) (3.11+)
- [Git](https://git-scm.com/)

### クイックスタート

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd chat_system
   ```

2. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .env ファイルを編集して必要な値を設定
   ```

3. **データベースの起動（Docker）**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **バックエンドのセットアップ**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **フロントエンドのセットアップ**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **アプリケーションにアクセス**
   - フロントエンド: http://localhost:3000
   - バックエンドAPI: http://localhost:8000
   - API ドキュメント: http://localhost:8000/docs

## 🐳 Docker を使用した開発

### 全サービスの起動

```bash
# 全サービスを起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# サービスの停止
docker-compose down
```

### 個別サービスの操作

```bash
# データベースのみ起動
docker-compose up -d postgres redis

# バックエンドのみ起動
docker-compose up -d backend

# フロントエンドのみ起動
docker-compose up -d frontend
```

## 🗃️ データベース操作

### マイグレーション

```bash
# マイグレーションファイルの生成
cd backend
alembic revision --autogenerate -m "Add new table"

# マイグレーションの実行
alembic upgrade head

# マイグレーションの履歴確認
alembic history

# 特定のリビジョンへのロールバック
alembic downgrade -1
```

### データベース接続

```bash
# PostgreSQL コンテナに接続
docker-compose exec postgres psql -U chat_user -d chat_db

# Redis コンテナに接続
docker-compose exec redis redis-cli
```

## 🔧 開発用コマンド

### バックエンド

```bash
cd backend

# 開発サーバー起動
uvicorn app.main:app --reload

# テスト実行
pytest

# コードフォーマット
black app/
isort app/

# 型チェック
mypy app/

# リント
flake8 app/

# 依存関係の更新
pip-compile requirements.in
```

### フロントエンド

```bash
cd frontend

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# テスト実行
npm test

# E2Eテスト
npm run test:e2e

# 型チェック
npm run type-check

# リント
npm run lint

# フォーマット
npm run format
```

## 🌐 環境変数

### バックエンド (.env)

```bash
# データベース設定
DATABASE_URL=postgresql://chat_user:chat_password@localhost:5432/chat_db
TEST_DATABASE_URL=postgresql://chat_user:chat_password@localhost:5432/chat_test_db

# Redis設定
REDIS_URL=redis://localhost:6379

# JWT設定
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AWS設定（本番環境）
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-northeast-1
S3_BUCKET_NAME=your-bucket-name

# アプリケーション設定
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

### フロントエンド (.env.local)

```bash
# API設定
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/v1/ws

# 認証設定
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# その他設定
NEXT_PUBLIC_APP_ENV=development
```

## 🧪 テスト

### バックエンドテスト

```bash
cd backend

# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app

# 特定のテストファイル実行
pytest tests/test_auth.py

# テストデータベースのリセット
pytest --create-db
```

### フロントエンドテスト

```bash
cd frontend

# 単体テスト
npm test

# ウォッチモード
npm test -- --watch

# E2Eテスト
npm run test:e2e

# ビジュアル回帰テスト
npm run test:visual
```

## 📚 ドキュメント

- [要件定義書](./doc/requirements.md)
- [データベース設計書](./doc/database_design.md)
- [API仕様書](./doc/api_specification.md)
- [バックエンド開発ガイド](./doc/backend_setup.md)
- [フロントエンド開発ガイド](./doc/frontend_setup.md)

## 🤝 開発フロー

1. **ブランチ作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **開発・テスト**
   - 機能実装
   - テスト作成・実行
   - コードレビュー

3. **プルリクエスト**
   - PR作成
   - レビュー対応
   - マージ

## 🐛 トラブルシューティング

### よくある問題

**1. PostgreSQL接続エラー**
```bash
# コンテナの状態確認
docker-compose ps

# ログ確認
docker-compose logs postgres

# コンテナの再起動
docker-compose restart postgres
```

**2. ポート競合エラー**
```bash
# 使用中のポート確認
lsof -i :8000
lsof -i :3000

# プロセス終了
kill -9 <PID>
```

**3. 依存関係エラー**
```bash
# Python仮想環境の再作成
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.jsモジュールの再インストール
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f postgres
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🚀 デプロイ

### 本番環境への デプロイ

詳細は [デプロイガイド](./doc/deployment.md) を参照してください。

```bash
# 本番用ビルド
docker-compose -f docker-compose.prod.yml build

# 本番環境起動
docker-compose -f docker-compose.prod.yml up -d
```

## 📞 サポート

質問や問題がある場合は、以下の方法でお問い合わせください：

- GitHub Issues: プロジェクトの Issue として報告
- 開発チーム: Slack #dev-chat-service チャンネル

## 📄 ライセンス

このプロジェクトは MIT License の下で公開されています。詳細は [LICENSE](./LICENSE) ファイルを参照してください。