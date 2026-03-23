import React from 'react';
import { useRealtime } from './RealtimeContext';

const PresenceDots: React.FC = () => {
  const { onlineUsers } = useRealtime();
  const usersArray = Object.values(onlineUsers);

  if (usersArray.length === 0) return null;

  return (
    <div className="presence-dots" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginRight: '1rem' }}>
      <div style={{ display: 'flex', marginLeft: '0.5rem' }}>
        {usersArray.map((user, i) => (
          <div 
            key={user.id} 
            title={`${user.name} ${user.isTyping ? '(Typing...)' : ''}`}
            style={{ 
              width: '28px', 
              height: '28px', 
              borderRadius: '50%', 
              backgroundColor: 'var(--color-primary)', 
              border: '2px solid var(--color-surface)',
              marginLeft: i === 0 ? 0 : '-10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'white',
              position: 'relative',
              zIndex: usersArray.length - i,
              boxShadow: user.isTyping ? '0 0 8px var(--color-accent)' : 'none',
              transition: 'all 0.3s ease'
            }}
          >
            {user.name.charAt(0)}
            {user.isTyping && (
              <div style={{
                position: 'absolute',
                bottom: '-2px',
                right: '-2px',
                width: '8px',
                height: '8px',
                backgroundColor: 'var(--color-accent)',
                borderRadius: '50%',
                border: '1px solid white'
              }} />
            )}
          </div>
        ))}
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
        {usersArray.length} Online
      </span>
    </div>
  );
};

export default PresenceDots;
