import keycloak from '../auth/keycloak';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

interface RequestOptions extends RequestInit {
  requireAuth?: boolean;
}

interface ApiResponse<T> {
  data: T;
  status: number;
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { requireAuth = true, headers = {}, ...fetchOptions } = options;

  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };

  if (requireAuth) {
    // if (!keycloak.authenticated || !keycloak.token) {
    //   throw new Error('NOT_AUTHENTICATED');
    // }
    requestHeaders['Authorization'] = `Bearer ${keycloak.token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: requestHeaders,
    });

    if (response.status === 401 && keycloak.authenticated) {
      const refreshed = await keycloak.updateToken(30);
      if (refreshed && keycloak.token) {
        requestHeaders['Authorization'] = `Bearer ${keycloak.token}`;
        const retryResponse = await fetch(url, {
          ...fetchOptions,
          headers: requestHeaders,
        });
        if (!retryResponse.ok) {
          throw new Error(`HTTP ${retryResponse.status}: ${retryResponse.statusText}`);
        }
        const data = await retryResponse.json();
        return { data, status: retryResponse.status };
      }
      throw new Error('SESSION_EXPIRED');
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    if (response.status === 204) {
      return { data: {} as T, status: response.status };
    }

    const data = await response.json();
    return { data, status: response.status };
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    }),

  put: <T>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
};

export interface Comment {
  _id: string;
  post_id: string;
  user_id: string;
  username: string;
  text: string;
  created_at: string;
}

export interface AnalysisSummary {
  id: string;
  text_preview: string;
  label: string;
  score: number;
  created_at: string;
}

export interface Post {
  _id: string;
  user_id: string;
  username: string;
  content: string;
  likes: string[];
  comments_count: number;
  created_at: string;
  analysis_id?: string;
  analysis_data?: {
      label: string;
      score: number;
      text_preview: string;
  };
}

export const socialApi = {
  getFeed: async () => {
    const response = await api.get<Post[]>('/social/feed');
    return response.data;
  },

  getMyAnalyses: async () => {
    const response = await api.get<AnalysisSummary[]>('/social/my-analyses');
    return response.data;
  },

  createPost: async (content: string, analysisId?: string) => {
    const response = await api.post<{ success: boolean; postId: string }>('/social/feed', {
      content,
      analysis_id: analysisId
    });
    return response.data;
  },

  toggleLike: async (postId: string) => {
    const response = await api.post<{ success: boolean; liked: boolean }>(`/social/feed/${postId}/like`);
    return response.data;
  },

  addComment: async (postId: string, text: string) => {
    const response = await api.post<{ success: boolean }>(`/social/feed/${postId}/comment`, { text });
    return response.data;
  },

  getComments: async (postId: string) => {
    const response = await api.get<Comment[]>(`/social/feed/${postId}/comments`);
    return response.data;
  },

  deletePost: async (postId: string) => {
    const response = await api.delete<{ success: boolean }>(`/social/feed/${postId}`);
    return response.data;
  },

  updatePost: async (postId: string, content: string) => {
    const response = await api.put<{ success: boolean }>(`/social/feed/${postId}`, { content });
    return response.data;
  },

  deleteComment: async (commentId: string) => {
    const response = await api.delete<{ success: boolean }>(`/social/feed/comments/${commentId}`);
    return response.data;
  },

  updateComment: async (commentId: string, text: string) => {
    const response = await api.put<{ success: boolean }>(`/social/feed/comments/${commentId}`, { text });
    return response.data;
  }
};
