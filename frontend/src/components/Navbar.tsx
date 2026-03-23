import PresenceDots from './realtime/PresenceDots'

export default function Navbar() {
  const [isAiOnline, setIsAiOnline] = useState(false)

  // ... existing checkAi logic ...

  return (
    <header className="glass" role="banner" style={{
      height: '64px',
      position: 'fixed',
      top: 0,
      left: '260px',
      right: 0,
      padding: '0 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      zIndex: 90
    }}>
      <nav aria-label="Breadcrumb" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>Projects / PulseTask</div>
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <PresenceDots />
        
        <div 
          role="status"
// ...rest of navbar...
          aria-label={`AI Agent is ${isAiOnline ? 'online' : 'offline'}`}
          style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: isAiOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
            color: isAiOnline ? 'var(--color-accent)' : '#ef4444',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <div aria-hidden="true" style={{ 
            width: '6px', 
            height: '6px', 
            borderRadius: '50%', 
            backgroundColor: isAiOnline ? 'var(--color-accent)' : '#ef4444' 
          }}></div>
          {isAiOnline ? 'AI Agent Online' : 'AI Agent Offline'}
        </div>
        
        <button 
          aria-label="View Notifications"
          style={{ position: 'relative', cursor: 'pointer', background: 'transparent', border: 'none' }}
        >
          <span aria-hidden="true" style={{ fontSize: '1.25rem' }}>🔔</span>
          <div aria-hidden="true" style={{ 
            position: 'absolute', 
            top: 2, 
            right: 2, 
            width: '8px', 
            height: '8px', 
            backgroundColor: '#ef4444', 
            borderRadius: '50%',
            border: '2px solid var(--color-surface)'
          }}></div>
        </button>
      </div>
    </header>
  )
}
