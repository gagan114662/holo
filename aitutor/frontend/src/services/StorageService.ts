/**
 * Storage Service - Persistent data management with localStorage
 * Tracks user progress, sessions, achievements, and settings
 */

export interface UserProgress {
  odUserId: string;
  totalSessions: number;
  totalQuestionsAnswered: number;
  totalCorrectAnswers: number;
  currentStreak: number;
  longestStreak: number;
  lastActiveDate: string;
  createdAt: string;
  skills: Record<string, SkillProgress>;
  achievements: Achievement[];
  sessionHistory: SessionSummary[];
}

export interface SkillProgress {
  name: string;
  subject: string;
  level: number;
  xp: number;
  questionsAttempted: number;
  questionsCorrect: number;
  lastPracticed: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlockedAt: string;
  category: 'learning' | 'streak' | 'mastery' | 'exploration';
}

export interface SessionSummary {
  id: string;
  avatarId: string;
  avatarName: string;
  subject: string;
  startTime: string;
  endTime: string;
  questionsAnswered: number;
  correctAnswers: number;
  topics: string[];
}

export interface CurrentSession {
  id: string;
  avatarId: string;
  avatarName: string;
  subject: string;
  startTime: string;
  questionsAnswered: number;
  correctAnswers: number;
  conversationHistory: ConversationMessage[];
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  questionId?: string;
  wasCorrect?: boolean;
}

export interface StudentData {
  odUserId: string;
  name: string;
  avatar?: string;
  progress: UserProgress;
  isActive: boolean;
  lastSeen: string;
}

const STORAGE_KEYS = {
  USER_PROGRESS: 'holotutor_progress',
  CURRENT_SESSION: 'holotutor_current_session',
  SETTINGS: 'holotutor_settings',
  STUDENTS: 'holotutor_students', // For teacher mode
  API_KEYS: 'holotutor_api_keys',
};

// Achievement definitions
const ACHIEVEMENT_DEFINITIONS: Omit<Achievement, 'unlockedAt'>[] = [
  { id: 'first_session', name: 'First Steps', description: 'Complete your first tutoring session', icon: 'rocket_launch', category: 'learning' },
  { id: 'five_correct', name: 'Quick Learner', description: 'Answer 5 questions correctly', icon: 'psychology', category: 'learning' },
  { id: 'ten_sessions', name: 'Dedicated Student', description: 'Complete 10 tutoring sessions', icon: 'school', category: 'learning' },
  { id: 'streak_3', name: 'On a Roll', description: 'Maintain a 3-day streak', icon: 'local_fire_department', category: 'streak' },
  { id: 'streak_7', name: 'Week Warrior', description: 'Maintain a 7-day streak', icon: 'whatshot', category: 'streak' },
  { id: 'streak_30', name: 'Monthly Master', description: 'Maintain a 30-day streak', icon: 'emoji_events', category: 'streak' },
  { id: 'first_mastery', name: 'Skill Mastered', description: 'Reach level 5 in any skill', icon: 'military_tech', category: 'mastery' },
  { id: 'multi_subject', name: 'Renaissance Mind', description: 'Study 3 different subjects', icon: 'auto_awesome', category: 'exploration' },
  { id: 'all_avatars', name: 'History Buff', description: 'Learn from all 8 historical tutors', icon: 'diversity_3', category: 'exploration' },
  { id: 'perfect_session', name: 'Perfectionist', description: 'Answer all questions correctly in a session', icon: 'stars', category: 'mastery' },
];

class StorageService {
  private userId: string;

  constructor() {
    // Generate or retrieve user ID (will be overridden by Firebase auth)
    this.userId = this.getOrCreateUserId();
  }

  /**
   * Safely parse JSON with error handling
   * Returns null if parsing fails instead of throwing
   */
  private safeJsonParse<T>(json: string | null, fallback: T | null = null): T | null {
    if (!json) return fallback;
    try {
      return JSON.parse(json) as T;
    } catch (error) {
      console.error('Failed to parse JSON from localStorage:', error);
      return fallback;
    }
  }

  /**
   * Set user ID from Firebase authentication
   * This should be called when user signs in
   */
  setAuthenticatedUser(firebaseUid: string): void {
    this.userId = firebaseUid;
    localStorage.setItem('holotutor_user_id', firebaseUid);

    // Migrate any existing progress to the authenticated user
    const existingProgress = localStorage.getItem(STORAGE_KEYS.USER_PROGRESS);
    if (existingProgress) {
      const progress = this.safeJsonParse<UserProgress>(existingProgress);
      if (progress) {
        progress.odUserId = firebaseUid;
        localStorage.setItem(STORAGE_KEYS.USER_PROGRESS, JSON.stringify(progress));
      }
    }
  }

  /**
   * Get current user ID (Firebase UID if authenticated, or local ID)
   */
  getUserId(): string {
    return this.userId;
  }

  private getOrCreateUserId(): string {
    let userId = localStorage.getItem('holotutor_user_id');
    if (!userId) {
      // Generate temporary ID until Firebase auth sets the real one
      userId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('holotutor_user_id', userId);
    }
    return userId;
  }

  // ============ User Progress ============

  getUserProgress(): UserProgress {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PROGRESS);
    const parsed = this.safeJsonParse<UserProgress>(stored);
    if (parsed) {
      return parsed;
    }

    // Create default progress
    const defaultProgress: UserProgress = {
      odUserId: this.userId,
      totalSessions: 0,
      totalQuestionsAnswered: 0,
      totalCorrectAnswers: 0,
      currentStreak: 0,
      longestStreak: 0,
      lastActiveDate: new Date().toISOString().split('T')[0],
      createdAt: new Date().toISOString(),
      skills: {},
      achievements: [],
      sessionHistory: [],
    };

    this.saveUserProgress(defaultProgress);
    return defaultProgress;
  }

  saveUserProgress(progress: UserProgress): void {
    localStorage.setItem(STORAGE_KEYS.USER_PROGRESS, JSON.stringify(progress));
  }

  // ============ Session Management ============

  startSession(avatarId: string, avatarName: string, subject: string): CurrentSession {
    const session: CurrentSession = {
      id: `session_${Date.now()}`,
      avatarId,
      avatarName,
      subject,
      startTime: new Date().toISOString(),
      questionsAnswered: 0,
      correctAnswers: 0,
      conversationHistory: [],
    };

    localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, JSON.stringify(session));
    return session;
  }

  getCurrentSession(): CurrentSession | null {
    const stored = localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION);
    return this.safeJsonParse<CurrentSession>(stored);
  }

  updateSession(updates: Partial<CurrentSession>): CurrentSession | null {
    const session = this.getCurrentSession();
    if (!session) return null;

    const updated = { ...session, ...updates };
    localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, JSON.stringify(updated));
    return updated;
  }

  addConversationMessage(message: ConversationMessage): void {
    const session = this.getCurrentSession();
    if (session) {
      session.conversationHistory.push(message);
      this.updateSession({ conversationHistory: session.conversationHistory });
    }
  }

  endSession(): SessionSummary | null {
    const session = this.getCurrentSession();
    if (!session) return null;

    const summary: SessionSummary = {
      id: session.id,
      avatarId: session.avatarId,
      avatarName: session.avatarName,
      subject: session.subject,
      startTime: session.startTime,
      endTime: new Date().toISOString(),
      questionsAnswered: session.questionsAnswered,
      correctAnswers: session.correctAnswers,
      topics: this.extractTopics(session.conversationHistory),
    };

    // Update user progress
    const progress = this.getUserProgress();
    progress.totalSessions++;
    progress.totalQuestionsAnswered += session.questionsAnswered;
    progress.totalCorrectAnswers += session.correctAnswers;
    progress.sessionHistory.unshift(summary);

    // Keep only last 50 sessions
    if (progress.sessionHistory.length > 50) {
      progress.sessionHistory = progress.sessionHistory.slice(0, 50);
    }

    // Update streak
    const today = new Date().toISOString().split('T')[0];
    const lastActive = progress.lastActiveDate;
    const daysDiff = this.daysBetween(lastActive, today);

    if (daysDiff === 1) {
      progress.currentStreak++;
    } else if (daysDiff > 1) {
      progress.currentStreak = 1;
    }
    // If same day, streak stays the same

    progress.lastActiveDate = today;
    if (progress.currentStreak > progress.longestStreak) {
      progress.longestStreak = progress.currentStreak;
    }

    // Check for new achievements
    this.checkAchievements(progress, session);

    this.saveUserProgress(progress);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION);

    return summary;
  }

  // ============ Question Tracking ============

  recordAnswer(isCorrect: boolean, skill?: string, subject?: string): void {
    const session = this.getCurrentSession();
    if (session) {
      session.questionsAnswered++;
      if (isCorrect) {
        session.correctAnswers++;
      }
      this.updateSession(session);
    }

    // Update skill progress
    if (skill && subject) {
      this.updateSkillProgress(skill, subject, isCorrect);
    }
  }

  private updateSkillProgress(skillName: string, subject: string, wasCorrect: boolean): void {
    const progress = this.getUserProgress();

    if (!progress.skills[skillName]) {
      progress.skills[skillName] = {
        name: skillName,
        subject,
        level: 1,
        xp: 0,
        questionsAttempted: 0,
        questionsCorrect: 0,
        lastPracticed: new Date().toISOString(),
      };
    }

    const skill = progress.skills[skillName];
    skill.questionsAttempted++;
    skill.lastPracticed = new Date().toISOString();

    if (wasCorrect) {
      skill.questionsCorrect++;
      skill.xp += 10;

      // Level up every 100 XP
      const newLevel = Math.floor(skill.xp / 100) + 1;
      if (newLevel > skill.level) {
        skill.level = newLevel;
      }
    } else {
      skill.xp += 2; // Small XP for attempting
    }

    this.saveUserProgress(progress);
  }

  // ============ Achievements ============

  private checkAchievements(progress: UserProgress, session: CurrentSession): void {
    const unlockedIds = new Set(progress.achievements.map(a => a.id));

    const tryUnlock = (id: string) => {
      if (!unlockedIds.has(id)) {
        const def = ACHIEVEMENT_DEFINITIONS.find(a => a.id === id);
        if (def) {
          progress.achievements.push({
            ...def,
            unlockedAt: new Date().toISOString(),
          });
        }
      }
    };

    // Check conditions
    if (progress.totalSessions >= 1) tryUnlock('first_session');
    if (progress.totalCorrectAnswers >= 5) tryUnlock('five_correct');
    if (progress.totalSessions >= 10) tryUnlock('ten_sessions');
    if (progress.currentStreak >= 3) tryUnlock('streak_3');
    if (progress.currentStreak >= 7) tryUnlock('streak_7');
    if (progress.currentStreak >= 30) tryUnlock('streak_30');

    // Check mastery
    if (Object.values(progress.skills).some(s => s.level >= 5)) {
      tryUnlock('first_mastery');
    }

    // Check exploration
    const uniqueSubjects = new Set(progress.sessionHistory.map(s => s.subject));
    if (uniqueSubjects.size >= 3) tryUnlock('multi_subject');

    const uniqueAvatars = new Set(progress.sessionHistory.map(s => s.avatarId));
    if (uniqueAvatars.size >= 8) tryUnlock('all_avatars');

    // Perfect session
    if (session.questionsAnswered >= 5 && session.correctAnswers === session.questionsAnswered) {
      tryUnlock('perfect_session');
    }
  }

  getAchievementDefinitions(): typeof ACHIEVEMENT_DEFINITIONS {
    return ACHIEVEMENT_DEFINITIONS;
  }

  // ============ Teacher Mode - Students ============

  getStudents(): StudentData[] {
    const stored = localStorage.getItem(STORAGE_KEYS.STUDENTS);
    return this.safeJsonParse<StudentData[]>(stored) || [];
  }

  addStudent(student: StudentData): void {
    const students = this.getStudents();
    students.push(student);
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(students));
  }

  updateStudent(odUserId: string, updates: Partial<StudentData>): void {
    const students = this.getStudents();
    const index = students.findIndex(s => s.odUserId === odUserId);
    if (index !== -1) {
      students[index] = { ...students[index], ...updates };
      localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(students));
    }
  }

  // ============ Settings ============

  getSettings(): Record<string, any> {
    const stored = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    const defaultSettings = {
      language: 'en',
      voiceEnabled: true,
      darkMode: false,
      ageGroup: 'middle_school',
    };
    return this.safeJsonParse<Record<string, any>>(stored) || defaultSettings;
  }

  saveSetting(key: string, value: any): void {
    const settings = this.getSettings();
    settings[key] = value;
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
  }

  // ============ API Keys (stored locally) ============

  getApiKeys(): { did?: string; heygen?: string; gemini?: string } {
    const stored = localStorage.getItem(STORAGE_KEYS.API_KEYS);
    return this.safeJsonParse<{ did?: string; heygen?: string; gemini?: string }>(stored) || {};
  }

  saveApiKey(service: 'did' | 'heygen' | 'gemini', key: string): void {
    const keys = this.getApiKeys();
    keys[service] = key;
    localStorage.setItem(STORAGE_KEYS.API_KEYS, JSON.stringify(keys));
  }

  // ============ Helpers ============

  private daysBetween(date1: string, date2: string): number {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    const diffTime = Math.abs(d2.getTime() - d1.getTime());
    return Math.floor(diffTime / (1000 * 60 * 60 * 24));
  }

  private extractTopics(history: ConversationMessage[]): string[] {
    // Simple topic extraction from conversation
    const topics = new Set<string>();
    const keywords = ['math', 'physics', 'chemistry', 'biology', 'literature', 'history',
                      'algebra', 'geometry', 'calculus', 'evolution', 'atoms', 'molecules',
                      'shakespeare', 'poetry', 'philosophy', 'ethics', 'art', 'painting'];

    history.forEach(msg => {
      const lower = msg.content.toLowerCase();
      keywords.forEach(kw => {
        if (lower.includes(kw)) {
          topics.add(kw.charAt(0).toUpperCase() + kw.slice(1));
        }
      });
    });

    return Array.from(topics).slice(0, 5);
  }

  clearAllData(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
    localStorage.removeItem('holotutor_user_id');
    this.userId = this.getOrCreateUserId();
  }
}

export const storageService = new StorageService();
export default StorageService;
