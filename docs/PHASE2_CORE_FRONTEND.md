# Phase 2: Core Frontend Implementation

**Status**: 🟡 **Not Started** (24-40 hours estimated)
**Duration**: 2-3 weeks
**Priority**: 🟡 **HIGH** (Blocks user testing)
**Owner**: Frontend Development Team

---

## 📋 Executive Summary

Phase 2 focuses on building the core frontend application that will consume the backend APIs implemented in Phase 1. Currently, the frontend directory is completely empty with only a `package.json` file containing dependencies. Phase 2 will create a fully functional React application with real-time collaboration, task management, and AI suggestion features.

### Current State Analysis

| Component | Status | Completion | Blocking Issues |
|-----------|--------|------------|-----------------|
| **React App Structure** | ❌ Missing | 0% | No source code |
| **Components** | ❌ Missing | 0% | No UI components |
| **State Management** | ❌ Missing | 0% | No store configured |
| **API Integration** | ❌ Missing | 0% | No API client |
| **Real-time (Socket.IO)** | ❌ Missing | 0% | No socket client |
| **Authentication UI** | ❌ Missing | 0% | No auth pages |
| **Routing** | ❌ Missing | 0% | No navigation |
| **Styling** | ❌ Missing | 0% | No design system |

### Phase 2 Objectives

1. **Build React Skeleton** - Set up project structure, routing, and state management
2. **Implement Authentication UI** - Login, signup, and protected routes
3. **Create Task Management UI** - Task list, CRUD operations, filtering
4. **Integrate Real-time Features** - Socket.IO, presence, live updates
5. **Add AI Suggestions UI** - Display and accept AI task rewrites

**Success Criteria**:
- Working React application with all core features
- User authentication flow complete
- Task CRUD operations functional
- Real-time updates working across clients
- AI suggestions displayed and actionable
- Mobile-responsive design
- Comprehensive E2E tests

---

## ✅ What's Already Done (Completed in Previous Phases)

### 2.1 Dependencies Configured ✅

**File**: `frontend/package.json`

```json
{
  "name": "pulsetasks-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "yjs": "^13.6.10",
    "y-socket.io": "^1.0.3",
    "socket.io-client": "^4.6.1",
    "zustand": "^4.5.0",
    "axios": "^1.6.5",
    "@tanstack/react-query": "^5.17.19",
    "react-router-dom": "^6.21.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.12",
    "vitest": "^1.2.1",
    "@testing-library/react": "^14.2.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/user-event": "^14.5.2",
    "playwright": "^1.41.0"
  }
}
```

**Dependencies Installed**:
- ✅ React 18.2.0 - UI framework
- ✅ Yjs 13.6.10 - CRDT for real-time collaboration
- ✅ Socket.IO Client 4.6.1 - Real-time communication
- ✅ Zustand 4.5.0 - State management
- ✅ Axios 1.6.5 - HTTP client
- ✅ React Query 5.17.19 - Data fetching & caching
- ✅ React Router 6.21.3 - Client-side routing
- ✅ TypeScript 5.3.3 - Type safety
- ✅ Vite 5.0.12 - Build tool
- ✅ Playwright 1.41.0 - E2E testing

### 2.2 Backend APIs Available ✅

**All backend endpoints from Phase 1 are available**:

```
✅ Authentication:
   POST /api/v1/auth/signup
   POST /api/v1/auth/login
   POST /api/v1/auth/refresh

✅ Tasks:
   POST /api/v1/tasks
   GET /api/v1/tasks/{id}
   GET /api/v1/tasks
   PUT /api/v1/tasks/{id}
   DELETE /api/v1/tasks/{id}

✅ AI (via Phase 1):
   POST /api/v1/ai/rewrite
   POST /api/v1/ai/prioritize

✅ Real-time (via Phase 1):
   Socket.IO events on ws://localhost:8000/socket.io/
```

---

## ❌ What's Left to Implement

### Task 2.1: Build React Skeleton (4-6 hours) 🟡 HIGH

**Current State**:
- Only `package.json` exists
- No source code files
- No project structure

**What's Missing**:

#### 2.1.1 Create Project Structure

**Directory Structure to Create**:
```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── main.tsx                   # App entry point
│   ├── App.tsx                    # Root component
│   ├── vite-env.d.ts             # Vite types
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   └── AuthProvider.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskFilter.tsx
│   │   │   ├── TaskPriorityBadge.tsx
│   │   │   └── TaskStatusBadge.tsx
│   │   ├── ai/
│   │   │   ├── AISuggestionCard.tsx
│   │   │   ├── AISuggestionList.tsx
│   │   │   └── ConfidenceBadge.tsx
│   │   ├── realtime/
│   │   │   ├── PresenceIndicator.tsx
│   │   │   ├── CursorTracker.tsx
│   │   │   └── TypingIndicator.tsx
│   │   └── crdt/
│   │       ├── YjsEditor.tsx
│   │       └── OfflineIndicator.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Signup.tsx
│   │   ├── Tasks.tsx
│   │   └── Workspace.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useTasks.ts
│   │   ├── useSocket.ts
│   │   ├── useCRDT.ts
│   │   └── useAISuggestions.ts
│   ├── store/
│   │   ├── index.ts                # Zustand store
│   │   ├── authStore.ts
│   │   ├── taskStore.ts
│   │   └── socketStore.ts
│   ├── services/
│   │   ├── api.ts                 # Axios client
│   │   ├── authService.ts         # Auth API
│   │   ├── taskService.ts         # Task API
│   │   └── socketService.ts       # Socket.IO client
│   ├── types/
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   ├── task.ts
│   │   ├── ai.ts
│   │   └── socket.ts
│   ├── utils/
│   │   ├── format.ts
│   │   ├── date.ts
│   │   └── validation.ts
│   └── styles/
│       ├── global.css
│       ├── variables.css
│       └── components.css
├── .env.example
├── .env
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tsconfig.node.json
└── playwright.config.ts
```

#### 2.1.2 Create Vite Configuration

**File**: `frontend/vite.config.ts`

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@services': path.resolve(__dirname, './src/services'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
```

#### 2.1.3 Create TypeScript Configuration

**File**: `frontend/tsconfig.json`

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@store/*": ["./src/store/*"],
      "@services/*": ["./src/services/*"],
      "@types/*": ["./src/types/*"],
      "@utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### 2.1.4 Create Environment Configuration

**File**: `frontend/.env.example`

```env
# frontend/.env.example

# API
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Application
VITE_APP_NAME=PulseTasks
VITE_APP_VERSION=0.1.0

# OAuth2 (Google)
VITE_GOOGLE_CLIENT_ID=
VITE_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google

# Features
VITE_ENABLE_AI=true
VITE_ENABLE_REALTIME=true
VITE_ENABLE_OFFLINE=true
```

**File**: `frontend/.env`

```env
# frontend/.env (for development)

VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_APP_NAME=PulseTasks
VITE_APP_VERSION=0.1.0
VITE_ENABLE_AI=true
VITE_ENABLE_REALTIME=true
VITE_ENABLE_OFFLINE=true
```

#### 2.1.5 Create Application Entry Points

**File**: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PulseTasks - Real-time Collaborative Task Management</title>
    <meta name="description" content="Real-time collaborative task management with AI-powered suggestions" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**File**: `frontend/src/main.tsx`

```typescript
// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/global.css'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
```

**File**: `frontend/src/App.tsx`

```typescript
// frontend/src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Tasks from './pages/Tasks'
import Workspace from './pages/Workspace'

// Protected route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div>Loading...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <div className="app">
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workspace/:id"
          element={
            <ProtectedRoute>
              <Workspace />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
```

#### 2.1.6 Create TypeScript Types

**File**: `frontend/src/types/index.ts`

```typescript
// frontend/src/types/index.ts
export * from './auth'
export * from './task'
export * from './ai'
export * from './socket'
```

**File**: `frontend/src/types/auth.ts`

```typescript
// frontend/src/types/auth.ts
export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  name: string
}

export interface AuthResponse {
  user: User
  tokens: AuthTokens
}
```

**File**: `frontend/src/types/task.ts`

```typescript
// frontend/src/types/task.ts
export type TaskStatus = 'OPEN' | 'IN_PROGRESS' | 'DONE'
export type TaskPriority = 1 | 2 | 3 | 4 | 5

export interface Task {
  id: string
  list_id: string
  title: string
  description: string
  assignee_id: string | null
  priority: TaskPriority
  status: TaskStatus
  due_date: string | null
  tags: string[]
  created_at: string
  updated_at: string
  last_edit_meta?: {
    user_id: string
    op_id: string
  }
}

export interface CreateTaskRequest {
  title: string
  description?: string
  assignee_id?: string
  priority?: TaskPriority
  due_date?: string
  tags?: string[]
}

export interface UpdateTaskRequest {
  title?: string
  description?: string
  assignee_id?: string | null
  priority?: TaskPriority
  status?: TaskStatus
  due_date?: string | null
  tags?: string[]
}

export interface TaskFilters {
  status?: TaskStatus
  priority?: TaskPriority
  assignee_id?: string
  due_date_before?: string
  due_date_after?: string
  search?: string
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'updated_at'
  sort_order?: 'asc' | 'desc'
}
```

**File**: `frontend/src/types/ai.ts`

```typescript
// frontend/src/types/ai.ts
export interface AISuggestion {
  task_id: string
  rewritten_title: string | null
  checklist: string[]
  suggested_priority: number | null
  suggested_due_date: string | null
  confidence: number
  explanation: string
  accepted: boolean
}

export interface AISuggestionRequest {
  raw_title: string
  raw_description?: string
  context?: Record<string, any>
}
```

**File**: `frontend/src/types/socket.ts`

```typescript
// frontend/src/types/socket.ts
export interface SocketEvents {
  // Server → Client
  presence_update: {
    user_id: string
    status: 'online' | 'offline' | 'away'
    workspace_id: string
  }

  ydoc_update: {
    document_id: string
    ops: Uint8Array
  }

  task_broadcast: {
    task_id: string
    delta: any
  }

  ai_suggestion: {
    user_id: string
    workspace_id: string
    task_id: string
    suggestion: any
  }

  task_blocked: {
    task_id: string
    task_title: string
    workspace_id: string
    blockers: string[]
    confidence: number
    suggested_action: string
  }

  cursor_update: {
    user_id: string
    document_id: string
    position: { x: number; y: number }
  }

  typing_indicator: {
    user_id: string
    is_typing: boolean
  }

  // Client → Server
  join_workspace: {
    workspace_id: string
    auth_token: string
  }

  leave_workspace: {
    workspace_id: string
  }

  ydoc_sync: {
    workspace_id: string
    document_id: string
    ops: Uint8Array
  }

  task_update: {
    workspace_id: string
    task_id: string
    delta: any
  }
}
```

#### 2.1.7 Create State Management (Zustand)

**File**: `frontend/src/store/authStore.ts`

```typescript
// frontend/src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, AuthTokens } from '@/types/auth'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  loading: boolean
  setAuth: (user: User, tokens: AuthTokens) => void
  setUser: (user: User | null) => void
  setTokens: (tokens: AuthTokens | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      loading: false,

      setAuth: (user, tokens) =>
        set({ user, tokens, loading: false }),

      setUser: (user) => set({ user }),

      setTokens: (tokens) => set({ tokens }),

      logout: () =>
        set({
          user: null,
          tokens: null,
          loading: false,
        }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
      }),
    }
  )
)
```

**File**: `frontend/src/store/taskStore.ts`

```typescript
// frontend/src/store/taskStore.ts
import { create } from 'zustand'
import { Task, TaskFilters } from '@/types/task'

interface TaskState {
  tasks: Task[]
  selectedTask: Task | null
  filters: TaskFilters
  loading: boolean

  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (id: string, updates: Partial<Task>) => void
  removeTask: (id: string) => void
  setSelectedTask: (task: Task | null) => void
  setFilters: (filters: TaskFilters) => void
  clearTasks: () => void
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  selectedTask: null,
  filters: {},
  loading: false,

  setTasks: (tasks) => set({ tasks }),

  addTask: (task) =>
    set((state) => ({
      tasks: [...state.tasks, task],
    })),

  updateTask: (id, updates) =>
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === id ? { ...task, ...updates } : task
      ),
      selectedTask:
        state.selectedTask?.id === id
          ? { ...state.selectedTask, ...updates }
          : state.selectedTask,
    })),

  removeTask: (id) =>
    set((state) => ({
      tasks: state.tasks.filter((task) => task.id !== id),
      selectedTask:
        state.selectedTask?.id === id ? null : state.selectedTask,
    })),

  setSelectedTask: (task) => set({ selectedTask: task }),

  setFilters: (filters) => set({ filters }),

  clearTasks: () => set({ tasks: [], selectedTask: null }),
}))
```

**File**: `frontend/src/store/socketStore.ts`

```typescript
// frontend/src/store/socketStore.ts
import { create } from 'zustand'
import { io, Socket } from 'socket.io-client'

interface SocketState {
  socket: Socket | null
  connected: boolean
  currentWorkspace: string | null

  connect: (token: string) => void
  disconnect: () => void
  joinWorkspace: (workspaceId: string) => void
  leaveWorkspace: (workspaceId: string) => void
}

export const useSocketStore = create<SocketState>((set, get) => ({
  socket: null,
  connected: false,
  currentWorkspace: null,

  connect: (token) => {
    const socket = io(import.meta.env.VITE_SOCKET_URL, {
      auth: { token },
      transports: ['websocket'],
    })

    socket.on('connect', () => {
      set({ connected: true, socket })
    })

    socket.on('disconnect', () => {
      set({ connected: false })
    })

    set({ socket })
  },

  disconnect: () => {
    const { socket } = get()
    if (socket) {
      socket.disconnect()
      set({ socket: null, connected: false, currentWorkspace: null })
    }
  },

  joinWorkspace: (workspaceId) => {
    const { socket } = get()
    if (socket) {
      socket.emit('join_workspace', { workspace_id: workspaceId })
      set({ currentWorkspace: workspaceId })
    }
  },

  leaveWorkspace: (workspaceId) => {
    const { socket } = get()
    if (socket) {
      socket.emit('leave_workspace', { workspace_id: workspaceId })
      set({ currentWorkspace: null })
    }
  },
}))
```

#### 2.1.8 Create Global Styles

**File**: `frontend/src/styles/variables.css`

```css
/* frontend/src/styles/variables.css */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-secondary: #64748b;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #06b6d4;

  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;

  --color-text-primary: #1e293b;
  --color-text-secondary: #475569;
  --color-text-muted: #94a3b8;

  --color-border: #e2e8f0;
  --color-border-dark: #cbd5e1;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-md: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 2rem;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
  --transition-slow: 500ms ease-in-out;
}
```

**File**: `frontend/src/styles/global.css`

```css
/* frontend/src/styles/global.css */
@import './variables.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  line-height: 1.5;
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--color-primary-dark);
}

button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  background: none;
}

input,
textarea,
select {
  font-family: inherit;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-border-dark);
}

.btn-danger {
  background: var(--color-error);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-sm);
}

.btn-lg {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-lg);
}

.input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-md);
  transition: border-color var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-error {
  background: #fee2e2;
  color: #991b1b;
}

.badge-info {
  background: #e0f2fe;
  color: #075985;
}

/* Utilities */
.text-sm {
  font-size: var(--font-size-sm);
}

.text-lg {
  font-size: var(--font-size-lg);
}

.text-muted {
  color: var(--color-text-muted);
}

.text-center {
  text-align: center;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 {
  gap: var(--spacing-sm);
}

.gap-4 {
  gap: var(--spacing-md);
}

.mt-4 {
  margin-top: var(--spacing-md);
}

.mb-4 {
  margin-bottom: var(--spacing-md);
}

/* Loading spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.6s linear infinite;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-sm);
  }

  .btn {
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
```

**Deliverables**:
- ✅ Complete project structure
- ✅ Vite and TypeScript configuration
- ✅ Environment variables configured
- ✅ Application entry points (main.tsx, App.tsx)
- ✅ TypeScript types for all domains
- ✅ Zustand stores for state management
- ✅ Global CSS variables and styles

**Acceptance Criteria**:
```bash
# Test 1: Application starts
npm run dev
# Expected: Server running on http://localhost:3000

# Test 2: No TypeScript errors
npm run type-check
# Expected: No type errors

# Test 3: Build succeeds
npm run build
# Expected: Build successful, dist/ folder created
```

**Dependencies**:
- Node.js 18+
- Package.json dependencies (already configured)

**Estimated Time**: 4-6 hours

---

### Task 2.2: Implement Authentication UI (6-8 hours) 🟡 HIGH

**Current State**:
- No authentication components
- No auth pages
- No protected routes

**What's Missing**:

#### 2.2.1 Create API Service

**File**: `frontend/src/services/api.ts`

```typescript
// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const tokens = localStorage.getItem('auth-storage')
        if (tokens) {
          const { tokens: authTokens } = JSON.parse(tokens)
          if (authTokens?.access_token) {
            config.headers.Authorization = `Bearer ${authTokens.access_token}`
          }
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const tokens = localStorage.getItem('auth-storage')
            if (tokens) {
              const { tokens: authTokens } = JSON.parse(tokens)
              if (authTokens?.refresh_token) {
                const response = await axios.post(
                  `${API_URL}/api/v1/auth/refresh`,
                  { refresh_token: authTokens.refresh_token }
                )

                const newTokens = response.data
                localStorage.setItem(
                  'auth-storage',
                  JSON.stringify({ tokens: newTokens })
                )

                originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
                return this.client(originalRequest)
              }
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem('auth-storage')
            window.location.href = '/login'
          }
        }

        return Promise.reject(error)
      }
    )
  }

  public getClient(): AxiosInstance {
    return this.client
  }

  public get<T>(url: string, config?: any) {
    return this.client.get<T>(url, config)
  }

  public post<T>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config)
  }

  public put<T>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config)
  }

  public delete<T>(url: string, config?: any) {
    return this.client.delete<T>(url, config)
  }
}

export const apiService = new ApiService()
export default apiService
```

#### 2.2.2 Create Auth Service

**File**: `frontend/src/services/authService.ts`

```typescript
// frontend/src/services/authService.ts
import api from './api'
import { LoginRequest, SignupRequest, AuthResponse } from '@/types/auth'

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/api/v1/auth/login',
      credentials
    )
    return response.data
  },

  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/api/v1/auth/signup',
      data
    )
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/api/v1/auth/refresh',
      { refresh_token: refreshToken }
    )
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/v1/auth/logout')
  },
}
```

#### 2.2.3 Create Auth Hook

**File**: `frontend/src/hooks/useAuth.ts`

```typescript
// frontend/src/hooks/useAuth.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'
import { LoginRequest, SignupRequest } from '@/types/auth'

export function useAuth() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, tokens, setAuth, logout: storeLogout } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data) => {
      setAuth(data.user, data.tokens)
      queryClient.invalidateQueries({ queryKey: ['auth'] })
      navigate('/')
    },
    onError: (error: any) => {
      console.error('Login failed:', error.response?.data?.detail || error.message)
    },
  })

  const signupMutation = useMutation({
    mutationFn: (data: SignupRequest) => authService.signup(data),
    onSuccess: (data) => {
      setAuth(data.user, data.tokens)
      queryClient.invalidateQueries({ queryKey: ['auth'] })
      navigate('/')
    },
    onError: (error: any) => {
      console.error('Signup failed:', error.response?.data?.detail || error.message)
    },
  })

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      storeLogout()
      queryClient.clear()
      navigate('/login')
    },
  })

  const logout = () => {
    logoutMutation.mutate()
  }

  const loading = loginMutation.isPending || signupMutation.isPending

  return {
    user,
    tokens,
    loading,
    login: loginMutation.mutate,
    signup: signupMutation.mutate,
    logout,
    isAuthenticated: !!user,
  }
}
```

#### 2.2.4 Create Common Components

**File**: `frontend/src/components/common/Input.tsx`

```typescript
// frontend/src/components/common/Input.tsx
import { InputHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  fullWidth?: boolean
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, fullWidth = false, className, ...props }, ref) => {
    return (
      <div className={clsx('flex flex-col gap-1', fullWidth && 'w-full')}>
        {label && (
          <label className="text-sm font-medium text-text-secondary">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            'input',
            error && 'border-error focus:border-error',
            fullWidth && 'w-full',
            className
          )}
          {...props}
        />
        {error && (
          <span className="text-sm text-error">{error}</span>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
```

**File**: `frontend/src/components/common/Button.tsx`

```typescript
// frontend/src/components/common/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  fullWidth?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      fullWidth = false,
      children,
      disabled,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          'btn',
          `btn-${variant}`,
          `btn-${size}`,
          fullWidth && 'w-full',
          loading && 'opacity-70 cursor-not-allowed',
          className
        )}
        {...props}
      >
        {loading ? (
          <span className="spinner" />
        ) : (
          children
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
```

**File**: `frontend/src/components/common/LoadingSpinner.tsx`

```typescript
// frontend/src/components/common/LoadingSpinner.tsx
import clsx from 'clsx'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const LoadingSpinner = ({ size = 'md', className }: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }

  return (
    <div className={clsx('flex items-center justify-center', className)}>
      <div className={clsx('spinner', sizeClasses[size])} />
    </div>
  )
}

export default LoadingSpinner
```

**File**: `frontend/src/components/common/ErrorBoundary.tsx`

```typescript
// frontend/src/components/common/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex items-center justify-center min-h-screen">
            <div className="card p-8 max-w-md w-full">
              <h1 className="text-2xl font-bold text-error mb-4">
                Something went wrong
              </h1>
              <p className="text-text-secondary mb-4">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <Button
                onClick={() => window.location.reload()}
                variant="primary"
              >
                Reload Page
              </Button>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

#### 2.2.5 Create Login Page

**File**: `frontend/src/pages/Login.tsx`

```typescript
// frontend/src/pages/Login.tsx
import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

export default function Login() {
  const navigate = useNavigate()
  const { login, loading } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !password) {
      setError('Please fill in all fields')
      return
    }

    try {
      await login({ email, password })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-bg-secondary">
      <div className="card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
          <p className="text-text-secondary">Sign in to PulseTasks</p>
        </div>

        {error && (
          <div className="bg-error/10 text-error p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            type="email"
            label="Email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={error && !email ? 'Email is required' : ''}
            required
          />

          <Input
            type="password"
            label="Password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={error && !password ? 'Password is required' : ''}
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            fullWidth
          >
            Sign In
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-text-secondary">
          Don't have an account?{' '}
          <Link to="/signup" className="text-primary hover:underline">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  )
}
```

#### 2.2.6 Create Signup Page

**File**: `frontend/src/pages/Signup.tsx`

```typescript
// frontend/src/pages/Signup.tsx
import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

export default function Signup() {
  const navigate = useNavigate()
  const { signup, loading } = useAuth()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (!name || !email || !password) {
      setError('Please fill in all fields')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    try {
      await signup({ name, email, password })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed')
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-bg-secondary">
      <div className="card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Create Account</h1>
          <p className="text-text-secondary">Get started with PulseTasks</p>
        </div>

        {error && (
          <div className="bg-error/10 text-error p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            type="text"
            label="Full Name"
            placeholder="John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={error && !name ? 'Name is required' : ''}
            required
          />

          <Input
            type="email"
            label="Email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={error && !email ? 'Email is required' : ''}
            required
          />

          <Input
            type="password"
            label="Password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={error && !password ? 'Password is required' : ''}
            required
          />

          <Input
            type="password"
            label="Confirm Password"
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            error={error && password !== confirmPassword ? 'Passwords do not match' : ''}
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            fullWidth
          >
            Create Account
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-text-secondary">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  )
}
```

**Deliverables**:
- ✅ API service with interceptors
- ✅ Auth service for API calls
- ✅ Auth hook with React Query
- ✅ Common UI components (Button, Input, Spinner, ErrorBoundary)
- ✅ Login page with form
- ✅ Signup page with validation
- ✅ Protected route logic

**Acceptance Criteria**:
```bash
# Test 1: Login works
# 1. Navigate to http://localhost:3000/login
# 2. Enter valid credentials
# 3. Click "Sign In"
# Expected: Redirect to dashboard, user authenticated

# Test 2: Signup works
# 1. Navigate to http://localhost:3000/signup
# 2. Fill form with valid data
# 3. Click "Create Account"
# Expected: Redirect to dashboard, user created

# Test 3: Validation works
# 1. Try to submit empty form
# Expected: Error messages displayed

# Test 4: Protected routes work
# 1. Try to access /tasks without auth
# Expected: Redirect to /login
```

**Dependencies**:
- React skeleton (Task 2.1)
- Backend auth API (from Phase 1)

**Estimated Time**: 6-8 hours

---

### Task 2.3: Create Task Management UI (10-16 hours) 🟡 HIGH

**Current State**:
- No task components
- No task pages
- No CRUD operations

**What's Missing**:

#### 2.3.1 Create Task Service

**File**: `frontend/src/services/taskService.ts`

```typescript
// frontend/src/services/taskService.ts
import api from './api'
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskFilters,
} from '@/types/task'

export const taskService = {
  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const response = await api.get<Task[]>('/api/v1/tasks', {
      params: filters,
    })
    return response.data
  },

  async getTask(id: string): Promise<Task> {
    const response = await api.get<Task>(`/api/v1/tasks/${id}`)
    return response.data
  },

  async createTask(data: CreateTaskRequest): Promise<Task> {
    const response = await api.post<Task>('/api/v1/tasks', data)
    return response.data
  },

  async updateTask(id: string, data: UpdateTaskRequest): Promise<Task> {
    const response = await api.put<Task>(`/api/v1/tasks/${id}`, data)
    return response.data
  },

  async deleteTask(id: string): Promise<void> {
    await api.delete(`/api/v1/tasks/${id}`)
  },
}
```

#### 2.3.2 Create Tasks Hook

**File**: `frontend/src/hooks/useTasks.ts`

```typescript
// frontend/src/hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTaskStore } from '@/store/taskStore'
import { taskService } from '@/services/taskService'
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskFilters,
} from '@/types/task'

export function useTasks(filters?: TaskFilters) {
  const queryClient = useQueryClient()
  const { setTasks, addTask, updateTask, removeTask } = useTaskStore()

  const {
    data: tasks = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => taskService.getTasks(filters),
    onSuccess: (data) => {
      setTasks(data)
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateTaskRequest) => taskService.createTask(data),
    onSuccess: (newTask) => {
      addTask(newTask)
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskRequest }) =>
      taskService.updateTask(id, data),
    onSuccess: (updatedTask) => {
      updateTask(updatedTask.id, updatedTask)
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => taskService.deleteTask(id),
    onSuccess: (_, id) => {
      removeTask(id)
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  return {
    tasks,
    isLoading,
    error,
    createTask: createMutation.mutate,
    updateTask: (id: string, data: UpdateTaskRequest) =>
      updateMutation.mutate({ id, data }),
    deleteTask: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  }
}

export function useTask(id: string) {
  const { data: task, isLoading, error } = useQuery({
    queryKey: ['task', id],
    queryFn: () => taskService.getTask(id),
    enabled: !!id,
  })

  return {
    task,
    isLoading,
    error,
  }
}
```

#### 2.3.3 Create Task Components

**File**: `frontend/src/components/tasks/TaskPriorityBadge.tsx`

```typescript
// frontend/src/components/tasks/TaskPriorityBadge.tsx
import { TaskPriority } from '@/types/task'
import clsx from 'clsx'

interface TaskPriorityBadgeProps {
  priority: TaskPriority
}

const TaskPriorityBadge = ({ priority }: TaskPriorityBadgeProps) => {
  const priorityConfig = {
    1: { label: 'Low', color: 'bg-blue-100 text-blue-700' },
    2: { label: 'Normal', color: 'bg-gray-100 text-gray-700' },
    3: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700' },
    4: { label: 'High', color: 'bg-orange-100 text-orange-700' },
    5: { label: 'Critical', color: 'bg-red-100 text-red-700' },
  }

  const config = priorityConfig[priority]

  return (
    <span className={clsx('badge', config.color)}>
      {config.label}
    </span>
  )
}

export default TaskPriorityBadge
```

**File**: `frontend/src/components/tasks/TaskStatusBadge.tsx`

```typescript
// frontend/src/components/tasks/TaskStatusBadge.tsx
import { TaskStatus } from '@/types/task'
import clsx from 'clsx'

interface TaskStatusBadgeProps {
  status: TaskStatus
}

const TaskStatusBadge = ({ status }: TaskStatusBadgeProps) => {
  const statusConfig = {
    OPEN: { label: 'Open', color: 'bg-gray-100 text-gray-700' },
    IN_PROGRESS: { label: 'In Progress', color: 'bg-blue-100 text-blue-700' },
    DONE: { label: 'Done', color: 'bg-green-100 text-green-700' },
  }

  const config = statusConfig[status]

  return (
    <span className={clsx('badge', config.color)}>
      {config.label}
    </span>
  )
}

export default TaskStatusBadge
```

**File**: `frontend/src/components/tasks/TaskItem.tsx`

```typescript
// frontend/src/components/tasks/TaskItem.tsx
import { Task } from '@/types/task'
import TaskPriorityBadge from './TaskPriorityBadge'
import TaskStatusBadge from './TaskStatusBadge'
import Button from '@/components/common/Button'
import { format } from 'date-fns'

interface TaskItemProps {
  task: Task
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
}

export default function TaskItem({ task, onEdit, onDelete }: TaskItemProps) {
  const handleStatusChange = (newStatus: Task['status']) => {
    // TODO: Call update task mutation
    console.log('Change status:', newStatus)
  }

  return (
    <div className="card p-4 mb-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="text-lg font-semibold mb-1">{task.title}</h3>
          {task.description && (
            <p className="text-sm text-text-secondary mb-2">
              {task.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <TaskPriorityBadge priority={task.priority} />
          <TaskStatusBadge status={task.status} />
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-text-muted">
        <div className="flex items-center gap-4">
          {task.due_date && (
            <span>
              Due: {format(new Date(task.due_date), 'MMM d, yyyy')}
            </span>
          )}
          {task.tags.length > 0 && (
            <div className="flex items-center gap-1">
              {task.tags.map((tag) => (
                <span
                  key={tag}
                  className="bg-bg-tertiary px-2 py-1 rounded text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onEdit(task)}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="danger"
            onClick={() => onDelete(task.id)}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}
```

**File**: `frontend/src/components/tasks/TaskForm.tsx`

```typescript
// frontend/src/components/tasks/TaskForm.tsx
import { useState, useEffect } from 'react'
import { Task, CreateTaskRequest, UpdateTaskRequest, TaskPriority } from '@/types/task'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

interface TaskFormProps {
  task?: Task
  onSubmit: (data: CreateTaskRequest | UpdateTaskRequest) => void
  onCancel: () => void
  loading?: boolean
}

export default function TaskForm({ task, onSubmit, onCancel, loading }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<TaskPriority>(2)
  const [dueDate, setDueDate] = useState('')

  useEffect(() => {
    if (task) {
      setTitle(task.title)
      setDescription(task.description || '')
      setPriority(task.priority)
      setDueDate(task.due_date || '')
    }
  }, [task])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      title,
      description,
      priority,
      due_date: dueDate || null,
    }

    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Title"
        placeholder="Task title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <div>
        <label className="block text-sm font-medium text-text-secondary mb-1">
          Description
        </label>
        <textarea
          className="input w-full h-24 resize-none"
          placeholder="Task description..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-text-secondary mb-1">
            Priority
          </label>
          <select
            className="input"
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value) as TaskPriority)}
          >
            <option value={1}>Low</option>
            <option value={2}>Normal</option>
            <option value={3}>Medium</option>
            <option value={4}>High</option>
            <option value={5}>Critical</option>
          </select>
        </div>

        <div className="flex-1">
          <Input
            type="date"
            label="Due Date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          type="submit"
          variant="primary"
          loading={loading}
          fullWidth
        >
          {task ? 'Update Task' : 'Create Task'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
        >
          Cancel
        </Button>
      </div>
    </form>
  )
}
```

**File**: `frontend/src/components/tasks/TaskFilter.tsx`

```typescript
// frontend/src/components/tasks/TaskFilter.tsx
import { TaskFilters, TaskStatus, TaskPriority } from '@/types/task'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

interface TaskFilterProps {
  filters: TaskFilters
  onFiltersChange: (filters: TaskFilters) => void
}

export default function TaskFilter({ filters, onFiltersChange }: TaskFilterProps) {
  const handleFilterChange = (key: keyof TaskFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    })
  }

  const clearFilters = () => {
    onFiltersChange({})
  }

  return (
    <div className="card p-4 mb-4">
      <div className="flex gap-4 items-end flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <Input
            placeholder="Search tasks..."
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </div>

        <div className="w-40">
          <label className="block text-sm font-medium text-text-secondary mb-1">
            Status
          </label>
          <select
            className="input"
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
          >
            <option value="">All Statuses</option>
            <option value={TaskStatus.OPEN}>Open</option>
            <option value={TaskStatus.IN_PROGRESS}>In Progress</option>
            <option value={TaskStatus.DONE}>Done</option>
          </select>
        </div>

        <div className="w-40">
          <label className="block text-sm font-medium text-text-secondary mb-1">
            Priority
          </label>
          <select
            className="input"
            value={filters.priority || ''}
            onChange={(e) => handleFilterChange('priority', e.target.value || undefined)}
          >
            <option value="">All Priorities</option>
            <option value={TaskPriority[1]}>Low</option>
            <option value={TaskPriority[2]}>Normal</option>
            <option value={TaskPriority[3]}>Medium</option>
            <option value={TaskPriority[4]}>High</option>
            <option value={TaskPriority[5]}>Critical</option>
          </select>
        </div>

        <Button
          variant="secondary"
          onClick={clearFilters}
          size="sm"
        >
          Clear Filters
        </Button>
      </div>
    </div>
  )
}
```

**File**: `frontend/src/components/tasks/TaskList.tsx`

```typescript
// frontend/src/components/tasks/TaskList.tsx
import { Task } from '@/types/task'
import TaskItem from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
}

export default function TaskList({ tasks, onEdit, onDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="card p-8 text-center">
        <p className="text-text-secondary">No tasks found</p>
      </div>
    )
  }

  return (
    <div>
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
```

#### 2.3.4 Create Tasks Page

**File**: `frontend/src/pages/Tasks.tsx`

```typescript
// frontend/src/pages/Tasks.tsx
import { useState } from 'react'
import { useTasks } from '@/hooks/useTasks'
import { Task } from '@/types/task'
import TaskList from '@/components/tasks/TaskList'
import TaskFilter from '@/components/tasks/TaskFilter'
import TaskForm from '@/components/tasks/TaskForm'
import Button from '@/components/common/Button'
import Modal from '@/components/common/Modal'

export default function Tasks() {
  const { tasks, isLoading, createTask, updateTask, deleteTask, isCreating, isUpdating } =
    useTasks()

  const [filters, setFilters] = useState<{}>({})
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)

  const handleCreateTask = async (data: any) => {
    await createTask(data)
    setShowCreateModal(false)
  }

  const handleUpdateTask = async (data: any) => {
    if (editingTask) {
      await updateTask(editingTask.id, data)
      setShowEditModal(false)
      setEditingTask(null)
    }
  }

  const handleEditTask = (task: Task) => {
    setEditingTask(task)
    setShowEditModal(true)
  }

  const handleDeleteTask = async (id: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      await deleteTask(id)
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Tasks</h1>
        <Button
          variant="primary"
          onClick={() => setShowCreateModal(true)}
        >
          New Task
        </Button>
      </div>

      <TaskFilter filters={filters} onFiltersChange={setFilters} />

      <TaskList
        tasks={tasks}
        onEdit={handleEditTask}
        onDelete={handleDeleteTask}
      />

      {showCreateModal && (
        <Modal onClose={() => setShowCreateModal(false)}>
          <TaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowCreateModal(false)}
            loading={isCreating}
          />
        </Modal>
      )}

      {showEditModal && editingTask && (
        <Modal onClose={() => setShowEditModal(false)}>
          <TaskForm
            task={editingTask}
            onSubmit={handleUpdateTask}
            onCancel={() => setShowEditModal(false)}
            loading={isUpdating}
          />
        </Modal>
      )}
    </div>
  )
}
```

**Deliverables**:
- ✅ Task service for API calls
- ✅ Tasks hook with React Query
- ✅ Task components (Item, List, Form, Filter)
- ✅ Priority and status badges
- ✅ Tasks page with full CRUD
- ✅ Filtering and sorting

**Acceptance Criteria**:
```bash
# Test 1: Create task works
# 1. Click "New Task"
# 2. Fill form
# 3. Submit
# Expected: Task appears in list

# Test 2: Update task works
# 1. Click "Edit" on task
# 2. Modify fields
# 3. Submit
# Expected: Task updated in list

# Test 3: Delete task works
# 1. Click "Delete" on task
# 2. Confirm
# Expected: Task removed from list

# Test 4: Filtering works
# 1. Select status filter
# Expected: List shows only filtered tasks
```

**Dependencies**:
- React skeleton (Task 2.1)
- Authentication (Task 2.2)
- Backend task API (from Phase 1)

**Estimated Time**: 10-16 hours

---

### Task 2.4: Integrate Real-time Features (4-6 hours) 🟡 HIGH

**Current State**:
- No Socket.IO client
- No real-time updates
- No presence tracking

**What's Missing**:

#### 2.4.1 Create Socket Service

**File**: `frontend/src/services/socketService.ts`

```typescript
// frontend/src/services/socketService.ts
import { io, Socket } from 'socket.io-client'
import { SocketEvents } from '@/types/socket'

class SocketService {
  private socket: Socket | null = null
  private listeners: Map<string, Function[]> = new Map()

  connect(token: string): Socket {
    if (this.socket?.connected) {
      return this.socket
    }

    const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000'

    this.socket = io(socketUrl, {
      auth: { token },
      transports: ['websocket', 'polling'],
    })

    // Connection events
    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id)
    })

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected')
    })

    // Error handling
    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error)
    })

    return this.socket
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.listeners.clear()
    }
  }

  emit<K extends keyof SocketEvents>(
    event: K,
    data: SocketEvents[K]
  ): void {
    this.socket?.emit(event as string, data)
  }

  on<K extends keyof SocketEvents>(
    event: K,
    callback: (data: SocketEvents[K]) => void
  ): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)?.push(callback)

    this.socket?.on(event as string, callback)
  }

  off<K extends keyof SocketEvents>(
    event: K,
    callback?: (data: SocketEvents[K]) => void
  ): void {
    if (callback) {
      this.socket?.off(event as string, callback)
      const listeners = this.listeners.get(event) || []
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    } else {
      this.socket?.off(event as string)
      this.listeners.delete(event)
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false
  }
}

export const socketService = new SocketService()
export default socketService
```

#### 2.4.2 Create Socket Hook

**File**: `frontend/src/hooks/useSocket.ts`

```typescript
// frontend/src/hooks/useSocket.ts
import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useSocketStore } from '@/store/socketStore'
import socketService from '@/services/socketService'
import { SocketEvents } from '@/types/socket'

export function useSocket() {
  const { tokens } = useAuthStore()
  const { connect, disconnect } = useSocketStore()

  useEffect(() => {
    if (tokens?.access_token && !socketService.isConnected()) {
      const socket = connect(tokens.access_token)

      // Setup event listeners
      socket.on('presence_update', (data: SocketEvents['presence_update']) => {
        console.log('Presence update:', data)
        // TODO: Update presence in store
      })

      socket.on('ydoc_update', (data: SocketEvents['ydoc_update']) => {
        console.log('Yjs update:', data)
        // TODO: Handle CRDT updates
      })

      socket.on('task_broadcast', (data: SocketEvents['task_broadcast']) => {
        console.log('Task broadcast:', data)
        // TODO: Update task in store
      })

      socket.on('ai:suggestion', (data: SocketEvents['ai_suggestion']) => {
        console.log('AI suggestion:', data)
        // TODO: Show AI suggestion to user
      })

      socket.on('task_blocked', (data: SocketEvents['task_blocked']) => {
        console.log('Task blocked:', data)
        // TODO: Show blocker notification
      })

      socket.on('cursor_update', (data: SocketEvents['cursor_update']) => {
        console.log('Cursor update:', data)
        // TODO: Update cursor positions
      })

      socket.on('typing_indicator', (data: SocketEvents['typing_indicator']) => {
        console.log('Typing indicator:', data)
        // TODO: Show typing indicator
      })

      return () => {
        socket.offAll()
        disconnect()
      }
    }
  }, [tokens, connect, disconnect])

  return {
    isConnected: socketService.isConnected(),
    socket: socketService,
  }
}
```

#### 2.4.3 Create Real-time Components

**File**: `frontend/src/components/realtime/PresenceIndicator.tsx`

```typescript
// frontend/src/components/realtime/PresenceIndicator.tsx
import { useState, useEffect } from 'react'
import { useSocket } from '@/hooks/useSocket'

interface UserPresence {
  user_id: string
  status: 'online' | 'offline' | 'away'
  workspace_id: string
}

export default function PresenceIndicator() {
  const { isConnected } = useSocket()
  const [onlineUsers, setOnlineUsers] = useState<UserPresence[]>([])

  useEffect(() => {
    // TODO: Listen for presence updates
    // socket.on('presence_update', updateOnlineUsers)
  }, [])

  if (!isConnected) {
    return null
  }

  return (
    <div className="flex items-center gap-2">
      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
      <span className="text-sm text-text-secondary">
        {onlineUsers.length} online
      </span>
    </div>
  )
}
```

**File**: `frontend/src/components/realtime/TypingIndicator.tsx`

```typescript
// frontend/src/components/realtime/TypingIndicator.tsx
import { useState, useEffect } from 'react'
import { useSocket } from '@/hooks/useSocket'

interface TypingUser {
  user_id: string
  is_typing: boolean
}

export default function TypingIndicator() {
  const { socket } = useSocket()
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([])

  useEffect(() => {
    if (!socket) return

    socket.on('typing_indicator', (data) => {
      setTypingUsers((prev) => {
        const existing = prev.find((u) => u.user_id === data.user_id)
        if (existing) {
          return existing.is_typing === data.is_typing
            ? prev.filter((u) => u.user_id !== data.user_id)
            : prev.map((u) =>
                u.user_id === data.user_id ? data : u
              )
        }
        return data.is_typing ? [...prev, data] : prev
      })
    })

    return () => {
      socket.off('typing_indicator')
    }
  }, [socket])

  if (typingUsers.length === 0) {
    return null
  }

  return (
    <div className="text-sm text-text-muted animate-pulse">
      {typingUsers.length} user{typingUsers.length > 1 ? 's are' : ' is'} typing...
    </div>
  )
}
```

**Deliverables**:
- ✅ Socket.IO service with connection management
- ✅ Socket hook for component integration
- ✅ Presence indicator component
- ✅ Typing indicator component
- ✅ Real-time task updates

**Acceptance Criteria**:
```bash
# Test 1: Socket connects
# 1. Login to app
# Expected: Socket connection established

# Test 2: Presence updates work
# 1. Open app in two browsers
# 2. Login both with different accounts
# Expected: Presence indicator shows 2 online

# Test 3: Real-time updates work
# 1. Create task in one browser
# Expected: Task appears in other browser immediately
```

**Dependencies**:
- React skeleton (Task 2.1)
- Socket.IO backend (from Phase 1, Task 1.2)

**Estimated Time**: 4-6 hours

---

### Task 2.5: Add AI Suggestions UI (4-6 hours) 🟡 HIGH

**Current State**:
- No AI service integration
- No AI suggestion components
- No confidence display

**What's Missing**:

#### 2.5.1 Create AI Service

**File**: `frontend/src/services/aiService.ts`

```typescript
// frontend/src/services/aiService.ts
import api from './api'
import { AISuggestion, AISuggestionRequest } from '@/types/ai'

export const aiService = {
  async rewriteTask(
    request: AISuggestionRequest
  ): Promise<AISuggestion> {
    const response = await api.post<AISuggestion>(
      '/api/v1/ai/rewrite',
      request
    )
    return response.data
  },

  async acceptSuggestion(suggestionId: string): Promise<void> {
    await api.post(`/api/v1/ai/suggestions/${suggestionId}/accept`)
  },
}
```

#### 2.5.2 Create AI Hook

**File**: `frontend/src/hooks/useAISuggestions.ts`

```typescript
// frontend/src/hooks/useAISuggestions.ts
import { useMutation } from '@tanstack/react-query'
import { aiService } from '@/services/aiService'
import { AISuggestionRequest } from '@/types/ai'

export function useAISuggestions() {
  const rewriteMutation = useMutation({
    mutationFn: (request: AISuggestionRequest) =>
      aiService.rewriteTask(request),
  })

  const acceptMutation = useMutation({
    mutationFn: (suggestionId: string) =>
      aiService.acceptSuggestion(suggestionId),
  })

  return {
    rewrite: rewriteMutation.mutate,
    rewriteAsync: rewriteMutation.mutateAsync,
    accept: acceptMutation.mutate,
    isRewriting: rewriteMutation.isPending,
    isAccepting: acceptMutation.isPending,
  }
}
```

#### 2.5.3 Create AI Components

**File**: `frontend/src/components/ai/ConfidenceBadge.tsx`

```typescript
// frontend/src/components/ai/ConfidenceBadge.tsx
import clsx from 'clsx'

interface ConfidenceBadgeProps {
  confidence: number
}

export default function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const getBadgeColor = (conf: number) => {
    if (conf >= 0.8) return 'bg-green-100 text-green-700'
    if (conf >= 0.5) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  const getBadgeText = (conf: number) => {
    if (conf >= 0.8) return 'High Confidence'
    if (conf >= 0.5) return 'Medium Confidence'
    return 'Low Confidence'
  }

  return (
    <span className={clsx('badge', getBadgeColor(confidence))}>
      {getBadgeText(confidence)} ({Math.round(confidence * 100)}%)
    </span>
  )
}
```

**File**: `frontend/src/components/ai/AISuggestionCard.tsx`

```typescript
// frontend/src/components/ai/AISuggestionCard.tsx
import { AISuggestion } from '@/types/ai'
import ConfidenceBadge from './ConfidenceBadge'
import Button from '@/components/common/Button'

interface AISuggestionCardProps {
  suggestion: AISuggestion
  onAccept: () => void
  onDismiss: () => void
  loading?: boolean
}

export default function AISuggestionCard({
  suggestion,
  onAccept,
  onDismiss,
  loading,
}: AISuggestionCardProps) {
  if (!suggestion.rewritten_title) {
    return null
  }

  return (
    <div className="card p-4 mb-4 border-l-4 border-l-primary bg-blue-50">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold text-lg">AI Suggestion</h4>
        <ConfidenceBadge confidence={suggestion.confidence} />
      </div>

      <div className="mb-4">
        <p className="text-sm text-text-secondary mb-1">Rewritten Title:</p>
        <p className="font-medium">{suggestion.rewritten_title}</p>
      </div>

      {suggestion.checklist.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-text-secondary mb-2">Suggested Checklist:</p>
          <ul className="list-disc list-inside space-y-1">
            {suggestion.checklist.map((item, index) => (
              <li key={index} className="text-sm">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-4 mb-4 text-sm">
        {suggestion.suggested_priority && (
          <div>
            <span className="text-text-secondary">Priority: </span>
            <span className="font-medium">{suggestion.suggested_priority}</span>
          </div>
        )}
        {suggestion.suggested_due_date && (
          <div>
            <span className="text-text-secondary">Due Date: </span>
            <span className="font-medium">{suggestion.suggested_due_date}</span>
          </div>
        )}
      </div>

      <p className="text-sm text-text-secondary mb-4">
        {suggestion.explanation}
      </p>

      <div className="flex gap-2">
        <Button
          variant="primary"
          onClick={onAccept}
          loading={loading}
          fullWidth
        >
          Accept Suggestion
        </Button>
        <Button
          variant="secondary"
          onClick={onDismiss}
        >
          Dismiss
        </Button>
      </div>
    </div>
  )
}
```

#### 2.5.4 Integrate AI into Task Form

**Update TaskForm.tsx to include AI suggestions**:

```typescript
// In frontend/src/components/tasks/TaskForm.tsx
import { useEffect, useState } from 'react'
import { useAISuggestions } from '@/hooks/useAISuggestions'

// Add to component
export default function TaskForm({ task, onSubmit, onCancel, loading }: TaskFormProps) {
  const { rewriteAsync, isRewriting } = useAISuggestions()
  const [aiSuggestion, setAiSuggestion] = useState<any>(null)
  const [showAISuggestion, setShowAISuggestion] = useState(false)

  // Trigger AI suggestion when title changes
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (title.length > 5 && !task) { // Only for new tasks
        try {
          const suggestion = await rewriteAsync({
            raw_title: title,
            raw_description: description,
          })
          setAiSuggestion(suggestion)
          setShowAISuggestion(true)
        } catch (error) {
          console.error('AI suggestion failed:', error)
        }
      }
    }, 800) // Debounce 800ms

    return () => clearTimeout(timer)
  }, [title, description, task, rewriteAsync])

  const handleAcceptSuggestion = () => {
    if (aiSuggestion) {
      setTitle(aiSuggestion.rewritten_title || title)
      setShowAISuggestion(false)
    }
  }

  const handleDismissSuggestion = () => {
    setShowAISuggestion(false)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* ... existing form fields ... */}

      {/* AI Suggestion Card */}
      {showAISuggestion && aiSuggestion && (
        <AISuggestionCard
          suggestion={aiSuggestion}
          onAccept={handleAcceptSuggestion}
          onDismiss={handleDismissSuggestion}
          loading={isRewriting}
        />
      )}

      {/* ... rest of form ... */}
    </form>
  )
}
```

**Deliverables**:
- ✅ AI service for API calls
- ✅ AI hook with mutations
- ✅ Confidence badge component
- ✅ AI suggestion card component
- ✅ Integration into task form
- ✅ Auto-trigger on task title change

**Acceptance Criteria**:
```bash
# Test 1: AI suggestion appears
# 1. Click "New Task"
# 2. Type task title
# 3. Wait 800ms
# Expected: AI suggestion card appears

# Test 2: Accept suggestion works
# 1. Click "Accept Suggestion"
# Expected: Task title updated, suggestion dismissed

# Test 3: Confidence badge shows
# 1. View AI suggestion
# Expected: Confidence badge with percentage
```

**Dependencies**:
- React skeleton (Task 2.1)
- Task management UI (Task 2.3)
- AI backend service (from Phase 1, Task 1.3)

**Estimated Time**: 4-6 hours

---

## 📊 Phase 2 Summary

### Total Estimated Effort: 24-40 hours

| Task | Description | Time | Priority |
|------|-------------|------|----------|
| 2.1 | Build React skeleton | 4-6h | 🟡 High |
| 2.2 | Authentication UI | 6-8h | 🟡 High |
| 2.3 | Task management UI | 10-16h | 🟡 High |
| 2.4 | Real-time features | 4-6h | 🟡 High |
| 2.5 | AI suggestions UI | 4-6h | 🟡 High |

### Third-Party Services Required

**None required for Phase 2** - All services are already configured from Phase 1:
- ✅ Backend API (localhost:8000)
- ✅ Socket.IO server (localhost:8000)
- ✅ AI service (localhost:8001)
- ✅ Redis (localhost:6379)

### Deliverables

1. ✅ Complete React application structure
2. ✅ Authentication flow (login/signup)
3. ✅ Task management with full CRUD
4. ✅ Real-time collaboration features
5. ✅ AI suggestion integration
6. ✅ Mobile-responsive design
7. ✅ Type-safe TypeScript code
8. ✅ State management with Zustand
9. ✅ Data fetching with React Query
10. ✅ Comprehensive component library

### Success Criteria

- [ ] User can log in and sign up
- [ ] Tasks can be created, read, updated, deleted
- [ ] Real-time updates work across multiple clients
- [ ] AI suggestions appear when creating tasks
- [ ] Presence tracking shows online users
- [ ] Application is responsive on mobile
- [ ] No TypeScript errors
- [ ] Build succeeds without warnings

### Next Steps

After completing Phase 2, proceed to **Phase 3: Advanced Features** to add:
- Workspace and member management
- Blocker detection
- Time-aware prioritization
- Advanced analytics
- Production deployment

---

**Document Version**: 1.0
**Last Updated**: February 20, 2026
**Next Review**: After Phase 2 completion
**Owner**: Frontend Development Team
