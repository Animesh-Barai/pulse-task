import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import Projects from './components/Projects'
import Team from './components/Team'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import TaskModal from './components/TaskModal'

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [stats, setStats] = useState([
    { label: 'Active Tasks', value: '0', trend: 'Live', color: 'var(--color-primary)' },
    { label: 'Team Velocity', value: '100%', trend: '+0%', color: 'var(--color-accent)' },
    { label: 'AI Assistance', value: 'Active', trend: 'Live', color: '#a855f7' },
  ])

  const fetchData = async () => {
    try {
      const fetchedTasks = await taskService.getTasks()
      setTasks(fetchedTasks || [])
      setStats(prev => [
        { ...prev[0], value: String(fetchedTasks?.filter(t => t.status !== 'DONE').length || 0) },
        prev[1],
        prev[2]
      ])
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
      // If 401, clear token and redirect
      if ((err as any).response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
  }

  useEffect(() => {
    fetchData()
    const socket = socketService.connect()
    
    // Auth-aware socket connection would go here
    
    socket?.on('pulse_update', fetchData)
    socket?.on('task_created', fetchData)
    socket?.on('task_deleted', fetchData)
    socket?.on('task_updated', fetchData)

    return () => {
      socketService.disconnect()
    }
  }, [])

  const handleCreateTask = async (data: { title: string; priority: number; description?: string; checklist?: string[] }) => {
    try {
      await taskService.createTask({
        title: data.title,
        priority: data.priority,
        description: data.description,
        checklist: data.checklist,
        status: 'OPEN'
      })
      fetchData()
    } catch (err) {
      alert('Failed to create task.')
    }
  }

  const handleDeleteTask = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await taskService.deleteTask(id)
        fetchData()
      } catch (err) {
        alert('Failed to delete task')
      }
    }
  }

  const handleToggleComplete = async (task: Task) => {
    try {
      const newStatus = task.status === 'DONE' ? 'OPEN' : 'DONE'
      await taskService.updateTask(task.id, { status: newStatus })
      fetchData()
    } catch (err) {
      alert('Failed to update task')
    }
  }

  const getPriorityLabel = (p: number) => {
    const labels: Record<number, string> = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical', 5: 'Urgent' }
    return labels[p] || 'Medium'
  }

  return (
    <main id="main-content" style={{ padding: '84px 2rem 2rem 280px', minHeight: '100vh' }}>
      <TaskModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onCreate={handleCreateTask} 
      />

      <section aria-labelledby="dashboard-title" style={{ marginBottom: '2rem' }}>
        <h1 id="dashboard-title" style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Dashboard Overview</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Welcome back! Here's what's happening in your projects today.</p>
      </section>

      <div role="region" aria-label="Quick Stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        {stats.map((stat, i) => (
          <article key={i} className="glass" style={{ padding: '1.5rem', borderRadius: 'var(--radius-base)' }}>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{stat.label}</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: stat.color }}>{stat.value}</div>
              <div style={{ fontSize: '0.75rem', color: '#a1a1aa' }}>{stat.trend}</div>
            </div>
          </article>
        ))}
      </div>

      <section className="glass" aria-labelledby="task-list-title" style={{ padding: '2rem', borderRadius: 'var(--radius-base)', minHeight: '400px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 id="task-list-title" style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recent Tasks</h2>
          <button 
            onClick={() => setIsModalOpen(true)}
            aria-label="Create New Task"
            className="btn-primary"
            style={{ 
              padding: '0.5rem 1rem', 
              borderRadius: '6px', 
              fontWeight: 500,
              cursor: 'pointer'
            }}
          >New Task</button>
        </div>
        
        <div role="list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {tasks.length > 0 ? tasks.map((task, i) => (
            <div role="listitem" key={i} style={{ 
              padding: '1rem', 
              borderBottom: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              opacity: task.status === 'DONE' ? 0.6 : 1
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <input 
                  type="checkbox" 
                  checked={task.status === 'DONE'}
                  onChange={() => handleToggleComplete(task)}
                  aria-label={`Mark task "${task.title}" as complete`}
                  style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                />
                <div>
                  <div style={{ 
                    fontWeight: 500, 
                    marginBottom: '0.25rem',
                    textDecoration: task.status === 'DONE' ? 'line-through' : 'none'
                  }}>{task.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    {task.status.replace('_', ' ')} • {getPriorityLabel(task.priority)}
                  </div>
                </div>
              </div>
              <button 
                onClick={() => handleDeleteTask(task.id)}
                aria-label={`Delete task "${task.title}"`}
                style={{ 
                  background: 'transparent', 
                  border: 'none', 
                  color: '#ef4444', 
                  cursor: 'pointer',
                  fontSize: '1.1rem' 
                }}
              >🗑️</button>
            </div>
          )) : (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-secondary)' }}>
              <div aria-hidden="true" style={{ fontSize: '3rem', marginBottom: '1rem' }}>📝</div>
              No tasks found. Click "New Task" to get started!
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <main id="main-content" style={{ padding: '84px 2rem 2rem 280px', minHeight: '100vh' }}>
      <section className="glass" style={{ padding: '4rem', borderRadius: 'var(--radius-base)', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{title}</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>This module is currently being optimized and will be available shortly.</p>
        <Link to="/" style={{ color: 'var(--color-primary)', marginTop: '2rem', display: 'inline-block' }}>Back to Dashboard</Link>
      </section>
    </main>
  )
}

import { RealtimeProvider, useRealtime } from './components/realtime/RealtimeContext'
import CursorOverlay from './components/realtime/CursorOverlay'

// ... existing code ...

const AppLayout = () => {
  const { updateCursor } = useRealtime();

  const handleMouseMove = (e: React.MouseEvent) => {
    updateCursor(e.clientX, e.clientY);
  };

  return (
    <div style={{ display: 'flex' }} onMouseMove={handleMouseMove}>
      <CursorOverlay />
      <Sidebar />
      <div style={{ flex: 1 }}>
        <Navbar />
        <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/team" element={<Team />} />
        <Route path="/settings" element={<PlaceholderPage title="System Settings" />} />
      </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <RealtimeProvider>
              <AppLayout />
            </RealtimeProvider>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}
