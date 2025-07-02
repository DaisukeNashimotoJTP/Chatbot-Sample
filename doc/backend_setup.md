# バックエンド開発環境セットアップガイド

## 1. 概要

FastAPI を使用したバックエンド API の開発環境セットアップ手順を説明します。

## 2. 前提条件

- Python 3.11+ がインストールされていること
- Docker & Docker Compose がインストールされていること
- Git がインストールされていること

## 3. 初期セットアップ

### 3.1 プロジェクトクローン

```bash
git clone <repository-url>
cd chat_system
```

### 3.2 環境変数設定

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# 必要に応じて .env ファイルを編集
vim .env
```

### 3.3 データベース起動

```bash
# PostgreSQL と Redis をDockerで起動
docker-compose up -d postgres redis

# データベース接続確認
docker-compose exec postgres psql -U chat_user -d chat_db -c "SELECT version();"
```

## 4. バックエンド環境構築

### 4.1 仮想環境作成

```bash
cd backend

# 仮想環境作成
python -m venv venv

# 仮想環境有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
```

### 4.2 依存関係インストール

```bash
# 依存関係インストール
pip install -r requirements.txt

# 開発用依存関係インストール
pip install -r requirements-dev.txt
```

### 4.3 データベースマイグレーション

```bash
# マイグレーション実行
alembic upgrade head

# 初期データ投入（オプション）
python scripts/seed_data.py
```

### 4.4 アプリケーション起動

```bash
# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動したら以下のURLでアクセス可能：
- API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 5. 開発用コマンド

### 5.1 コード品質チェック

```bash
# コードフォーマット
black app/
isort app/

# リント
flake8 app/
pylint app/

# 型チェック
mypy app/
```

### 5.2 テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app --cov-report=html

# 特定のテストファイル実行
pytest tests/test_auth.py

# テストデータベース使用
pytest --create-db
```

### 5.3 データベース操作

```bash
# 新しいマイグレーションファイル作成
alembic revision --autogenerate -m "Add new table"

# マイグレーション実行
alembic upgrade head

# マイグレーション履歴確認
alembic history

# 1つ前のマイグレーションにロールバック
alembic downgrade -1

# 特定のリビジョンまでロールバック
alembic downgrade <revision_id>
```

## 6. プロジェクト構造

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
```

### 10.2 デバッガー使用
```python
import pdb

def some_function():
    pdb.set_trace()  # ブレークポイント
    # デバッグしたいコード
```

### 10.3 API テスト
```bash
# cURL を使用したテスト
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# HTTPie を使用したテスト（推奨）
http POST localhost:8000/v1/auth/login email=test@example.com password=password
```

## 11. 本番環境への準備

### 11.1 環境変数の設定
本番環境用の環境変数を適切に設定

### 11.2 セキュリティ設定
- SECRET_KEY を安全な値に変更
- CORS_ORIGINS を適切に設定
- HTTPS の使用

### 11.3 パフォーマンス最適化
- データベース接続プールの設定
- キャッシュの活用
- 適切なインデックスの設定