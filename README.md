# Chat Service - コンテナベース開発環境

Slackライクなリアルタイムチャットサービス

## 🚀 プロジェクト概要

リアルタイムでのメッセージングとチームコラボレーションを支援するWebベースのチャットサービスです。
フロントエンドとバックエンドの両方がDockerコンテナで動作するよう設定されており、ローカル環境にNode.jsやPythonをインストールする必要はありません。

### 技術スタック
- **バックエンド**: Python 3.11+ / FastAPI / PostgreSQL
- **フロントエンド**: Next.js 14+ / TypeScript / Tailwind CSS
- **インフラ**: Docker / Docker Compose
- **データベース**: PostgreSQL 15 / Redis 7

## 📁 プロジェクト構成

```
chat_system/
├── backend/               # FastAPI アプリケーション
│   ├── Dockerfile        # バックエンド用マルチステージDockerfile
│   ├── requirements.txt  # Python依存関係
│   └── app/             # アプリケーションコード
├── frontend/             # Next.js アプリケーション
│   ├── Dockerfile       # フロントエンド用マルチステージDockerfile
│   ├── package.json     # Node.js依存関係
│   └── src/             # アプリケーションコード
├── doc/                  # ドキュメント
├── docker-compose.yml    # 開発環境用Docker設定
├── docker-compose.prod.yml # 本番環境用Docker設定
├── Makefile             # 開発用コマンド
└── README.md
```

## 🛠️ 開発環境セットアップ

### 前提条件

以下のツールがインストールされている必要があります：

- [Docker](https://docs.docker.com/get-docker/) (20.10.0 以上)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0.0 以上)

### クイックスタート

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd chat_system
   ```

2. **初期セットアップ（初回のみ）**
   ```bash
   make setup
   ```

3. **開発環境を起動**
   ```bash
   make start
   ```

4. **アプリケーションにアクセス**
   - **フロントエンド**: http://localhost:3000
   - **バックエンドAPI**: http://localhost:8000
   - **API ドキュメント**: http://localhost:8000/v1/docs
   - **pgAdmin** (オプション): http://localhost:5050

## 🐳 利用可能なコマンド

### 基本操作

```bash
make setup       # 初期セットアップ
make start       # 開発環境を起動
make stop        # 開発環境を停止
make restart     # 開発環境を再起動
make clean       # クリーンアップ（データ削除）
```

### 開発用コマンド

```bash
make logs           # 全サービスのログを表示
make logs-backend   # バックエンドのログのみ
make logs-frontend  # フロントエンドのログのみ

make test           # 全テストを実行
make test-backend   # バックエンドテストのみ
make test-frontend  # フロントエンドテストのみ

make lint           # 全コード品質チェック
make lint-backend   # バックエンドのリントのみ
make lint-frontend  # フロントエンドのリントのみ
```

### データベース操作

```bash
make migrate               # マイグレーション実行
make migrate-create        # 新しいマイグレーション作成
make migrate-downgrade     # マイグレーション1つ戻す
make migrate-history       # マイグレーション履歴表示
make seed                  # テストデータ投入

make backup                # データベースバックアップ
make restore FILE=backup.sql  # データベース復元

make db-connect            # PostgreSQLに接続
make redis-connect         # Redisに接続
```

### 個別サービス起動

```bash
make start-db        # データベースのみ起動
make start-backend   # バックエンドのみ起動
make start-frontend  # フロントエンドのみ起動
```

### 本番環境

```bash
# .env.prod.exampleを参考に.env.prodを作成してから：
make build-prod     # 本番用ビルド
make start-prod     # 本番環境起動
make stop-prod      # 本番環境停止
```

## 🔧 開発環境の構成

### サービス構成

- **postgres**: PostgreSQL 15 (ポート 5432)
- **redis**: Redis 7 (ポート 6379)
- **backend**: Python/FastAPI (ポート 8000)
- **frontend**: Next.js/TypeScript (ポート 3000)
- **pgadmin**: 管理ツール (ポート 5050, profiles: tools)

### 環境変数

環境変数は`docker-compose.yml`内に直接定義されています。開発環境用の設定が含まれており、本番環境では`docker-compose.prod.yml`と`.env.prod`ファイルを使用します。

主な環境変数：

#### バックエンド
- `DATABASE_URL`: データベース接続URL
- `REDIS_URL`: Redis接続URL
- `SECRET_KEY`: JWT署名用秘密鍵
- `CORS_ORIGINS`: CORS許可オリジン
- `DEBUG`: デバッグモード

#### フロントエンド
- `NEXT_PUBLIC_API_URL`: APIのベースURL
- `NEXT_PUBLIC_WS_URL`: WebSocket URL
- `NEXTAUTH_URL`: 認証のベースURL
- `NEXTAUTH_SECRET`: NextAuth.js用秘密鍵

## 🗃️ データベース操作

### マイグレーション

```bash
# マイグレーションファイルの生成
make migrate-create

# マイグレーションの実行
make migrate

# マイグレーションの履歴確認
make migrate-history

# 特定のリビジョンへのロールバック
make migrate-downgrade
```

### データベース接続

```bash
# PostgreSQL コンテナに接続
make db-connect

# Redis コンテナに接続
make redis-connect
```

## 🧪 開発用コマンド

### バックエンド

```bash
# テスト実行
make test-backend

# コードフォーマット・リント
make lint-backend

# ログ確認
make logs-backend
```

### フロントエンド

```bash
# テスト実行
make test-frontend

# リント・フォーマット
make lint-frontend

# ログ確認
make logs-frontend
```

## 🌐 開発のワークフロー

1. **初期セットアップ**
   ```bash
   make setup
   ```

2. **開発環境起動**
   ```bash
   make start
   ```

3. **コード変更**
   - バックエンド: `./backend/` 内のファイルを編集
   - フロントエンド: `./frontend/` 内のファイルを編集
   - 変更は自動でリロードされます

4. **テスト実行**
   ```bash
   make test
   ```

5. **コード品質チェック**
   ```bash
   make lint
   ```

6. **データベース変更**
   ```bash
   # モデル変更後
   make migrate-create
   make migrate
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

### 全テスト実行

```bash
# 全テスト実行
make test

# バックエンドテストのみ
make test-backend

# フロントエンドテストのみ
make test-frontend
```

### バックエンドテスト

```bash
# コンテナ内でテスト実行
make test-backend

# カバレッジ付きテスト
docker-compose run --rm backend pytest --cov=app --cov-report=html

# 特定のテストファイル実行
docker-compose run --rm backend pytest tests/test_auth.py
```

### フロントエンドテスト

```bash
# 単体テスト
make test-frontend

# E2Eテスト
docker-compose run --rm frontend npm run test:e2e

# ウォッチモードでテスト
docker-compose run --rm frontend npm test -- --watch
```

## 📚 ドキュメント

- [要件定義書](./doc/requirements.md)
- [データベース設計書](./doc/database_design.md)
- [API仕様書](./doc/api_specification.md)
- [バックエンド開発ガイド](./doc/backend_setup.md)
- [フロントエンド開発ガイド](./doc/frontend_setup.md)

## 🤝 貢献方法

1. ブランチを作成
2. 変更を実装
3. テストを実行: `make test`
4. リントを実行: `make lint`
5. プルリクエストを作成

## 🐛 トラブルシューティング

### よくある問題

**1. ポートが使用されている場合**
```bash
# 使用中のプロセスを確認
sudo lsof -i :3000
sudo lsof -i :8000

# 強制停止
make stop
```

**2. データベース接続エラー**
```bash
# データベースを再起動
make stop
make start-db
# 少し待ってから
make start
```

**3. コンテナの完全リセット**
```bash
make clean
make setup
```

**4. 依存関係エラー**
```bash
# イメージの再ビルド
docker-compose build --no-cache

# ボリュームのクリア
docker-compose down -v
make setup
```

### ログの確認

```bash
# 全サービスのログ
make logs

# 特定サービスのログ
make logs-backend
make logs-frontend

# エラー確認
make logs | grep -i error
```

### パフォーマンスの最適化

#### 開発時のボリュームマウント

- `node_modules`と`.next`はボリュームとしてマウントされ、ホストとコンテナ間での同期を高速化
- `venv`（Python仮想環境）もボリュームマウントで高速化

#### 本番時の最適化

- マルチステージビルドによる最小限のイメージサイズ
- 非rootユーザーでの実行
- ヘルスチェック機能

## 🚀 デプロイ

### 本番環境へのデプロイ

詳細は [デプロイガイド](./doc/deployment.md) を参照してください。

```bash
# .env.prod.exampleを参考に.env.prodを作成してから：

# 本番用ビルド
make build-prod

# 本番環境起動
make start-prod

# 本番環境停止
make stop-prod
```

### セキュリティ

- 開発環境では弱いシークレットキーを使用
- 本番環境では必ず`.env.prod`で強力な値を設定
- 非rootユーザーでのコンテナ実行
- 最小限の権限での実行

## 📞 サポート

質問や問題がある場合は、以下の方法でお問い合わせください：

- GitHub Issues: プロジェクトの Issue として報告
- 開発チーム: Slack #dev-chat-service チャンネル

## 📄 ライセンス

このプロジェクトは MIT License の下で公開されています。詳細は [LICENSE](./LICENSE) ファイルを参照してください。