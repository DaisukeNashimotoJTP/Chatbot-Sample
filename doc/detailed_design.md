# 詳細設計書

## 1. 概要

### 1.1 目的
本書は、Slackライクなチャットサービスの詳細設計について記載する。各コンポーネントの具体的な実装仕様、クラス設計、処理シーケンス、およびインターフェース定義を詳述する。

### 1.2 対象読者
- 開発者
- テスター
- コードレビュアー

### 1.3 関連ドキュメント
- [基本設計書](./basic_design.md)
- [API仕様書](./api_specification.md)
- [データベース設計書](./database_design.md)

## 2. バックエンド詳細設計

### 2.1 プロジェクト構造

```
backend/
├── app/
│   ├── main.py                    # FastAPIアプリケーション
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 設定クラス
│   │   ├── database.py            # データベース接続
│   │   ├── security.py            # 認証・認可
│   │   ├── exceptions.py          # カスタム例外
│   │   └── middleware.py          # ミドルウェア
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # ベースモデル
│   │   ├── user.py                # ユーザーモデル
│   │   ├── workspace.py           # ワークスペースモデル
│   │   ├── channel.py             # チャンネルモデル
│   │   ├── message.py             # メッセージモデル
│   │   └── file.py                # ファイルモデル
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py              # 共通スキーマ
│   │   ├── user.py                # ユーザースキーマ
│   │   ├── workspace.py           # ワークスペーススキーマ
│   │   ├── channel.py             # チャンネルスキーマ
│   │   ├── message.py             # メッセージスキーマ
│   │   └── auth.py                # 認証スキーマ
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # 依存関係
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py            # 認証API
│   │       ├── users.py           # ユーザーAPI
│   │       ├── workspaces.py      # ワークスペースAPI
│   │       ├── channels.py        # チャンネルAPI
│   │       ├── messages.py        # メッセージAPI
│   │       └── files.py           # ファイルAPI
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # 認証サービス
│   │   ├── user_service.py        # ユーザーサービス
│   │   ├── workspace_service.py   # ワークスペースサービス
│   │   ├── channel_service.py     # チャンネルサービス
│   │   ├── message_service.py     # メッセージサービス
│   │   └── file_service.py        # ファイルサービス
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                # ベースリポジトリ
│   │   ├── user_repository.py     # ユーザーリポジトリ
│   │   ├── workspace_repository.py
│   │   ├── channel_repository.py
│   │   ├── message_repository.py
│   │   └── file_repository.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── email.py               # メール送信
│   │   ├── file_handler.py        # ファイル処理
│   │   ├── websocket_manager.py   # WebSocket管理
│   │   └── cache.py               # キャッシュ操作
│   └── websocket/
│       ├── __init__.py
│       ├── connection_manager.py   # 接続管理
│       ├── handlers.py            # WebSocketハンドラー
│       └── events.py              # イベント定義
```

### 2.2 データモデル詳細設計

#### 2.2.1 ベースモデル

```python
# app/models/base.py
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

#### 2.2.2 ユーザーモデル

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    timezone = Column(String(50), default="UTC")
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user_workspaces = relationship("UserWorkspace", back_populates="user")
    channel_members = relationship("ChannelMember", back_populates="user")
    messages = relationship("Message", back_populates="user")
    files = relationship("File", back_populates="uploaded_by_user")
    
    def is_active(self) -> bool:
        return self.status == "active" and self.deleted_at is None
```

#### 2.2.3 ワークスペースモデル

```python
# app/models/workspace.py
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Workspace(BaseModel):
    __tablename__ = "workspaces"
    
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    invite_code = Column(String(50), unique=True, nullable=True)
    max_members = Column(Integer, default=1000)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    user_workspaces = relationship("UserWorkspace", back_populates="workspace")
    channels = relationship("Channel", back_populates="workspace")
    files = relationship("File", back_populates="workspace")

class UserWorkspace(BaseModel):
    __tablename__ = "user_workspaces"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_workspaces")
    workspace = relationship("Workspace", back_populates="user_workspaces")
```

### 2.3 サービス層詳細設計

#### 2.3.1 認証サービス

```python
# app/services/auth_service.py
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData, UserCreate, UserLogin

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def register_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name
        )
        
        return await self.user_repository.create(user)
    
    async def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(user_id=user_id)
        except JWTError:
            raise credentials_exception
        
        user = await self.user_repository.get_by_id(token_data.user_id)
        if user is None:
            raise credentials_exception
        
        return user
```

#### 2.3.2 メッセージサービス

```python
# app/services/message_service.py
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.models.message import Message
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.repositories.channel_repository import ChannelRepository
from app.schemas.message import MessageCreate, MessageUpdate
from app.utils.websocket_manager import WebSocketManager

class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        channel_repository: ChannelRepository,
        websocket_manager: WebSocketManager
    ):
        self.message_repository = message_repository
        self.channel_repository = channel_repository
        self.websocket_manager = websocket_manager
    
    async def create_message(
        self,
        message_data: MessageCreate,
        user: User
    ) -> Message:
        # Verify user has access to channel
        channel = await self.channel_repository.get_by_id(message_data.channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        # Check if user is member of channel
        is_member = await self.channel_repository.is_user_member(
            channel.id, user.id
        )
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this channel"
            )
        
        # Create message
        message = Message(
            channel_id=message_data.channel_id,
            user_id=user.id,
            content=message_data.content,
            message_type=message_data.message_type,
            reply_to=message_data.reply_to
        )
        
        created_message = await self.message_repository.create(message)
        
        # Broadcast to WebSocket connections
        await self.websocket_manager.broadcast_to_channel(
            channel.id,
            {
                "type": "message_sent",
                "data": created_message.to_dict()
            }
        )
        
        return created_message
    
    async def get_channel_messages(
        self,
        channel_id: UUID,
        user: User,
        limit: int = 50,
        before: Optional[UUID] = None,
        after: Optional[UUID] = None
    ) -> List[Message]:
        # Verify user has access to channel
        is_member = await self.channel_repository.is_user_member(channel_id, user.id)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this channel"
            )
        
        return await self.message_repository.get_channel_messages(
            channel_id, limit, before, after
        )
    
    async def update_message(
        self,
        message_id: UUID,
        message_data: MessageUpdate,
        user: User
    ) -> Message:
        message = await self.message_repository.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user owns the message
        if message.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only edit your own messages"
            )
        
        # Update message
        updated_message = await self.message_repository.update(
            message_id, message_data.dict(exclude_unset=True)
        )
        
        # Broadcast update to WebSocket connections
        await self.websocket_manager.broadcast_to_channel(
            message.channel_id,
            {
                "type": "message_updated",
                "data": updated_message.to_dict()
            }
        )
        
        return updated_message
```

### 2.4 WebSocket詳細設計

#### 2.4.1 接続管理

```python
# app/utils/websocket_manager.py
from typing import Dict, List, Set
from uuid import UUID
from fastapi import WebSocket
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # user_id -> List[WebSocket]
        self.user_connections: Dict[UUID, List[WebSocket]] = {}
        # channel_id -> Set[user_id]
        self.channel_subscriptions: Dict[UUID, Set[UUID]] = {}
        # websocket -> user_id
        self.connection_users: Dict[WebSocket, UUID] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        self.connection_users[websocket] = user_id
    
    def disconnect(self, websocket: WebSocket):
        user_id = self.connection_users.get(websocket)
        if user_id:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
            
            # Remove from channel subscriptions
            for channel_id, users in self.channel_subscriptions.items():
                users.discard(user_id)
            
            del self.connection_users[websocket]
    
    async def subscribe_to_channel(self, user_id: UUID, channel_id: UUID):
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        
        self.channel_subscriptions[channel_id].add(user_id)
    
    async def unsubscribe_from_channel(self, user_id: UUID, channel_id: UUID):
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(user_id)
    
    async def send_personal_message(self, message: dict, user_id: UUID):
        if user_id in self.user_connections:
            connections = self.user_connections[user_id]
            await asyncio.gather(
                *[self._send_safe(conn, message) for conn in connections],
                return_exceptions=True
            )
    
    async def broadcast_to_channel(self, channel_id: UUID, message: dict):
        if channel_id in self.channel_subscriptions:
            users = self.channel_subscriptions[channel_id]
            tasks = []
            
            for user_id in users:
                if user_id in self.user_connections:
                    connections = self.user_connections[user_id]
                    tasks.extend([
                        self._send_safe(conn, message) for conn in connections
                    ])
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_safe(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            # Connection might be closed, ignore
            pass

# Singleton instance
websocket_manager = ConnectionManager()
```

#### 2.4.2 WebSocketハンドラー

```python
# app/websocket/handlers.py
from fastapi import WebSocket, WebSocketDisconnect
import json
from app.utils.websocket_manager import websocket_manager
from app.services.auth_service import AuthService
from app.services.channel_service import ChannelService

class WebSocketHandler:
    def __init__(
        self,
        auth_service: AuthService,
        channel_service: ChannelService
    ):
        self.auth_service = auth_service
        self.channel_service = channel_service
    
    async def handle_connection(self, websocket: WebSocket, token: str):
        try:
            # Authenticate user
            user = await self.auth_service.get_current_user(token)
            await websocket_manager.connect(websocket, user.id)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self.handle_message(websocket, user.id, message)
            
            except WebSocketDisconnect:
                websocket_manager.disconnect(websocket)
        
        except Exception as e:
            await websocket.close(code=1000, reason=str(e))
    
    async def handle_message(self, websocket: WebSocket, user_id: UUID, message: dict):
        message_type = message.get("type")
        data = message.get("data", {})
        
        if message_type == "subscribe":
            await self.handle_subscribe(user_id, data)
        elif message_type == "unsubscribe":
            await self.handle_unsubscribe(user_id, data)
        elif message_type == "typing":
            await self.handle_typing(user_id, data)
        elif message_type == "ping":
            await self.handle_ping(websocket)
    
    async def handle_subscribe(self, user_id: UUID, data: dict):
        channel_ids = data.get("channel_ids", [])
        
        for channel_id in channel_ids:
            # Verify user has access to channel
            is_member = await self.channel_service.is_user_member(
                channel_id, user_id
            )
            if is_member:
                await websocket_manager.subscribe_to_channel(user_id, channel_id)
    
    async def handle_typing(self, user_id: UUID, data: dict):
        channel_id = data.get("channel_id")
        typing = data.get("typing", False)
        
        if channel_id:
            await websocket_manager.broadcast_to_channel(
                channel_id,
                {
                    "type": "user_typing",
                    "data": {
                        "user_id": str(user_id),
                        "channel_id": str(channel_id),
                        "typing": typing
                    }
                }
            )
    
    async def handle_ping(self, websocket: WebSocket):
        await websocket.send_text(json.dumps({"type": "pong"}))
```

## 3. フロントエンド詳細設計

### 3.1 状態管理設計

#### 3.1.1 認証ストア

```typescript
// src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  email: string
  displayName: string
  avatarUrl?: string
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
  setUser: (user: User) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          })
          
          if (!response.ok) {
            throw new Error('Login failed')
          }
          
          const data = await response.json()
          
          set({
            user: data.data.user,
            token: data.data.access_token,
            refreshToken: data.data.refresh_token,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          set({
            error: error.message,
            isLoading: false
          })
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null
        })
      },
      
      refreshAccessToken: async () => {
        const { refreshToken } = get()
        if (!refreshToken) return
        
        try {
          const response = await fetch('/api/v1/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
          })
          
          if (!response.ok) {
            throw new Error('Token refresh failed')
          }
          
          const data = await response.json()
          
          set({
            token: data.data.access_token,
            refreshToken: data.data.refresh_token
          })
        } catch (error) {
          // Refresh failed, logout user
          get().logout()
        }
      },
      
      setUser: (user: User) => set({ user }),
      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)
```

#### 3.1.2 WebSocketストア

```typescript
// src/store/websocketStore.ts
import { create } from 'zustand'

interface WebSocketState {
  socket: WebSocket | null
  isConnected: boolean
  reconnectAttempts: number
  maxReconnectAttempts: number
  
  // Actions
  connect: (token: string) => void
  disconnect: () => void
  send: (message: any) => void
  subscribe: (channelIds: string[]) => void
  sendTyping: (channelId: string, typing: boolean) => void
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  socket: null,
  isConnected: false,
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
  
  connect: (token: string) => {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}?token=${token}`
    const socket = new WebSocket(wsUrl)
    
    socket.onopen = () => {
      set({ isConnected: true, reconnectAttempts: 0 })
    }
    
    socket.onclose = () => {
      set({ isConnected: false })
      
      // Auto-reconnect logic
      const { reconnectAttempts, maxReconnectAttempts } = get()
      if (reconnectAttempts < maxReconnectAttempts) {
        setTimeout(() => {
          set({ reconnectAttempts: reconnectAttempts + 1 })
          get().connect(token)
        }, Math.pow(2, reconnectAttempts) * 1000) // Exponential backoff
      }
    }
    
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      // Handle different message types
      switch (message.type) {
        case 'message_sent':
          useMessageStore.getState().addMessage(message.data)
          break
        case 'message_updated':
          useMessageStore.getState().updateMessage(message.data)
          break
        case 'user_typing':
          useTypingStore.getState().setUserTyping(message.data)
          break
      }
    }
    
    set({ socket })
  },
  
  disconnect: () => {
    const { socket } = get()
    if (socket) {
      socket.close()
      set({ socket: null, isConnected: false })
    }
  },
  
  send: (message: any) => {
    const { socket, isConnected } = get()
    if (socket && isConnected) {
      socket.send(JSON.stringify(message))
    }
  },
  
  subscribe: (channelIds: string[]) => {
    get().send({
      type: 'subscribe',
      data: { channel_ids: channelIds }
    })
  },
  
  sendTyping: (channelId: string, typing: boolean) => {
    get().send({
      type: 'typing',
      data: { channel_id: channelId, typing }
    })
  }
}))
```

### 3.2 コンポーネント設計

#### 3.2.1 メッセージコンポーネント

```typescript
// src/components/message/MessageList.tsx
import React, { useEffect, useRef } from 'react'
import { Message } from '@/types/message'
import { MessageItem } from './MessageItem'
import { useVirtual } from 'react-virtual'

interface MessageListProps {
  messages: Message[]
  onLoadMore?: () => void
  isLoading?: boolean
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  onLoadMore,
  isLoading
}) => {
  const parentRef = useRef<HTMLDivElement>(null)
  const previousScrollHeight = useRef<number>(0)
  
  const rowVirtualizer = useVirtual({
    size: messages.length,
    parentRef,
    estimateSize: React.useCallback(() => 60, []),
    overscan: 5
  })
  
  // Auto-scroll to bottom for new messages
  useEffect(() => {
    if (parentRef.current) {
      const { scrollHeight, scrollTop, clientHeight } = parentRef.current
      const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100
      
      if (isNearBottom) {
        parentRef.current.scrollTop = scrollHeight
      }
    }
  }, [messages])
  
  // Load more when scrolled to top
  useEffect(() => {
    const handleScroll = () => {
      if (parentRef.current && onLoadMore) {
        const { scrollTop } = parentRef.current
        if (scrollTop < 100 && !isLoading) {
          onLoadMore()
        }
      }
    }
    
    const element = parentRef.current
    element?.addEventListener('scroll', handleScroll)
    return () => element?.removeEventListener('scroll', handleScroll)
  }, [onLoadMore, isLoading])
  
  return (
    <div
      ref={parentRef}
      className="flex-1 overflow-auto p-4 space-y-4"
      style={{ height: '100%' }}
    >
      <div
        style={{
          height: `${rowVirtualizer.totalSize}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {rowVirtualizer.virtualItems.map((virtualItem) => {
          const message = messages[virtualItem.index]
          
          return (
            <div
              key={message.id}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`
              }}
            >
              <MessageItem message={message} />
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

#### 3.2.2 メッセージ入力コンポーネント

```typescript
// src/components/message/MessageInput.tsx
import React, { useState, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/Button'
import { useWebSocketStore } from '@/store/websocketStore'
import { useDebounce } from '@/hooks/useDebounce'

interface MessageInputProps {
  channelId: string
  onSendMessage: (content: string) => Promise<void>
  placeholder?: string
}

export const MessageInput: React.FC<MessageInputProps> = ({
  channelId,
  onSendMessage,
  placeholder = "メッセージを入力..."
}) => {
  const [content, setContent] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { sendTyping } = useWebSocketStore()
  
  // Debounced typing indicator
  const debouncedTyping = useDebounce((typing: boolean) => {
    sendTyping(channelId, typing)
    setIsTyping(typing)
  }, 500)
  
  const handleContentChange = useCallback((value: string) => {
    setContent(value)
    
    if (value.trim() && !isTyping) {
      debouncedTyping(true)
    } else if (!value.trim() && isTyping) {
      debouncedTyping(false)
    }
  }, [isTyping, debouncedTyping])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!content.trim() || isSending) return
    
    setIsSending(true)
    
    try {
      await onSendMessage(content.trim())
      setContent('')
      
      // Stop typing indicator
      if (isTyping) {
        sendTyping(channelId, false)
        setIsTyping(false)
      }
      
      // Focus back to textarea
      textareaRef.current?.focus()
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsSending(false)
    }
  }
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }
  
  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="p-4 border-t bg-white">
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => {
              handleContentChange(e.target.value)
              adjustTextareaHeight()
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
            disabled={isSending}
          />
        </div>
        <Button
          type="submit"
          disabled={!content.trim() || isSending}
          className="px-4 py-2"
        >
          {isSending ? '送信中...' : '送信'}
        </Button>
      </div>
    </form>
  )
}
```

### 3.3 カスタムフック

#### 3.3.1 WebSocketフック

```typescript
// src/hooks/useWebSocket.ts
import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useWebSocketStore } from '@/store/websocketStore'

export const useWebSocket = () => {
  const { token, isAuthenticated } = useAuthStore()
  const { connect, disconnect, isConnected } = useWebSocketStore()
  
  useEffect(() => {
    if (isAuthenticated && token) {
      connect(token)
    } else {
      disconnect()
    }
    
    return () => {
      disconnect()
    }
  }, [isAuthenticated, token, connect, disconnect])
  
  return { isConnected }
}
```

#### 3.3.2 リアルタイムメッセージフック

```typescript
// src/hooks/useRealtimeMessages.ts
import { useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useWebSocketStore } from '@/store/websocketStore'
import { messageApi } from '@/lib/api'

export const useRealtimeMessages = (channelId: string) => {
  const queryClient = useQueryClient()
  const { subscribe } = useWebSocketStore()
  
  // Subscribe to channel on mount
  useEffect(() => {
    if (channelId) {
      subscribe([channelId])
    }
  }, [channelId, subscribe])
  
  // Fetch initial messages
  const {
    data: messages,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage
  } = useQuery({
    queryKey: ['messages', channelId],
    queryFn: ({ pageParam = null }) =>
      messageApi.getChannelMessages(channelId, {
        limit: 50,
        before: pageParam
      }),
    getNextPageParam: (lastPage) => {
      if (lastPage.data.has_more) {
        const messages = lastPage.data.messages
        return messages[messages.length - 1].id
      }
      return undefined
    },
    enabled: !!channelId
  })
  
  return {
    messages: messages?.pages.flatMap(page => page.data.messages) || [],
    isLoading,
    error,
    loadMore: fetchNextPage,
    hasMore: hasNextPage,
    isLoadingMore: isFetchingNextPage
  }
}
```

## 4. シーケンス図

### 4.1 ユーザーログインシーケンス

```
User → Frontend → Backend → Database
 |        |         |         |
 |------->|         |         |
 | Login  |         |         |
 | Form   |         |         |
 |        |-------->|         |
 |        | POST    |         |
 |        | /auth/  |         |
 |        | login   |-------->|
 |        |         | SELECT  |
 |        |         | user    |
 |        |         |<--------|
 |        |         | user    |
 |        |         | data    |
 |        |<--------|         |
 |        | JWT     |         |
 |        | token   |         |
 |<-------|         |         |
 | Success|         |         |
 | & token|         |         |
```

### 4.2 リアルタイムメッセージ送信シーケンス

```
User A → Frontend A → WebSocket → Backend → Database → WebSocket → Frontend B → User B
  |         |           |          |         |          |           |          |
  |-------->|           |          |         |          |           |          |
  | Type    |           |          |         |          |           |          |
  | message |---------->|          |         |          |           |          |
  |         | Send      |--------->|         |          |           |          |
  |         | message   | POST     |-------->|          |           |          |
  |         |           | /message | INSERT  |          |           |          |
  |         |           |          | message |          |           |          |
  |         |           |          |<--------|          |           |          |
  |         |           |          | message |          |           |          |
  |         |           |          | created |--------->|           |          |
  |         |           |          |         | broadcast|---------->|          |
  |         |           |          |         |          | message   |--------->|
  |         |           |          |         |          | event     | Display  |
  |         |           |          |         |          |           | message  |
```

### 4.3 ファイルアップロードシーケンス

```
User → Frontend → Backend → S3 → Database
 |        |         |       |       |
 |------->|         |       |       |
 | Select |         |       |       |
 | file   |-------->|       |       |
 |        | POST    |------>|       |
 |        | /files/ | PUT   |       |
 |        | upload  | object|       |
 |        |         |<------|       |
 |        |         | URL   |------>|
 |        |         |       | INSERT|
 |        |         |       | file  |
 |        |         |       | meta  |
 |        |         |       |<------|
 |        |<--------|       | file  |
 | File   | file    |       | record|
 | URL    | info    |       |       |
```

## 5. パフォーマンス考慮事項

### 5.1 フロントエンド最適化

#### 仮想化
- **React Virtual**: 大量メッセージリストの仮想化
- **Intersection Observer**: 遅延読み込み

#### メモ化
- **React.memo**: コンポーネントの不要な再レンダー防止
- **useMemo/useCallback**: 重い計算処理のキャッシュ

#### 画像最適化
- **Next.js Image**: 自動最適化
- **Lazy loading**: 遅延読み込み

### 5.2 バックエンド最適化

#### データベース
- **接続プール**: SQLAlchemy connection pool
- **インデックス**: 検索最適化
- **N+1問題**: Eager loading

#### キャッシュ
- **Redis**: セッション、頻繁アクセスデータ
- **アプリケーションキャッシュ**: メモリ内キャッシュ

#### 非同期処理
- **asyncio**: I/O集約処理の非同期化
- **バックグラウンドタスク**: Celery（将来）

## 6. セキュリティ実装

### 6.1 認証・認可実装

```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    if not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user

async def require_workspace_member(
    workspace_id: UUID,
    user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends()
):
    is_member = await workspace_service.is_user_member(workspace_id, user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )
    return user
```

### 6.2 入力検証

```python
# app/schemas/message.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID

class MessageCreate(BaseModel):
    channel_id: UUID
    content: str = Field(..., min_length=1, max_length=4000)
    message_type: str = Field(default="text", regex="^(text|file|system)$")
    reply_to: Optional[UUID] = None
    
    @validator('content')
    def validate_content(cls, v):
        # Remove potential XSS
        import html
        return html.escape(v.strip())
```

このように、詳細設計書では実装レベルでの具体的な設計を示し、開発者が直接コードを書けるレベルまで詳細化しています。