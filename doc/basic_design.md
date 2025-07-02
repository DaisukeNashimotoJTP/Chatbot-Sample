# 基本設計書

## 1. 概要

### 1.1 目的
本書は、Slackライクなチャットサービスの基本設計について記載する。システム全体のアーキテクチャ、主要コンポーネントの設計、および技術的な実装方針を定義する。

### 1.2 対象読者
- 開発チーム
- プロジェクトマネージャー
- システムアーキテクト
- インフラ担当者

### 1.3 関連ドキュメント
- [要件定義書](./requirements.md)
- [データベース設計書](./database_design.md)
- [API仕様書](./api_specification.md)
- [詳細設計書](./detailed_design.md)

## 2. システム全体アーキテクチャ

### 2.1 アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Web Browser (Next.js SPA)  │  Mobile App (Future)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (ALB)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                       │
├─────────────────────────────────────────────────────────────┤
│           FastAPI Application Server (ECS)                 │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   REST API      │  │      WebSocket Handler         │   │
│  │   Endpoints     │  │   (Real-time Communication)    │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Auth Service │ │ User Service │ │ Workspace Service    │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │Channel Service│ │Message Service│ │ File Service        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Access Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ ┌──────────────┐  │
│  │   PostgreSQL    │  │      Redis      │ │     S3       │  │
│  │   (RDS)         │  │    (Cache)      │ │ (File Store) │  │
│  └─────────────────┘  └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 アーキテクチャパターン
- **分層アーキテクチャ**: プレゼンテーション層、ビジネスロジック層、データアクセス層の3層構造
- **クリーンアーキテクチャ**: 依存関係の方向を制御し、ビジネスロジックを外部フレームワークから独立
- **マイクロサービス指向**: 将来的な拡張を考慮した疎結合な設計

### 2.3 技術スタック詳細

#### フロントエンド
- **フレームワーク**: Next.js 14 (App Router)
- **言語**: TypeScript
- **状態管理**: Zustand + React Query
- **スタイリング**: Tailwind CSS + shadcn/ui
- **リアルタイム通信**: WebSocket (native) + Socket.io-client

#### バックエンド
- **フレームワーク**: FastAPI
- **言語**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 + Alembic
- **認証**: JWT (PyJWT)
- **バリデーション**: Pydantic v2
- **非同期処理**: asyncio + asyncpg

#### インフラストラクチャ
- **コンテナ**: Docker + ECS
- **データベース**: PostgreSQL (RDS Multi-AZ)
- **キャッシュ**: Redis (ElastiCache)
- **ファイルストレージ**: S3
- **ロードバランサー**: Application Load Balancer
- **監視**: CloudWatch + X-Ray

## 3. コンポーネント設計

### 3.1 フロントエンドコンポーネント構成

```
frontend/
├── app/                     # Next.js App Router
│   ├── (auth)/             # 認証関連ページ
│   ├── workspace/          # ワークスペース関連ページ
│   └── api/                # API Routes
├── components/
│   ├── ui/                 # 基本UIコンポーネント
│   ├── layout/             # レイアウトコンポーネント
│   ├── features/           # 機能別コンポーネント
│   │   ├── auth/
│   │   ├── workspace/
│   │   ├── channel/
│   │   └── message/
│   └── providers/          # Context Providers
├── hooks/                  # カスタムフック
├── lib/                    # ユーティリティ・設定
├── store/                  # 状態管理
└── types/                  # 型定義
```

### 3.2 バックエンドコンポーネント構成

```
backend/
├── app/
│   ├── main.py             # FastAPI アプリケーション
│   ├── core/               # コア機能
│   │   ├── config.py       # 設定管理
│   │   ├── database.py     # DB接続
│   │   ├── security.py     # 認証・認可
│   │   └── exceptions.py   # 例外処理
│   ├── models/             # SQLAlchemy モデル
│   ├── schemas/            # Pydantic スキーマ
│   ├── api/                # API エンドポイント
│   │   └── v1/
│   ├── services/           # ビジネスロジック
│   ├── repositories/       # データアクセス層
│   └── utils/              # ユーティリティ
├── tests/                  # テストコード
└── alembic/                # マイグレーション
```

## 4. データフロー設計

### 4.1 リクエスト処理フロー

```
User Action → Frontend → API Gateway → Business Logic → Repository → Database
     ↑                                                                    ↓
Response ← Frontend ← JSON Response ← Service Layer ← Data Access ← Query Result
```

### 4.2 リアルタイム通信フロー

```
User A sends message
        ↓
Frontend (WebSocket) → FastAPI WebSocket Handler
        ↓
Message Service → Repository → Database
        ↓
WebSocket Broadcast → Connected Clients
        ↓
User B receives message
```

### 4.3 認証フロー

```
1. User Login Request → Auth Service
2. Validate Credentials → User Repository
3. Generate JWT Token ← Auth Service
4. Store Token → Frontend (localStorage)
5. API Request with Token → Protected Endpoint
6. Validate Token → JWT Middleware
7. Extract User Info → Request Context
```

## 5. セキュリティ設計

### 5.1 認証・認可

#### JWT認証フロー
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend   │    │   Database   │
└──────┬───────┘    └──────┬──────┘    └──────┬───────┘
       │                   │                  │
       │ 1. Login Request  │                  │
       ├──────────────────→│                  │
       │                   │ 2. Validate User│
       │                   ├─────────────────→│
       │                   │ 3. User Data     │
       │                   │←─────────────────┤
       │ 4. JWT Token      │                  │
       │←──────────────────┤                  │
       │                   │                  │
       │ 5. API Request    │                  │
       │   (with Token)    │                  │
       ├──────────────────→│                  │
       │                   │ 6. Validate Token│
       │                   │                  │
       │ 7. Response       │                  │
       │←──────────────────┤                  │
```

#### 権限管理
- **Role-Based Access Control (RBAC)**
- **ワークスペースレベル**: Owner, Admin, Member, Guest
- **チャンネルレベル**: Admin, Member
- **リソースレベル**: Read, Write, Delete

### 5.2 データ保護

#### 暗号化
- **通信暗号化**: TLS 1.3
- **パスワード**: bcrypt (cost=12)
- **データベース**: RDS暗号化
- **ファイル**: S3サーバーサイド暗号化

#### 入力検証
- **Pydantic**: スキーマベースバリデーション
- **SQLインジェクション**: SQLAlchemy ORM使用
- **XSS**: CSP (Content Security Policy)
- **CSRF**: SameSite Cookie + Token

## 6. パフォーマンス設計

### 6.1 キャッシュ戦略

#### Redis キャッシュ階層
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │      Redis      │    │   PostgreSQL    │
│      Cache      │    │      Cache      │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Check App Cache    │                       │
         ├──────────────────────→│                       │
         │ 2. Check Redis        │                       │
         │   (if miss)           ├──────────────────────→│
         │                       │ 3. Query Database     │
         │                       │   (if miss)           │
         │                       │←──────────────────────┤
         │←──────────────────────┤ 4. Cache Result       │
         │ 5. Return Data        │                       │
```

#### キャッシュ対象
- **ユーザーセッション**: 30分TTL
- **ワークスペース情報**: 1時間TTL
- **チャンネル一覧**: 10分TTL
- **よく使用されるメッセージ**: 5分TTL

### 6.2 データベース最適化

#### インデックス戦略
- **複合インデックス**: 検索頻度の高いカラム組み合わせ
- **部分インデックス**: 条件付きインデックス
- **GIN インデックス**: 全文検索用

#### クエリ最適化
- **N+1問題**: SQLAlchemy Eager Loading
- **バッチ処理**: 一括操作の活用
- **ページネーション**: カーソルベース + オフセットベース

### 6.3 スケーラビリティ設計

#### 水平スケーリング
- **アプリケーションサーバー**: ECS Auto Scaling
- **データベース**: Read Replica
- **ファイルストレージ**: S3 (無制限)

#### 負荷分散
- **ロードバランサー**: ALB (Layer 7)
- **WebSocket**: Sticky Sessions
- **Database**: Read/Write 分離

## 7. エラーハンドリング設計

### 7.1 エラー分類

#### システムエラー
- **50x系**: サーバー内部エラー
- **40x系**: クライアントエラー
- **30x系**: リダイレクト

#### ビジネスエラー
- **認証エラー**: 無効な認証情報
- **認可エラー**: 権限不足
- **バリデーションエラー**: 入力データ不正
- **リソースエラー**: 存在しないリソース

### 7.2 エラーレスポンス形式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが不正です",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください",
        "code": "INVALID_EMAIL"
      }
    ],
    "trace_id": "req_123456789"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 7.3 ログ設計

#### ログレベル
- **ERROR**: システムエラー、例外
- **WARN**: 警告、非推奨機能使用
- **INFO**: 重要な処理、API呼び出し
- **DEBUG**: デバッグ情報

#### ログ形式
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "chat-api",
  "trace_id": "req_123456789",
  "user_id": "user_abc",
  "message": "User login successful",
  "metadata": {
    "endpoint": "/api/v1/auth/login",
    "method": "POST",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

## 8. 監視・運用設計

### 8.1 メトリクス

#### アプリケーションメトリクス
- **レスポンス時間**: P50, P95, P99
- **スループット**: RPS (Requests Per Second)
- **エラー率**: 4xx, 5xx エラーの割合
- **アクティブユーザー数**: DAU, MAU

#### インフラメトリクス
- **CPU使用率**: ECSタスク
- **メモリ使用率**: アプリケーション
- **ディスク使用率**: RDS
- **ネットワーク**: 帯域幅、レイテンシ

### 8.2 アラート設定

#### 重要度: Critical
- **サービス停止**: 5分間連続でエラー率50%以上
- **データベース停止**: 接続エラー
- **メモリ不足**: 使用率90%以上

#### 重要度: Warning
- **レスポンス遅延**: P95 > 2秒
- **エラー率上昇**: 10%以上
- **ディスク使用率**: 80%以上

## 9. 開発・デプロイ設計

### 9.1 開発フロー

```
Feature Branch → Development → Staging → Production
      ↓               ↓            ↓           ↓
   Unit Tests    Integration    E2E Tests   Monitoring
                     Tests
```

### 9.2 CI/CD パイプライン

#### GitHub Actions Workflow
```yaml
1. Code Push/PR
2. Lint & Type Check
3. Unit Tests
4. Build Docker Images
5. Security Scan
6. Deploy to Staging
7. Integration Tests
8. Manual Approval
9. Deploy to Production
10. Monitoring Alert
```

### 9.3 環境構成

#### Development
- **目的**: 開発・デバッグ
- **データ**: サンプルデータ
- **リソース**: 最小構成

#### Staging
- **目的**: 統合テスト・品質保証
- **データ**: 本番類似データ
- **リソース**: 本番同等構成

#### Production
- **目的**: 本番サービス
- **データ**: 実データ
- **リソース**: 高可用性構成

## 10. 将来拡張設計

### 10.1 機能拡張

#### Phase 2 機能
- **音声・ビデオ通話**: WebRTC
- **スレッド機能**: メッセージスレッド
- **リアクション**: カスタム絵文字
- **検索機能**: Elasticsearch

#### Phase 3 機能
- **モバイルアプリ**: React Native
- **AI機能**: 要約、翻訳
- **インテグレーション**: 外部サービス連携
- **ワークフロー**: Bot、自動化

### 10.2 技術的改善

#### マイクロサービス化
- **認証サービス**: 独立したサービス
- **通知サービス**: プッシュ通知専用
- **ファイルサービス**: アップロード・変換専用
- **検索サービス**: 全文検索専用

#### 新技術導入
- **GraphQL**: 柔軟なデータ取得
- **gRPC**: サービス間通信
- **Kubernetes**: より柔軟なオーケストレーション
- **サーバーレス**: 特定機能のLambda化

## 11. 制約・前提条件

### 11.1 技術的制約
- **PostgreSQL**: ACID特性が必要
- **WebSocket**: リアルタイム通信必須
- **JWT**: ステートレス認証
- **S3**: ファイルストレージ

### 11.2 ビジネス制約
- **同時接続数**: 1000ユーザー以上
- **レスポンス時間**: 2秒以内
- **可用性**: 99.9%以上
- **セキュリティ**: SOC2準拠

### 11.3 運用制約
- **24時間監視**: アラート対応
- **バックアップ**: 日次バックアップ
- **災害復旧**: 4時間以内復旧
- **セキュリティパッチ**: 月次適用