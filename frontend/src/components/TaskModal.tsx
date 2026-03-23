import React, { useState, useEffect } from 'react'
import { useRealtime } from './realtime/RealtimeContext'
import { aiService } from '../services/aiService'

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (task: { title: string; priority: number; description?: string; checklist?: string[] }) => void;
}

export default function TaskModal({ isOpen, onClose, onCreate }: TaskModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState(2)
  const [checklist, setChecklist] = useState<string[]>([])
  const [isOptimizing, setIsOptimizing] = useState(false)
  const { setTyping } = useRealtime();

  useEffect(() => {
    if (isOpen && title.length > 0) {
      setTyping(true);
      const timeout = setTimeout(() => setTyping(false), 2000);
      return () => {
        clearTimeout(timeout);
        setTyping(false);
      };
    } else {
      setTyping(false);
    }
  }, [title, isOpen]);

  const handleAiOptimize = async () => {
    if (!title.trim()) return;
    setIsOptimizing(true);
    try {
      const suggestion = await aiService.getTaskSuggestion(title, description);
      if (suggestion) {
        setTitle(suggestion.rewritten_title);
        setChecklist(suggestion.checklist || []);
        setPriority(suggestion.suggested_priority || 2);
      }
    } catch (err) {
      console.error('AI Optimization failed:', err);
    } finally {
      setIsOptimizing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="modal-title"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)'
      }}
    >
      <div className="glass" style={{
        width: '500px',
        padding: '2rem',
        borderRadius: 'var(--radius-base)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 id="modal-title" style={{ margin: 0, fontSize: '1.25rem' }}>Create New Task</h2>
          <button 
            disabled={isOptimizing || !title.trim()}
            onClick={handleAiOptimize}
            style={{ 
              fontSize: '0.75rem', 
              padding: '0.4rem 0.8rem', 
              borderRadius: '20px', 
              backgroundColor: 'rgba(168, 85, 247, 0.1)', 
              color: '#a855f7',
              border: '1px solid rgba(168, 85, 247, 0.2)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <span>✨</span> {isOptimizing ? 'Optimizing...' : 'AI Optimize'}
          </button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Title</label>
          <input 
            autoFocus
            type="text" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Refactor API"
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '0.75rem',
              color: 'white',
              outline: 'none'
            }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Description (Optional)</label>
          <textarea 
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Details..."
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '0.75rem',
              color: 'white',
              outline: 'none',
              minHeight: '80px',
              resize: 'none'
            }}
          />
        </div>

        {checklist.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>AI Suggested Checklist</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {checklist.map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                  <input type="checkbox" defaultChecked />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Priority</label>
            <select 
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                padding: '0.75rem',
                color: 'white',
                outline: 'none'
              }}
            >
              <option value={1}>Low</option>
              <option value={2}>Medium</option>
              <option value={3}>High</option>
              <option value={4}>Critical</option>
              <option value={5}>Urgent</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <button 
            onClick={onClose}
            style={{
              flex: 1,
              padding: '0.75rem',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              background: 'transparent',
              color: 'white',
              cursor: 'pointer'
            }}
          >Cancel</button>
          <button 
            onClick={() => {
              if (title.trim()) {
                onCreate({ title, priority, description, checklist })
                setTitle('')
                setDescription('')
                setChecklist([])
                onClose()
              }
            }}
            style={{
              flex: 1,
              padding: '0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: 'var(--color-primary)',
              color: 'white',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >Create Task</button>
        </div>
      </div>
    </div>
  )
}
// ...rest of modal...
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(4px)'
    }}>
      <div className="glass" style={{
        width: '400px',
        padding: '2rem',
        borderRadius: 'var(--radius-base)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Create New Task</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Task Title</label>
          <input 
            autoFocus
            type="text" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '0.75rem',
              color: 'white',
              outline: 'none'
            }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Priority</label>
          <select 
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              padding: '0.75rem',
              color: 'white',
              outline: 'none'
            }}
          >
            <option value={1}>Low</option>
            <option value={2}>Medium</option>
            <option value={3}>High</option>
            <option value={4}>Critical</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <button 
            onClick={onClose}
            style={{
              flex: 1,
              padding: '0.75rem',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              background: 'transparent',
              color: 'white',
              cursor: 'pointer'
            }}
          >Cancel</button>
          <button 
            onClick={() => {
              if (title.trim()) {
                onCreate({ title, priority })
                setTitle('')
                onClose()
              }
            }}
            style={{
              flex: 1,
              padding: '0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: 'var(--color-primary)',
              color: 'white',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >Create Task</button>
        </div>
      </div>
    </div>
  )
}
