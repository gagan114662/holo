/**
 * API Service - Connects to HoloTutor backend
 * Real API calls replacing mock data
 */

import { firebaseService } from './FirebaseService';

const API_BASE_URL = process.env.REACT_APP_DASH_API_URL || 'http://localhost:8000/api';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: any;
  headers?: Record<string, string>;
}

class ApiService {
  /**
   * Make an authenticated API request
   */
  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const token = await firebaseService.getIdToken();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }
    
    return response.json();
  }

  // ============ Questions API ============

  async getNextQuestion(subjectId?: string, skillId?: string) {
    const params = new URLSearchParams();
    if (subjectId) params.append('subject_id', subjectId);
    if (skillId) params.append('skill_id', skillId);
    const query = params.toString() ? `?${params}` : '';
    return this.request(`/questions/next${query}`);
  }

  async submitAnswer(questionId: string, answer: string, sessionId?: string) {
    return this.request('/questions/submit', {
      method: 'POST',
      body: { question_id: questionId, answer, session_id: sessionId },
    });
  }

  async getSubjects() {
    return this.request('/questions/subjects');
  }

  async getSkills(subjectId: string) {
    return this.request(`/questions/subjects/${subjectId}/skills`);
  }

  // ============ Sessions API ============

  async createSession(avatarId: string, subjectId?: string) {
    return this.request('/sessions', {
      method: 'POST',
      body: { avatar_id: avatarId, subject_id: subjectId },
    });
  }

  async getCurrentSession() {
    return this.request('/sessions/current');
  }

  async endSession(sessionId: string) {
    return this.request(`/sessions/${sessionId}/end`, { method: 'POST' });
  }

  async getSessionStats() {
    return this.request('/sessions/stats/summary');
  }

  // ============ Progress API ============

  async getProgress() {
    return this.request('/progress');
  }

  async getSkillProgress(subjectId?: string) {
    const query = subjectId ? `?subject_id=${subjectId}` : '';
    return this.request(`/progress/skills${query}`);
  }

  async getDailyProgress() {
    return this.request('/progress/daily');
  }

  async getLeaderboard(limit: number = 10) {
    return this.request(`/progress/leaderboard?limit=${limit}`);
  }

  // ============ Teacher API ============

  async getClassrooms() {
    return this.request('/teachers/classrooms');
  }

  async createClassroom(data: { name: string; description?: string; subjectId?: string; gradeLevel?: string }) {
    return this.request('/teachers/classrooms', {
      method: 'POST',
      body: data,
    });
  }

  async getClassroomStudents(classroomId: string) {
    return this.request(`/teachers/classrooms/${classroomId}/students`);
  }

  async getClassroomStats(classroomId: string) {
    return this.request(`/teachers/classrooms/${classroomId}/stats`);
  }

  async joinClassroom(joinCode: string) {
    return this.request('/teachers/join', {
      method: 'POST',
      body: { join_code: joinCode },
    });
  }

  // ============ Avatar API ============

  async getAvatars() {
    return this.request('/avatars/historical');
  }

  async getAvatarsBySubject(subject: string) {
    return this.request(`/avatars/by-subject/${subject}`);
  }

  async createAvatarSession(avatarId: string) {
    return this.request('/avatars/sessions/create', {
      method: 'POST',
      body: { avatar_id: avatarId },
    });
  }

  async speakAsAvatar(sessionId: string, text: string, emotion: string = 'neutral') {
    return this.request(`/avatars/sessions/${sessionId}/speak`, {
      method: 'POST',
      body: { text, emotion },
    });
  }
}

export const apiService = new ApiService();
