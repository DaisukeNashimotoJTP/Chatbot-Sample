# Chat Service - コンテナベース開発環境

本プロジェクトは、フロントエンドとバックエンドの両方がDocker コンテナで動作するよう設定されています。ローカル環境にNode.jsやPythonをインストールする必要はありません。

## 前提条件

以下のツールがインストールされている必要があります：

- Docker (20.10.0 以上)
- Docker Compose (2.0.0 以上)

## クイックスタート

```bash
# リポジトリをクローン
git clone <repository-url>
cd chat_system

# 初期セットアップ（初回のみ）
make setup

# 開発環境を起動
make start
```

環境が起動したら、以下のURLでアクセスできます：

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/v1/docs
- **pgAdmin** (オプション): http://localhost:5050

## 利用可能なコマンド

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

## 開発環境の構成

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

## ファイル構造

```
├── docker-compose.yml          # 開発環境用Docker設定
├── docker-compose.prod.yml     # 本番環境用Docker設定
├── .env.prod.example          # 本番環境用環境変数テンプレート
├── Makefile                   # 開発用コマンド
├── backend/
│   ├── Dockerfile            # バックエンド用マルチステージDockerfile
│   ├── requirements.txt      # Python依存関係
│   └── app/                  # アプリケーションコード
├── frontend/
│   ├── Dockerfile           # フロントエンド用マルチステージDockerfile
│   ├── package.json         # Node.js依存関係
│   └── src/                 # アプリケーションコード
└── scripts/
    └── (削除済み)           # 完全コンテナ化により開発スクリプトは不要
```

## 開発のワークフロー

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

## トラブルシューティング

### ポートが使用されている場合

```bash
# 使用中のプロセスを確認
sudo lsof -i :3000
sudo lsof -i :8000

# 強制停止
make stop
```

### データベース接続エラー

```bash
# データベースを再起動
make stop
make start-db
# 少し待ってから
make start
```

### コンテナの完全リセット

```bash
make clean
make setup
```

### ログの確認

```bash
# エラー確認
make logs

# 特定のサービスのログ
make logs-backend
make logs-frontend
```

## パフォーマンスの最適化

### 開発時のボリュームマウント

- `node_modules`と`.next`はボリュームとしてマウントされ、ホストとコンテナ間での同期を高速化
- `venv`（Python仮想環境）もボリュームマウントで高速化

### 本番時の最適化

- マルチステージビルドによる最小限のイメージサイズ
- 非rootユーザーでの実行
- ヘルスチェック機能

## セキュリティ

- 開発環境では弱いシークレットキーを使用
- 本番環境では必ず`.env.prod`で強力な値を設定
- 非rootユーザーでのコンテナ実行
- 最小限の権限での実行

## 貢献方法

1. ブランチを作成
2. 変更を実装
3. テストを実行: `make test`
4. リントを実行: `make lint`
5. プルリクエストを作成
