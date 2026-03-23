import React, { createContext, useContext, useEffect, useState } from 'react';
import { socketService } from '../../services/socket';

interface UserPresence {
  id: string;
  name: string;
  isTyping: boolean;
  cursor: { x: number; y: number } | null;
  lastActive: number;
}

interface RealtimeContextType {
  onlineUsers: Record<string, UserPresence>;
  setTyping: (isTyping: boolean) => void;
  updateCursor: (x: number, y: number) => void;
}

const RealtimeContext = createContext<RealtimeContextType | undefined>(undefined);

export const RealtimeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [onlineUsers, setOnlineUsers] = useState<Record<string, UserPresence>>({});
  
  useEffect(() => {
    const socket = socketService.connect();
    const userJson = localStorage.getItem('user');
    const user = userJson ? JSON.parse(userJson) : null;

    if (user && socket) {
      // Join default workspace
      socket.emit('join_workspace', { workspace_id: 'default', user_id: user.id, user_name: user.name });

      socket.on('presence_update', (data: any) => {
        setOnlineUsers(data.users || {});
      });

      socket.on('user_typing', (data: { user_id: string; is_typing: boolean }) => {
        setOnlineUsers(prev => ({
          ...prev,
          [data.user_id]: { ...prev[data.user_id], isTyping: data.is_typing }
        }));
      });

      socket.on('cursor_move', (data: { user_id: string; x: number; y: number }) => {
        setOnlineUsers(prev => ({
          ...prev,
          [data.user_id]: { ...prev[data.user_id], cursor: { x: data.x, y: data.y } }
        }));
      });
    }

    return () => {
      socketService.disconnect();
    };
  }, []);

  const setTyping = (isTyping: boolean) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    socketService.emit('typing', { workspace_id: 'default', user_id: user.id, is_typing: isTyping });
  };

  const updateCursor = (x: number, y: number) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    socketService.emit('cursor_position', { workspace_id: 'default', user_id: user.id, x, y });
  };

  return (
    <RealtimeContext.Provider value={{ onlineUsers, setTyping, updateCursor }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (context === undefined) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
};
