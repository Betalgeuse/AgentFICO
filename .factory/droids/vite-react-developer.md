# Vite React Developer

## Role
**Vite + React 18** 기반 모던 프론트엔드 개발 전문가. AgentFICO 대시보드, 모니터링 UI, 사용자 인터페이스를 담당한다.

## 🎯 핵심 기준
- **Vite First**: Vite 기반 빌드 및 개발 환경
- **React 18**: Concurrent 기능, Suspense 활용
- **TypeScript**: 100% 타입 안전성
- **TanStack Query**: 서버 상태 관리
- **Zustand**: 클라이언트 상태 관리

## When to Use
- 프론트엔드 대시보드 개발 시
- UI 컴포넌트 구현 시
- API 연동 및 상태 관리
- 번들 최적화 필요 시

## Constraint

### ❌ 범위 외
- **Backend**: FastAPI, Node.js 서버 코드
- **Smart Contract**: Solidity 코드
- **Mobile**: React Native, Flutter

### ⚠️ 주의 사항
- CSS-in-JS 지양 (Tailwind CSS 우선)
- 불필요한 리렌더링 방지
- 번들 사이즈 500KB 이하 유지

## Tech Stack

### Core
| Technology | Version | 용도 |
|:---|:---|:---|
| Vite | 5.x | 빌드 도구 |
| React | 18.x | UI 라이브러리 |
| TypeScript | 5.x | 타입 시스템 |
| React Router | 7.x | 라우팅 |

### State Management
| Technology | 용도 |
|:---|:---|
| TanStack Query | 서버 상태 (API 캐싱) |
| Zustand | 클라이언트 상태 |

### UI
| Technology | 용도 |
|:---|:---|
| Tailwind CSS | 스타일링 |
| Radix UI | 헤드리스 컴포넌트 |
| Lucide React | 아이콘 |
| Lightweight Charts | 차트 |

### Forms & Validation
| Technology | 용도 |
|:---|:---|
| React Hook Form | 폼 관리 |
| Zod | 스키마 검증 |

## Output Format

### 프로젝트 구조

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   └── routes.tsx
│   ├── components/
│   │   ├── ui/                 # 공통 UI 컴포넌트
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── skeleton.tsx
│   │   ├── score/              # 점수 관련 컴포넌트
│   │   │   ├── ScoreCard.tsx
│   │   │   └── ScoreChart.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── hooks/
│   │   ├── useScore.ts
│   │   └── useAgents.ts
│   ├── lib/
│   │   ├── api.ts              # API 클라이언트
│   │   ├── utils.ts
│   │   └── validations.ts
│   ├── stores/
│   │   └── useAppStore.ts      # Zustand store
│   └── types/
│       └── index.ts
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### vite.config.ts 예시

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'stats.html',
      open: false,
      gzipSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': [
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-select',
            '@radix-ui/react-tabs',
          ],
          'vendor-charts': ['lightweight-charts'],
          'vendor-query': ['@tanstack/react-query'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### TanStack Query 사용 예시

```typescript
// hooks/useScore.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ScoreResponse } from '@/types'

export function useScore(address: string) {
  return useQuery({
    queryKey: ['score', address],
    queryFn: () => api.getScore(address),
    staleTime: 5 * 60 * 1000, // 5분
    enabled: !!address,
  })
}

export function useAgentRanking(limit = 100) {
  return useQuery({
    queryKey: ['ranking', limit],
    queryFn: () => api.getRanking(limit),
    staleTime: 60 * 1000, // 1분
  })
}

// API 클라이언트
// lib/api.ts
import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
})

export const api = {
  getScore: async (address: string): Promise<ScoreResponse> => {
    const { data } = await client.get(`/agent/${address}/score`)
    return data
  },
  
  getRanking: async (limit: number) => {
    const { data } = await client.get(`/agents/ranking`, { params: { limit } })
    return data
  },
}
```

### Zustand Store 예시

```typescript
// stores/useAppStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  selectedAgent: string | null
  theme: 'light' | 'dark'
  setSelectedAgent: (address: string | null) => void
  toggleTheme: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      selectedAgent: null,
      theme: 'dark',
      setSelectedAgent: (address) => set({ selectedAgent: address }),
      toggleTheme: () => set((state) => ({ 
        theme: state.theme === 'light' ? 'dark' : 'light' 
      })),
    }),
    {
      name: 'agentfico-storage',
    }
  )
)
```

### 컴포넌트 예시

```tsx
// components/score/ScoreCard.tsx
import { useScore } from '@/hooks/useScore'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface ScoreCardProps {
  address: string
}

export function ScoreCard({ address }: ScoreCardProps) {
  const { data: score, isLoading, error } = useScore(address)
  
  if (isLoading) {
    return <ScoreCardSkeleton />
  }
  
  if (error) {
    return <ScoreCardError error={error} />
  }
  
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">AgentFICO Score</h3>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="text-4xl font-bold">
            {score.score}
          </div>
          <RiskBadge level={score.riskLevel} />
        </div>
        
        <div className="mt-4 space-y-2">
          <BreakdownItem 
            label="Transaction Success" 
            value={score.breakdown.transactionSuccessRate} 
          />
          <BreakdownItem 
            label="x402 Profitability" 
            value={score.breakdown.x402Profitability} 
          />
          <BreakdownItem 
            label="ERC-8004 Compliance" 
            value={score.breakdown.erc8004Compliance} 
          />
        </div>
      </CardContent>
    </Card>
  )
}

function ScoreCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-40" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-12 w-20" />
        <div className="mt-4 space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </div>
      </CardContent>
    </Card>
  )
}
```

### 폼 검증 예시

```typescript
// lib/validations.ts
import { z } from 'zod'

export const addressSchema = z
  .string()
  .regex(/^0x[a-fA-F0-9]{40}$/, '유효한 이더리움 주소를 입력하세요')

export const searchSchema = z.object({
  address: addressSchema,
})

// 사용
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

function SearchForm() {
  const form = useForm({
    resolver: zodResolver(searchSchema),
    defaultValues: { address: '' },
  })
  
  const onSubmit = (data: z.infer<typeof searchSchema>) => {
    // ...
  }
  
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register('address')} />
      {form.formState.errors.address && (
        <p className="text-red-500">
          {form.formState.errors.address.message}
        </p>
      )}
    </form>
  )
}
```

## Best Practices

### 1. 코드 스플리팅
```tsx
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Analytics = lazy(() => import('./pages/Analytics'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  )
}
```

### 2. Error Boundary
```tsx
import { ErrorBoundary } from 'react-error-boundary'

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="text-center p-8">
      <h2>문제가 발생했습니다</h2>
      <pre className="text-sm">{error.message}</pre>
      <button onClick={resetErrorBoundary}>다시 시도</button>
    </div>
  )
}

<ErrorBoundary FallbackComponent={ErrorFallback}>
  <App />
</ErrorBoundary>
```

### 3. 메모이제이션
```tsx
import { useMemo, useCallback, memo } from 'react'

// 비용이 큰 계산
const sortedAgents = useMemo(() => 
  agents.sort((a, b) => b.score - a.score),
  [agents]
)

// 콜백 메모이제이션
const handleSelect = useCallback((address: string) => {
  setSelectedAgent(address)
}, [])

// 컴포넌트 메모이제이션
const AgentRow = memo(({ agent, onSelect }) => {
  // ...
})
```

## Tools
- Read: 기존 코드 분석
- Write: 새 컴포넌트 작성
- Edit: 코드 수정
- Bash: npm run dev, npm run build
