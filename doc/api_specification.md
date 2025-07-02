# API仕様書

## 1. 概要

### 1.1 API情報
- **ベースURL**: `https://api.chatservice.com/v1`
- **プロトコル**: HTTPS
- **認証方式**: JWT Bearer Token
- **データフォーマット**: JSON
- **文字エンコーディング**: UTF-8

### 1.2 バージョニング
- URLパスによるバージョニング (`/v1/`, `/v2/`)
- 後方互換性を保ちながら段階的に更新

### 1.3 レスポンス形式
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 2. 認証・認可

### 2.1 JWT トークン
- **Header**: `Authorization: Bearer <token>`
- **有効期限**: 24時間
- **リフレッシュトークン**: 30日間

### 2.2 認証エンドポイント

#### POST /auth/register
ユーザー登録

**リクエスト:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securePassword123!",
  "display_name": "John Doe"
}
```

**レスポンス (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com",
      "display_name": "John Doe",
      "avatar_url": null,
      "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  }
}
```

**エラー (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが不正です",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください"
      }
    ]
  }
}
```

#### POST /auth/login
ユーザーログイン

**リクエスト:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123!"
}
```

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com",
      "display_name": "John Doe",
      "avatar_url": null,
      "last_seen_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  }
}
```

#### POST /auth/refresh
トークンリフレッシュ

**リクエスト:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/logout
ログアウト（トークン無効化）

**レスポンス (200):**
```json
{
  "success": true,
  "message": "ログアウトしました"
}
```

#### GET /auth/me
現在のユーザー情報取得

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "johndoe",
    "email": "john@example.com",
    "display_name": "John Doe",
    "avatar_url": "https://cdn.example.com/avatars/john.jpg",
    "timezone": "Asia/Tokyo",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## 3. ワークスペース API

#### GET /workspaces
ユーザーが参加しているワークスペース一覧

**クエリパラメータ:**
- `limit` (optional): 取得件数 (default: 50, max: 100)
- `offset` (optional): オフセット (default: 0)

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "workspaces": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "開発チーム",
        "slug": "dev-team",
        "description": "プロダクト開発用ワークスペース",
        "avatar_url": "https://cdn.example.com/workspace-avatars/dev.jpg",
        "owner_id": "550e8400-e29b-41d4-a716-446655440000",
        "is_public": false,
        "member_count": 15,
        "user_role": "admin",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 3,
    "limit": 50,
    "offset": 0
  }
}
```

#### POST /workspaces
新規ワークスペース作成

**リクエスト:**
```json
{
  "name": "新しいチーム",
  "slug": "new-team",
  "description": "新しいプロジェクト用のワークスペース",
  "is_public": false
}
```

**レスポンス (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "新しいチーム",
    "slug": "new-team",
    "description": "新しいプロジェクト用のワークスペース",
    "avatar_url": null,
    "owner_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_public": false,
    "invite_code": "abc123def",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### GET /workspaces/{workspace_id}
ワークスペース詳細取得

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "開発チーム",
    "slug": "dev-team",
    "description": "プロダクト開発用ワークスペース",
    "avatar_url": "https://cdn.example.com/workspace-avatars/dev.jpg",
    "owner_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_public": false,
    "invite_code": "xyz789abc",
    "max_members": 1000,
    "member_count": 15,
    "user_role": "admin",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### PUT /workspaces/{workspace_id}
ワークスペース情報更新

**リクエスト:**
```json
{
  "name": "開発チーム（更新）",
  "description": "更新された説明"
}
```

#### DELETE /workspaces/{workspace_id}
ワークスペース削除（論理削除）

**レスポンス (200):**
```json
{
  "success": true,
  "message": "ワークスペースを削除しました"
}
```

#### POST /workspaces/{workspace_id}/join
ワークスペース参加（招待コード使用）

**リクエスト:**
```json
{
  "invite_code": "xyz789abc"
}
```

#### POST /workspaces/{workspace_id}/leave
ワークスペース退出

## 4. チャンネル API

#### GET /workspaces/{workspace_id}/channels
ワークスペース内チャンネル一覧

**クエリパラメータ:**
- `type` (optional): チャンネルタイプ (public/private/direct)
- `limit` (optional): 取得件数
- `offset` (optional): オフセット

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "channels": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "workspace_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "general",
        "description": "一般的な話題用チャンネル",
        "type": "public",
        "member_count": 15,
        "unread_count": 3,
        "last_message": {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "display_name": "John Doe"
          },
          "content": "おはようございます！",
          "created_at": "2024-01-01T09:00:00Z"
        },
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 5
  }
}
```

#### POST /workspaces/{workspace_id}/channels
新規チャンネル作成

**リクエスト:**
```json
{
  "name": "新しいチャンネル",
  "description": "プロジェクト専用チャンネル",
  "type": "public"
}
```

#### GET /channels/{channel_id}
チャンネル詳細取得

#### PUT /channels/{channel_id}
チャンネル情報更新

#### DELETE /channels/{channel_id}
チャンネル削除

#### POST /channels/{channel_id}/join
チャンネル参加

#### POST /channels/{channel_id}/leave
チャンネル退出

#### GET /channels/{channel_id}/members
チャンネルメンバー一覧

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "members": [
      {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "johndoe",
        "display_name": "John Doe",
        "avatar_url": "https://cdn.example.com/avatars/john.jpg",
        "role": "admin",
        "joined_at": "2024-01-01T00:00:00Z",
        "last_read_at": "2024-01-01T09:00:00Z"
      }
    ],
    "total": 15
  }
}
```

## 5. メッセージ API

#### GET /channels/{channel_id}/messages
チャンネルのメッセージ一覧

**クエリパラメータ:**
- `limit` (optional): 取得件数 (default: 50, max: 100)
- `before` (optional): 指定メッセージID以前のメッセージ取得
- `after` (optional): 指定メッセージID以降のメッセージ取得
- `thread_ts` (optional): スレッドメッセージのタイムスタンプ

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "channel_id": "550e8400-e29b-41d4-a716-446655440003",
        "user": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "username": "johndoe",
          "display_name": "John Doe",
          "avatar_url": "https://cdn.example.com/avatars/john.jpg"
        },
        "content": "おはようございます！今日もよろしくお願いします。",
        "message_type": "text",
        "reply_to": null,
        "thread_ts": null,
        "is_edited": false,
        "reactions": [
          {
            "emoji_code": ":+1:",
            "count": 3,
            "users": ["user1", "user2", "user3"],
            "reacted": false
          }
        ],
        "files": [],
        "created_at": "2024-01-01T09:00:00Z",
        "updated_at": "2024-01-01T09:00:00Z"
      }
    ],
    "has_more": true,
    "total": 150
  }
}
```

#### POST /channels/{channel_id}/messages
メッセージ送信

**リクエスト:**
```json
{
  "content": "こんにちは！",
  "message_type": "text",
  "reply_to": "550e8400-e29b-41d4-a716-446655440010",
  "file_ids": []
}
```

**レスポンス (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440011",
    "channel_id": "550e8400-e29b-41d4-a716-446655440003",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "display_name": "John Doe",
      "avatar_url": "https://cdn.example.com/avatars/john.jpg"
    },
    "content": "こんにちは！",
    "message_type": "text",
    "reply_to": "550e8400-e29b-41d4-a716-446655440010",
    "created_at": "2024-01-01T09:30:00Z"
  }
}
```

#### GET /messages/{message_id}
メッセージ詳細取得

#### PUT /messages/{message_id}
メッセージ編集

**リクエスト:**
```json
{
  "content": "編集されたメッセージ内容"
}
```

#### DELETE /messages/{message_id}
メッセージ削除

#### POST /messages/{message_id}/reactions
リアクション追加

**リクエスト:**
```json
{
  "emoji_code": ":+1:"
}
```

#### DELETE /messages/{message_id}/reactions/{emoji_code}
リアクション削除

## 6. ファイル API

#### POST /files/upload
ファイルアップロード

**リクエスト (multipart/form-data):**
- `file`: アップロードするファイル
- `workspace_id`: ワークスペースID

**レスポンス (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440020",
    "filename": "document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "download_url": "https://api.chatservice.com/v1/files/550e8400-e29b-41d4-a716-446655440020/download",
    "thumbnail_url": null,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

#### GET /files/{file_id}
ファイル情報取得

#### GET /files/{file_id}/download
ファイルダウンロード

#### DELETE /files/{file_id}
ファイル削除

## 7. 検索 API

#### GET /search
全体検索

**クエリパラメータ:**
- `q`: 検索クエリ
- `type` (optional): 検索対象 (messages/files/users/channels)
- `workspace_id` (optional): ワークスペース指定
- `channel_id` (optional): チャンネル指定
- `limit` (optional): 取得件数
- `offset` (optional): オフセット
- `from` (optional): 検索開始日時
- `to` (optional): 検索終了日時

**レスポンス (200):**
```json
{
  "success": true,
  "data": {
    "results": {
      "messages": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "content": "検索にヒットしたメッセージ",
          "channel": {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "general"
          },
          "user": {
            "display_name": "John Doe"
          },
          "created_at": "2024-01-01T09:00:00Z",
          "highlight": "検索にヒットした<mark>メッセージ</mark>"
        }
      ],
      "files": [],
      "channels": [],
      "users": []
    },
    "total": {
      "messages": 15,
      "files": 0,
      "channels": 0,
      "users": 0
    }
  }
}
```

## 8. WebSocket API

### 8.1 接続
- **エンドポイント**: `wss://api.chatservice.com/v1/ws`
- **認証**: クエリパラメータまたはヘッダーでJWTトークン送信

### 8.2 接続時認証
```json
{
  "type": "auth",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 8.3 チャンネル購読
```json
{
  "type": "subscribe",
  "data": {
    "channel_ids": [
      "550e8400-e29b-41d4-a716-446655440003",
      "550e8400-e29b-41d4-a716-446655440004"
    ]
  }
}
```

### 8.4 受信イベント

#### message_sent
新しいメッセージ受信
```json
{
  "type": "message_sent",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440011",
    "channel_id": "550e8400-e29b-41d4-a716-446655440003",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "John Doe"
    },
    "content": "リアルタイムメッセージ",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

#### message_updated
メッセージ更新
```json
{
  "type": "message_updated",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440011",
    "content": "編集されたメッセージ",
    "is_edited": true,
    "edited_at": "2024-01-01T10:05:00Z"
  }
}
```

#### message_deleted
メッセージ削除
```json
{
  "type": "message_deleted",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440011",
    "channel_id": "550e8400-e29b-41d4-a716-446655440003"
  }
}
```

#### user_typing
ユーザータイピング状態
```json
{
  "type": "user_typing",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "channel_id": "550e8400-e29b-41d4-a716-446655440003",
    "typing": true
  }
}
```

#### user_presence
ユーザーオンライン状態変更
```json
{
  "type": "user_presence",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "online"
  }
}
```

### 8.5 送信イベント

#### typing
タイピング状態通知
```json
{
  "type": "typing",
  "data": {
    "channel_id": "550e8400-e29b-41d4-a716-446655440003",
    "typing": true
  }
}
```

## 9. エラーハンドリング

### 9.1 HTTPステータスコード
- `200`: 成功
- `201`: 作成成功
- `400`: リクエストエラー
- `401`: 認証エラー
- `403`: 権限エラー
- `404`: リソースが見つからない
- `409`: 競合エラー
- `422`: バリデーションエラー
- `429`: レート制限
- `500`: サーバーエラー

### 9.2 エラーレスポンス形式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが不正です",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 9.3 主要エラーコード
- `VALIDATION_ERROR`: バリデーションエラー
- `AUTHENTICATION_FAILED`: 認証失敗
- `AUTHORIZATION_FAILED`: 認可失敗
- `RESOURCE_NOT_FOUND`: リソースが見つからない
- `RESOURCE_CONFLICT`: リソース競合
- `RATE_LIMIT_EXCEEDED`: レート制限超過
- `INTERNAL_SERVER_ERROR`: サーバー内部エラー

## 10. レート制限

### 10.1 制限値
- **認証API**: 5 requests/minute per IP
- **一般API**: 100 requests/minute per user
- **メッセージ送信**: 30 requests/minute per user
- **ファイルアップロード**: 10 requests/minute per user

### 10.2 レスポンスヘッダー
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 11. ページネーション

### 11.1 オフセットベース
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### 11.2 カーソルベース（メッセージ）
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "550e8400-e29b-41d4-a716-446655440011",
    "prev_cursor": "550e8400-e29b-41d4-a716-446655440009",
    "has_more": true
  }
}
```