# バックエンド開発環境セットアップガイド - コンテナベース

## 1. 概要

FastAPI を使用したバックエンド API のコンテナベース開発環境セットアップ手順を説明します。
ローカル環境にPythonをインストールする必要はありません。

## 2. 前提条件

- Docker (20.10.0 以上) がインストールされていること
- Docker Compose (2.0.0 以上) がインストールされていること
- Git がインストールされていること

## 3. 初期セットアップ

### 3.1 プロジェクトクローン

```bash
git clone <repository-url>
cd chat_system
```

### 3.2 初期セットアップ実行

```bash
# 初期セットアップ（データベース、マイグレーション、シードデータを含む）
make setup
```

このコマンドで以下が自動実行されます：
- Dockerイメージのビルド
- データベース（PostgreSQL、Redis）の起動
- データベースマイグレーション
- テストデータの投入

### 3.3 開発環境起動

```bash
# 開発環境を起動
make start
```

## 4. バックエンド開発

```bash
# 仮想環境有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
```

### 4.1 コード編集

バックエンドのコードは `./backend/` ディレクトリ内で編集します。
変更は自動でコンテナに反映され、開発サーバーが自動リロードされます。

```bash
# ログの確認
make logs-backend

# バックエンドコンテナ内でコマンド実行
docker-compose exec backend bash
```

### 4.2 データベースマイグレーション

```bash
# 新しいマイグレーションファイルを作成
make migrate-create

# マイグレーション実行
make migrate

# マイグレーション履歴確認
make migrate-history

# 1つ前のマイグレーションに戻す
make migrate-downgrade
```

### 4.3 テストデータ管理

```bash
# テストデータの投入
make seed

# データベースバックアップ
make backup

# データベース復元
make restore FILE=backup.sql
```

## 5. 開発用コマンド

### 5.1 コード品質チェック

```bash
# バックエンドのリント・フォーマット実行
make lint-backend

```bash
# バックエンドテスト実行
make test-backend

# 個別実行の場合：
docker-compose run --rm backend pytest

# カバレッジ付きテスト
docker-compose run --rm backend pytest --cov=app --cov-report=html

# 特定のテストファイル実行
docker-compose run --rm backend pytest tests/test_auth.py
```

### 5.3 データベース操作

```bash
# データベースに接続
make db-connect

# Redisに接続
make redis-connect

# データベースバックアップ
make backup

# データベース復元
make restore FILE=path/to/backup.sql
```

### 5.4 依存関係管理

```bash
# 新しいパッケージを追加
# 1. requirements.txt または requirements-dev.txt を編集
# 2. イメージを再ビルド
docker-compose build backend

# または個別にインストール
docker-compose run --rm backend pip install <package-name>
```

## 6. デバッグとログ

### 6.1 ログ確認

```bash
# バックエンドログの確認
make logs-backend

# リアルタイムログ監視
docker-compose logs -f backend

# エラーログのみ表示
make logs-backend | grep -i error
```

### 6.2 デバッグ

```bash
# バックエンドコンテナ内でシェル実行
docker-compose exec backend bash

# Python インタープリター起動
docker-compose exec backend python

# 依存関係の確認
docker-compose exec backend pip list
```

## 7. プロジェクト構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリケーション
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # 設定
│   │   ├── database.py      # データベース接続
│   │   ├── security.py      # 認証・認可
│   │   └── exceptions.py    # 例外処理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # ユーザーモデル
│   │   ├── workspace.py     # ワークスペースモデル
│   │   ├── channel.py       # チャンネルモデル
│   │   └── message.py       # メッセージモデル
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # ユーザースキーマ
│   │   ├── workspace.py     # ワークスペーススキーマ
│   │   ├── channel.py       # チャンネルスキーマ
│   │   └── message.py       # メッセージスキーマ
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # 依存関係
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py      # 認証API
│   │       ├── users.py     # ユーザーAPI
│   │       ├── workspaces.py # ワークスペースAPI
│   │       ├── channels.py  # チャンネルAPI
│   │       └── messages.py  # メッセージAPI
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py          # 認証サービス
│   │   ├── user.py          # ユーザーサービス
│   │   ├── workspace.py     # ワークスペースサービス
│   │   ├── channel.py       # チャンネルサービス
│   │   └── message.py       # メッセージサービス
│   └── utils/
│       ├── __init__.py
│       ├── email.py         # メール送信
│       ├── file.py          # ファイル操作
│       └── websocket.py     # WebSocket処理
├── alembic/
│   ├── versions/            # マイグレーションファイル
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # テスト設定
│   ├── test_auth.py         # 認証テスト
│   ├── test_users.py        # ユーザーテスト
│   └── test_messages.py     # メッセージテスト
├── scripts/
│   ├── seed_data.py         # 初期データ投入
│   └── init_db.sql          # DB初期化SQL
├── requirements.txt         # 本番依存関係
├── requirements-dev.txt     # 開発依存関係
├── alembic.ini             # Alembic設定
├── pytest.ini             # pytest設定
├── pyproject.toml          # プロジェクト設定
└── Dockerfile              # Docker設定
```

## 7. 重要なファイル

### 7.1 app/main.py
FastAPI アプリケーションのエントリーポイント

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, workspaces, channels, messages

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
# 他のルーターも同様に登録
```

### 7.2 app/core/config.py
アプリケーション設定

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Chat Service"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/v1"
    
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    CORS_ORIGINS: List[str] = []
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 7.3 app/core/database.py
データベース接続設定

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 8. 開発時の注意点

### 8.1 コーディング規約
- PEP 8 に従う
- 型ヒントを使用する
- docstring を記述する
- 適切な例外処理を行う

### 8.2 Git コミット規約
```bash
# 機能追加
git commit -m "feat: add user authentication"

# バグ修正
git commit -m "fix: resolve database connection issue"

# ドキュメント更新
git commit -m "docs: update API documentation"
```

### 8.3 テスト記述
- 各 API エンドポイントに対してテストを作成
- エッジケースもテストする
- モックを適切に使用する

## 9. よくある問題と解決方法

### 9.1 データベース接続エラー
```bash
# PostgreSQL コンテナの状態確認
docker-compose ps postgres

# ログ確認
docker-compose logs postgres

# 再起動
docker-compose restart postgres
```

### 9.2 マイグレーションエラー
```bash
# マイグレーション履歴確認
alembic history

# 問題のあるマイグレーションを削除して再作成
alembic downgrade -1
rm alembic/versions/<problem_revision>.py
alembic revision --autogenerate -m "Fixed migration"
```

### 9.3 依存関係エラー
```bash
# 仮想環境を削除して再作成
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 10. デバッグ方法

### 10.1 ログ出力
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("Function called")
    logger.debug("Debug information")
    logger.error("Error occurred")
## 8. 環境変数

環境変数は`docker-compose.yml`内に直接定義されており、開発時に設定ファイルを編集する必要はありません。

主な環境変数：

```yaml
# データベース設定
DATABASE_URL: postgresql+asyncpg://chat_user:chat_password@postgres:5432/chat_db
TEST_DATABASE_URL: postgresql+asyncpg://chat_user:chat_password@postgres_test:5432/chat_test_db

# Redis設定
REDIS_URL: redis://redis:6379

# JWT設定
SECRET_KEY: dev-secret-key-change-in-production-123456789
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 1440

# CORS設定
CORS_ORIGINS: '["http://localhost:3000", "http://frontend:3000"]'

# アプリケーション設定
DEBUG: "true"
```

本番環境では`.env.prod`ファイルで適切な値を設定します。

## 9. トラブルシューティング

### 9.1 よくある問題

**バックエンドコンテナが起動しない**
```bash
# ログを確認
make logs-backend

# イメージを再ビルド
docker-compose build backend

# コンテナを再作成
docker-compose up -d --force-recreate backend
```

**データベース接続エラー**
```bash
# データベースの状態確認
docker-compose ps postgres

# データベースを再起動
docker-compose restart postgres

# データベース接続確認
make db-connect
```

**依存関係のエラー**
```bash
# コンテナ内で依存関係確認
docker-compose exec backend pip list

# requirements.txtが更新された場合
docker-compose build --no-cache backend
```

### 9.2 デバッグ

**コンテナ内でデバッグ**
```bash
# バックエンドコンテナにアクセス
docker-compose exec backend bash

# Python REPLでテスト
docker-compose exec backend python
>>> from app.main import app
>>> print(app.routes)
```

**APIテスト**
```bash
# ヘルスチェック
curl http://localhost:8000/v1/health

# API ドキュメントにアクセス
# http://localhost:8000/v1/docs
```

## 10. 本番環境への準備

### 10.1 本番用ビルド
```bash
# 本番用イメージビルド
make build-prod

# 本番環境起動
make start-prod
```

### 10.2 セキュリティ設定
本番環境では以下を必ず変更：
- `.env.prod`でSECRET_KEYを安全な値に設定
- CORS_ORIGINSを本番ドメインに限定
- DEBUGをfalseに設定

### 10.3 パフォーマンス最適化
- データベース接続プールの設定
- Redis キャッシュの活用
- 適切なインデックスの設定
- ログレベルの調整