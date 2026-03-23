import api from './api';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  created_at: string;
}

export const taskService = {
  getTasks: async (listId: string = 'default'): Promise<Task[]> => {
    const response = await api.get(`/api/v1/tasks?list_id=${listId}`);
    return response.data;
  },

  createTask: async (task: any): Promise<Task> => {
    // The backend expects list_id in the body
    const response = await api.post('/api/v1/tasks', { ...task, list_id: 'default' });
    return response.data;
  },

  updateTask: async (taskId: string, updates: any): Promise<Task> => {
    const response = await api.put(`/api/v1/tasks/${taskId}`, updates);
    return response.data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`/api/v1/tasks/${taskId}`);
  }
};
