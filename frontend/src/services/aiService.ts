import api from './api';

export const aiService = {
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data.status === 'healthy';
    } catch (e) {
      return false;
    }
  },
  
  getTaskSuggestion: async (title: string, description?: string) => {
    try {
      const response = await api.post('/ai/suggest/task', {
        raw_title: title,
        raw_description: description,
        context: {}
      });
      return response.data;
    } catch (e) {
      console.error('AI Suggestion failed:', e);
      return null;
    }
  },

  getAiSuggestions: async (taskId: string) => {
    const response = await api.get(`/ai/suggest/${taskId}`);
    return response.data;
  }
};
