import { NavLink, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

export default function Sidebar() {
  const navigate = useNavigate();
  const [user, setUser] = useState<{name: string} | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const menuItems = [
    { icon: '📊', label: 'Dashboard', path: '/' },
    { icon: '🚀', label: 'Projects', path: '/projects' },
    { icon: '👥', label: 'Team', path: '/team' },
    { icon: '⚙️', label: 'Settings', path: '/settings' },
  ]

  return (
    <aside className="glass" role="complementary" aria-label="Main Sidebar" style={{
      width: '260px',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      padding: '2rem 1.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem',
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.5rem' }}>
        <div aria-hidden="true" style={{
          width: '32px',
          height: '32px',
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
          borderRadius: '8px'
        }}></div>
        <span style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em' }}>PulseTask</span>
      </div>

      <nav aria-label="Main Navigation" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {menuItems.map((item, i) => (
          <NavLink 
            key={i} 
            to={item.path}
            aria-label={item.label}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-base)',
              textDecoration: 'none',
              backgroundColor: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
              color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              transition: 'all 0.2s ease',
              fontWeight: isActive ? 600 : 400
            })}
          >
            <span aria-hidden="true" style={{ fontSize: '1.25rem' }}>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="user-profile" style={{ padding: '1rem', borderRadius: 'var(--radius-base)', backgroundColor: 'rgba(255,255,255,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div aria-hidden="true" style={{ width: '32px', height: '32px', backgroundColor: 'var(--color-primary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 600 }}>
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '0.875rem', fontWeight: 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{user?.name || 'User Name'}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Pro Plan</div>
            </div>
          </div>
        </div>
        
        <button 
          onClick={handleLogout}
          className="btn-outline"
          aria-label="Logout"
          style={{ width: '100%', padding: '0.5rem', fontSize: '0.875rem' }}
        >
          Logout
        </button>
      </div>
    </aside>
  )
}
