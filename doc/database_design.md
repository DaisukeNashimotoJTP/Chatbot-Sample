# データベース設計書

## 1. 概要

### 1.1 データベース情報
- **DBMS**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **マイグレーション**: Alembic
- **接続プール**: SQLAlchemy Connection Pool
- **キャラクターセット**: UTF-8

### 1.2 設計方針
- 正規化を基本とし、パフォーマンス要件に応じて非正規化を検討
- UUIDを主キーとして使用（セキュリティとスケーラビリティのため）
- 作成日時・更新日時は全テーブルに共通で付与
- 論理削除を基本とし、物理削除は管理者操作のみ
- インデックス設計でクエリパフォーマンスを最適化

## 2. ER図

```
[Users] 1----* [UserWorkspaces] *----1 [Workspaces]
   |                                        |
   |                                        |
   1                                        1
   |                                        |
   *                                        *
[Messages] *----1 [Channels] *----1 [WorkspaceChannels]
   |              |
   |              |
   *              *
[MessageReactions] [ChannelMembers]
   |              |
   *              *
[Reactions]    [Users]

[Users] 1----* [Files]
[Messages] 1----* [MessageFiles] *----1 [Files]
[Messages] 1----* [Messages] (reply_to)
```

## 3. テーブル設計

### 3.1 users（ユーザー）
ユーザーアカウント情報を管理

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ユーザーID |
| username | VARCHAR(50) | UNIQUE NOT NULL | | ユーザー名（@username形式） |
| email | VARCHAR(255) | UNIQUE NOT NULL | | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | | ハッシュ化されたパスワード |
| display_name | VARCHAR(100) | NOT NULL | | 表示名 |
| avatar_url | TEXT | | | アバター画像URL |
| status | VARCHAR(20) | NOT NULL | 'active' | ユーザー状態（active/inactive/suspended） |
| timezone | VARCHAR(50) | | 'UTC' | タイムゾーン |
| last_seen_at | TIMESTAMP | | | 最終アクセス日時 |
| email_verified | BOOLEAN | NOT NULL | false | メール認証済みフラグ |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |
| deleted_at | TIMESTAMP | | | 論理削除日時 |

**インデックス:**
- idx_users_username (username)
- idx_users_email (email)
- idx_users_status (status)
- idx_users_last_seen_at (last_seen_at)

### 3.2 workspaces（ワークスペース）
チームやプロジェクトのワークスペース情報

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ワークスペースID |
| name | VARCHAR(100) | NOT NULL | | ワークスペース名 |
| slug | VARCHAR(50) | UNIQUE NOT NULL | | URL用スラッグ |
| description | TEXT | | | 説明 |
| avatar_url | TEXT | | | ワークスペースアイコンURL |
| owner_id | UUID | NOT NULL REFERENCES users(id) | | オーナーユーザーID |
| is_public | BOOLEAN | NOT NULL | false | 公開フラグ |
| invite_code | VARCHAR(50) | UNIQUE | | 招待コード |
| max_members | INTEGER | | 1000 | 最大メンバー数 |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |
| deleted_at | TIMESTAMP | | | 論理削除日時 |

**インデックス:**
- idx_workspaces_slug (slug)
- idx_workspaces_owner_id (owner_id)
- idx_workspaces_invite_code (invite_code)

### 3.3 user_workspaces（ユーザー・ワークスペース関連）
ユーザーのワークスペース参加情報

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ID |
| user_id | UUID | NOT NULL REFERENCES users(id) | | ユーザーID |
| workspace_id | UUID | NOT NULL REFERENCES workspaces(id) | | ワークスペースID |
| role | VARCHAR(20) | NOT NULL | 'member' | 役割（owner/admin/member/guest） |
| joined_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 参加日時 |
| left_at | TIMESTAMP | | | 退出日時 |

**制約:**
- UNIQUE(user_id, workspace_id)

**インデックス:**
- idx_user_workspaces_user_id (user_id)
- idx_user_workspaces_workspace_id (workspace_id)
- idx_user_workspaces_role (role)

### 3.4 channels（チャンネル）
チャンネル情報

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | チャンネルID |
| workspace_id | UUID | NOT NULL REFERENCES workspaces(id) | | ワークスペースID |
| name | VARCHAR(80) | NOT NULL | | チャンネル名（#なし） |
| description | TEXT | | | チャンネル説明 |
| type | VARCHAR(20) | NOT NULL | 'public' | タイプ（public/private/direct） |
| created_by | UUID | NOT NULL REFERENCES users(id) | | 作成者ID |
| is_archived | BOOLEAN | NOT NULL | false | アーカイブフラグ |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |
| deleted_at | TIMESTAMP | | | 論理削除日時 |

**制約:**
- UNIQUE(workspace_id, name) WHERE deleted_at IS NULL

**インデックス:**
- idx_channels_workspace_id (workspace_id)
- idx_channels_type (type)
- idx_channels_created_by (created_by)
- idx_channels_name_workspace (workspace_id, name)

### 3.5 channel_members（チャンネルメンバー）
チャンネル参加者情報

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ID |
| channel_id | UUID | NOT NULL REFERENCES channels(id) | | チャンネルID |
| user_id | UUID | NOT NULL REFERENCES users(id) | | ユーザーID |
| role | VARCHAR(20) | NOT NULL | 'member' | 役割（admin/member） |
| joined_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 参加日時 |
| last_read_at | TIMESTAMP | | | 最後に読んだ日時 |
| notification_level | VARCHAR(20) | NOT NULL | 'all' | 通知レベル（all/mentions/none） |
| left_at | TIMESTAMP | | | 退出日時 |

**制約:**
- UNIQUE(channel_id, user_id)

**インデックス:**
- idx_channel_members_channel_id (channel_id)
- idx_channel_members_user_id (user_id)
- idx_channel_members_last_read_at (last_read_at)

### 3.6 messages（メッセージ）
チャット メッセージ

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | メッセージID |
| channel_id | UUID | NOT NULL REFERENCES channels(id) | | チャンネルID |
| user_id | UUID | NOT NULL REFERENCES users(id) | | 送信者ID |
| content | TEXT | | | メッセージ内容 |
| message_type | VARCHAR(20) | NOT NULL | 'text' | メッセージタイプ（text/file/system） |
| reply_to | UUID | REFERENCES messages(id) | | 返信先メッセージID |
| thread_ts | TIMESTAMP | | | スレッドタイムスタンプ |
| is_edited | BOOLEAN | NOT NULL | false | 編集済みフラグ |
| edited_at | TIMESTAMP | | | 編集日時 |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |
| deleted_at | TIMESTAMP | | | 論理削除日時 |

**インデックス:**
- idx_messages_channel_id_created_at (channel_id, created_at DESC)
- idx_messages_user_id (user_id)
- idx_messages_reply_to (reply_to)
- idx_messages_thread_ts (thread_ts)
- idx_messages_content_gin (content) USING gin(to_tsvector('english', content))

### 3.7 files（ファイル）
アップロードファイル情報

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ファイルID |
| workspace_id | UUID | NOT NULL REFERENCES workspaces(id) | | ワークスペースID |
| uploaded_by | UUID | NOT NULL REFERENCES users(id) | | アップロード者ID |
| filename | VARCHAR(255) | NOT NULL | | オリジナルファイル名 |
| file_size | BIGINT | NOT NULL | | ファイルサイズ（bytes） |
| mime_type | VARCHAR(100) | NOT NULL | | MIMEタイプ |
| storage_path | TEXT | NOT NULL | | ストレージパス（S3キー） |
| thumbnail_path | TEXT | | | サムネイルパス |
| is_public | BOOLEAN | NOT NULL | false | 公開フラグ |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| deleted_at | TIMESTAMP | | | 論理削除日時 |

**インデックス:**
- idx_files_workspace_id (workspace_id)
- idx_files_uploaded_by (uploaded_by)
- idx_files_mime_type (mime_type)

### 3.8 message_files（メッセージ・ファイル関連）
メッセージに添付されたファイル

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ID |
| message_id | UUID | NOT NULL REFERENCES messages(id) | | メッセージID |
| file_id | UUID | NOT NULL REFERENCES files(id) | | ファイルID |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |

**制約:**
- UNIQUE(message_id, file_id)

**インデックス:**
- idx_message_files_message_id (message_id)
- idx_message_files_file_id (file_id)

### 3.9 reactions（リアクション定義）
使用可能なリアクション（絵文字）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | リアクションID |
| workspace_id | UUID | REFERENCES workspaces(id) | | ワークスペースID（NULLの場合はシステム共通） |
| name | VARCHAR(50) | NOT NULL | | リアクション名 |
| emoji_code | VARCHAR(50) | NOT NULL | | 絵文字コード |
| image_url | TEXT | | | カスタム絵文字URL |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |

**制約:**
- UNIQUE(workspace_id, name)

**インデックス:**
- idx_reactions_workspace_id (workspace_id)
- idx_reactions_name (name)

### 3.10 message_reactions（メッセージリアクション）
メッセージに対するリアクション

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | ID |
| message_id | UUID | NOT NULL REFERENCES messages(id) | | メッセージID |
| user_id | UUID | NOT NULL REFERENCES users(id) | | リアクション者ID |
| reaction_id | UUID | NOT NULL REFERENCES reactions(id) | | リアクションID |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |

**制約:**
- UNIQUE(message_id, user_id, reaction_id)

**インデックス:**
- idx_message_reactions_message_id (message_id)
- idx_message_reactions_user_id (user_id)

## 4. 制約・ルール

### 4.1 業務制約
- ユーザー名は3-50文字、英数字とハイフン、アンダースコアのみ
- チャンネル名は1-80文字、英数字とハイフン、アンダースコアのみ
- メッセージ最大長は4000文字
- ファイルサイズ上限は100MB
- ワークスペース最大メンバー数は1000人（デフォルト）

### 4.2 データ整合性制約
- 論理削除されたワークスペースに新規チャンネル作成不可
- アーカイブされたチャンネルへの新規メッセージ送信不可
- 退出したチャンネルのメッセージは参照不可
- DMチャンネルはメンバー数2人固定

## 5. パフォーマンス考慮事項

### 5.1 パーティショニング（将来検討）
- `messages` テーブルの時系列パーティショニング（月単位）
- `files` テーブルのワークスペース別パーティショニング

### 5.2 キャッシュ戦略
- よく使用されるワークスペース・チャンネル情報をRedisキャッシュ
- 未読メッセージ数の集計結果キャッシュ
- ユーザーセッション情報のキャッシュ

### 5.3 読み取り専用レプリカ
- メッセージ履歴検索用の読み取り専用レプリカ構成
- レポート・分析クエリの分離

## 6. セキュリティ考慮事項

### 6.1 データ暗号化
- パスワードはbcryptでハッシュ化
- 機密データは保存時暗号化（AWS RDS暗号化）
- 通信はTLS暗号化

### 6.2 アクセス制御
- 行レベルセキュリティ（RLS）の適用検討
- ワークスペース・チャンネル単位でのデータアクセス制限
- 監査ログテーブルの追加検討

## 7. 運用・監視

### 7.1 監視対象
- 接続数・クエリ実行時間
- テーブルサイズ・インデックス使用率
- 長時間実行クエリの検出

### 7.2 メンテナンス
- 定期的なVACUUM・ANALYZE実行
- 不要な論理削除データのパージ処理
- インデックス断片化の監視・再構築