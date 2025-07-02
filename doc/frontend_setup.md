# フロントエンド開発環境セットアップガイド

## 1. 概要

Next.js を使用したフロントエンド Web アプリケーションの開発環境セットアップ手順を説明します。

## 2. 前提条件

- Node.js 18.0+ がインストールされていること
- npm または yarn がインストールされていること
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
cp .env.example .env.local

# 必要に応じて .env.local ファイルを編集
vim .env.local
```

## 4. フロントエンド環境構築

### 4.1 Node.js バージョン確認

```bash
# Node.js バージョン確認
node --version  # v18.0+ であることを確認

# npm バージョン確認
npm --version
```

### 4.2 依存関係インストール

```bash
cd frontend

# 依存関係インストール
npm install

# または yarn を使用する場合
yarn install
```

### 4.3 アプリケーション起動

```bash
# 開発サーバー起動
npm run dev

# または yarn を使用する場合
yarn dev
```

アプリケーションが起動したら以下のURLでアクセス可能：
- Web アプリケーション: http://localhost:3000

## 5. 開発用コマンド

### 5.1 ビルド関連

```bash
# 本番用ビルド
npm run build

# ビルド後のアプリケーション起動
npm run start

# 型チェック
npm run type-check

# リント
npm run lint

# リント修正
npm run lint:fix

# フォーマット
npm run format

# フォーマットチェック
npm run format:check
```

### 5.2 テスト関連

```bash
# 単体テスト実行
npm test

# ウォッチモードでテスト実行
npm run test:watch

# カバレッジ付きテスト実行
npm run test:coverage

# E2E テスト実行
npm run test:e2e

# E2E テスト（ヘッドレスモード）
npm run test:e2e:headless

# ビジュアル回帰テスト
npm run test:visual
```

### 5.3 開発支援

```bash
# Storybook 起動
npm run storybook

# Storybook ビルド
npm run build-storybook

# Bundle Analyzer
npm run analyze

# 依存関係の脆弱性チェック
npm audit

# 依存関係の更新
npm update
```

## 6. プロジェクト構造

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── images/
│   └── icons/
├── src/
│   ├── app/                 # App Router (Next.js 13+)
│   │   ├── layout.tsx       # ルートレイアウト
│   │   ├── page.tsx         # ホームページ
│   │   ├── globals.css      # グローバルスタイル
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── workspace/
│   │   │   └── [id]/
│   │   └── api/             # API Routes
│   ├── components/
│   │   ├── ui/              # 基本UIコンポーネント
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── index.ts
│   │   ├── layout/          # レイアウトコンポーネント
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── auth/            # 認証関連コンポーネント
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── workspace/       # ワークスペース関連
│   │   │   ├── WorkspaceList.tsx
│   │   │   └── WorkspaceCard.tsx
│   │   ├── channel/         # チャンネル関連
│   │   │   ├── ChannelList.tsx
│   │   │   └── ChannelItem.tsx
│   │   └── message/         # メッセージ関連
│   │       ├── MessageList.tsx
│   │       ├── MessageItem.tsx
│   │       └── MessageInput.tsx
│   ├── hooks/               # カスタムフック
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   ├── useLocalStorage.ts
│   │   └── useDebounce.ts
│   ├── lib/                 # ユーティリティ・設定
│   │   ├── api.ts           # API クライアント
│   │   ├── auth.ts          # 認証設定
│   │   ├── utils.ts         # ユーティリティ関数
│   │   ├── validations.ts   # バリデーション
│   │   └── constants.ts     # 定数
│   ├── store/               # 状態管理
│   │   ├── authStore.ts     # 認証状態
│   │   ├── workspaceStore.ts # ワークスペース状態
│   │   ├── channelStore.ts  # チャンネル状態
│   │   └── messageStore.ts  # メッセージ状態
│   ├── types/               # 型定義
│   │   ├── auth.ts
│   │   ├── workspace.ts
│   │   ├── channel.ts
│   │   ├── message.ts
│   │   └── api.ts
│   └── styles/              # スタイル
│       ├── globals.css      # グローバルスタイル
│       └── components.css   # コンポーネントスタイル
├── tests/
│   ├── __mocks__/           # モック
│   ├── components/          # コンポーネントテスト
│   ├── hooks/               # フックテスト
│   ├── pages/               # ページテスト
│   └── e2e/                 # E2Eテスト
├── .storybook/              # Storybook設定
├── .next/                   # Next.jsビルド出力
├── package.json
├── next.config.js           # Next.js設定
├── tailwind.config.js       # Tailwind CSS設定
├── tsconfig.json            # TypeScript設定
├── jest.config.js           # Jest設定
├── playwright.config.ts     # Playwright設定
└── Dockerfile
```

## 7. 重要なファイル

### 7.1 package.json
プロジェクトの依存関係とスクリプト定義

```json
{
  "name": "chat-service-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

### 7.2 next.config.js
Next.js の設定

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  images: {
    domains: ['localhost', 'api.chatservice.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
```

### 7.3 tailwind.config.js
Tailwind CSS の設定

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}
```

### 7.4 src/lib/api.ts
API クライアント設定

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // トークンリフレッシュ処理
      await refreshToken()
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

## 8. 状態管理（Zustand）

### 8.1 認証状態管理

```typescript
// src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  email: string
  displayName: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (user: User, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) =>
        set({ user, token, isAuthenticated: true }),
      logout: () =>
        set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)
```

## 9. WebSocket 接続

### 9.1 WebSocket フック

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react'

interface UseWebSocketProps {
  url: string
  onMessage?: (data: any) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
}: UseWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef<WebSocket | null>(null)

  const sendMessage = (data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }

  useEffect(() => {
    ws.current = new WebSocket(url)

    ws.current.onopen = () => {
      setIsConnected(true)
      onOpen?.()
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage?.(data)
    }

    ws.current.onclose = () => {
      setIsConnected(false)
      onClose?.()
    }

    ws.current.onerror = (error) => {
      onError?.(error)
    }

    return () => {
      ws.current?.close()
    }
  }, [url])

  return { isConnected, sendMessage }
}
```

## 10. テスト戦略

### 10.1 Jest 設定

```javascript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
}

module.exports = createJestConfig(customJestConfig)
```

### 10.2 コンポーネントテスト例

```typescript
// tests/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '@/components/ui/Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### 10.3 E2E テスト例

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/auth/login')
  
  await page.fill('[data-testid=email]', 'test@example.com')
  await page.fill('[data-testid=password]', 'password')
  await page.click('[data-testid=login-button]')
  
  await expect(page).toHaveURL('/workspace')
})
```

## 11. スタイリング（Tailwind CSS）

### 11.1 基本的なクラスの使用

```tsx
// コンポーネント例
export const MessageItem = ({ message }) => {
  return (
    <div className="flex items-start space-x-3 p-4 hover:bg-gray-50">
      <img
        src={message.user.avatar}
        alt={message.user.name}
        className="w-8 h-8 rounded-full"
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">
          {message.user.name}
        </p>
        <p className="text-sm text-gray-500">
          {message.content}
        </p>
      </div>
    </div>
  )
}
```

### 11.2 カスタムコンポーネント

```tsx
// shadcn/ui風のコンポーネント
export const Button = ({ className, variant = 'default', ...props }) => {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md text-sm font-medium',
        'focus-visible:outline-none focus-visible:ring-2',
        'disabled:pointer-events-none disabled:opacity-50',
        {
          'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
          'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
          'border border-input bg-background hover:bg-accent': variant === 'outline',
        },
        className
      )}
      {...props}
    />
  )
}
```

## 12. パフォーマンス最適化

### 12.1 画像最適化

```tsx
import Image from 'next/image'

export const UserAvatar = ({ src, alt, size = 40 }) => {
  return (
    <Image
      src={src}
      alt={alt}
      width={size}
      height={size}
      className="rounded-full"
      priority={false}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  )
}
```

### 12.2 コード分割

```tsx
import dynamic from 'next/dynamic'

const MessageEditor = dynamic(
  () => import('@/components/message/MessageEditor'),
  {
    loading: () => <p>Loading...</p>,
    ssr: false,
  }
)
```

### 12.3 メモ化

```tsx
import { memo, useMemo } from 'react'

export const MessageList = memo(({ messages }) => {
  const sortedMessages = useMemo(
    () => messages.sort((a, b) => a.createdAt - b.createdAt),
    [messages]
  )

  return (
    <div>
      {sortedMessages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  )
})
```

## 13. よくある問題と解決方法

### 13.1 ハイドレーションエラー

```tsx
// 解決方法: useEffect を使用
import { useEffect, useState } from 'react'

export const ClientOnlyComponent = () => {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return null
  }

  return <div>This renders only on the client</div>
}
```

### 13.2 環境変数の問題

```bash
# .env.local で NEXT_PUBLIC_ プレフィックスを使用
NEXT_PUBLIC_API_URL=http://localhost:8000/v1

# サーバーサイドでのみ使用する場合はプレフィックス不要
DATABASE_URL=postgresql://...
```

### 13.3 TypeScript エラー

```typescript
// 型定義の追加
// types/global.d.ts
declare global {
  interface Window {
    gtag: (...args: any[]) => void
  }
}

export {}
```

## 14. デプロイ準備

### 14.1 本番用ビルド

```bash
# 本番用ビルド
npm run build

# ビルド結果の確認
npm run start
```

### 14.2 環境変数の設定

本番環境用の環境変数を適切に設定：

- `NEXT_PUBLIC_API_URL`: 本番APIのURL
- `NEXTAUTH_URL`: 本番ドメイン
- `NEXTAUTH_SECRET`: セキュアなシークレット

## 15. 監視・分析

### 15.1 Web Vitals

```tsx
// pages/_app.tsx または app/layout.tsx
export function reportWebVitals(metric) {
  console.log(metric)
  // 分析サービスに送信
}
```

### 15.2 エラー追跡

```typescript
// Sentry の設定例
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
})
```