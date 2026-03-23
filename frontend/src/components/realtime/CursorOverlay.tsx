import React from 'react';
import { useRealtime } from './RealtimeContext';

const CursorOverlay: React.FC = () => {
  const { onlineUsers } = useRealtime();
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <div className="cursor-overlay" style={{ pointerEvents: 'none', position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 9999 }}>
      {Object.values(onlineUsers).map((user) => {
        if (user.id === currentUser.id || !user.cursor) return null;

        return (
          <div 
            key={user.id}
            style={{ 
              position: 'absolute', 
              left: user.cursor.x, 
              top: user.cursor.y,
              transition: 'all 0.1s linear',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start'
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="var(--color-primary)">
              <path d="M7 2l12 11.2l-5.8 0.8l4 6.1l-2.1 1.4-4-6.1l-4.1 4.3z" stroke="white" strokeWidth="1" />
            </svg>
            <div style={{ 
              backgroundColor: 'var(--color-primary)', 
              color: 'white', 
              padding: '2px 6px', 
              borderRadius: '4px', 
              fontSize: '10px', 
              fontWeight: 600,
              whiteSpace: 'nowrap',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}>
              {user.name}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CursorOverlay;
