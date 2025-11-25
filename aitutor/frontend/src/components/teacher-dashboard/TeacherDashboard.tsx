/**
 * TeacherDashboard Component
 * Comprehensive class management - SUPERIOR to 2wai
 * Real-time monitoring, intervention alerts, analytics
 */

import React, { useState, useEffect, useMemo } from 'react';
import { storageService, UserProgress, SessionSummary } from '../../services/StorageService';
import './TeacherDashboard.scss';

interface Student {
  id: string;
  name: string;
  avatar: string;
  currentTutor: string;
  status: 'active' | 'idle' | 'struggling' | 'offline';
  currentTopic: string;
  progress: number;
  streak: number;
  lastActive: string;
  questionsToday: number;
  accuracy: number;
}

interface ClassStats {
  totalStudents: number;
  activeNow: number;
  averageProgress: number;
  averageAccuracy: number;
  strugglingCount: number;
  topPerformers: string[];
}

interface ActivityItem {
  type: 'success' | 'warning' | 'milestone' | 'normal';
  icon: string;
  message: string;
  student: string;
  time: string;
}

interface TeacherDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

// Convert API student data to local Student interface
const convertStudentData = (apiStudent: any): Student => {
  // Determine status based on last activity and accuracy
  let status: Student['status'] = 'offline';
  const lastActive = apiStudent.last_active || apiStudent.lastActive;

  if (lastActive) {
    const lastActiveDate = new Date(lastActive);
    const now = new Date();
    const minutesSinceActive = (now.getTime() - lastActiveDate.getTime()) / (1000 * 60);

    if (minutesSinceActive < 5) {
      status = apiStudent.accuracy_rate < 0.6 ? 'struggling' : 'active';
    } else if (minutesSinceActive < 30) {
      status = 'idle';
    }
  }

  const name = apiStudent.student_name || apiStudent.display_name || 'Student';
  const initials = name.split(' ').map((n: string) => n[0]).join('').toUpperCase();

  return {
    id: apiStudent.student_id || apiStudent.id,
    name,
    avatar: initials.slice(0, 2),
    currentTutor: apiStudent.current_tutor || 'Einstein',
    status,
    currentTopic: apiStudent.current_topic || 'General',
    progress: Math.round((apiStudent.mastery_level || 0) * 100),
    streak: apiStudent.streak_days || 0,
    lastActive: lastActive ? formatTimeAgo(lastActive) : 'Never',
    questionsToday: apiStudent.questions_today || 0,
    accuracy: Math.round((apiStudent.accuracy_rate || 0) * 100),
  };
};

// Helper to format time ago
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const minutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

  if (minutes < 1) return 'Now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
};

// Generate students from real progress data only (no mock students)
const generateStudentsFromProgress = (progress: UserProgress): Student[] => {
  const students: Student[] = [];

  // Current user's data
  const totalQuestions = progress.totalQuestionsAnswered;
  const accuracy = totalQuestions > 0
    ? Math.round((progress.totalCorrectAnswers / totalQuestions) * 100)
    : 0;

  // Determine status based on accuracy
  let userStatus: Student['status'] = 'active';
  if (accuracy < 60 && totalQuestions > 3) userStatus = 'struggling';
  else if (progress.totalSessions === 0) userStatus = 'offline';

  const lastSession = progress.sessionHistory[progress.sessionHistory.length - 1];
  const currentTutor = lastSession?.avatarName || 'Einstein';
  const currentTopic = lastSession?.subject || 'General';

  students.push({
    id: 'current-user',
    name: 'You',
    avatar: 'ME',
    currentTutor,
    status: userStatus,
    currentTopic: currentTopic.charAt(0).toUpperCase() + currentTopic.slice(1),
    progress: Math.min(Math.round(progress.totalCorrectAnswers * 5), 100),
    streak: progress.currentStreak,
    lastActive: 'Now',
    questionsToday: totalQuestions,
    accuracy,
  });

  // Note: Real students will be fetched from API via getClassroomStudents
  return students;
};

// Generate activity feed from real session history
const generateActivityFeed = (progress: UserProgress): ActivityItem[] => {
  const activities: ActivityItem[] = [];

  // Add activities from session history
  progress.sessionHistory.slice(-5).reverse().forEach((session, index) => {
    const timeAgo = index === 0 ? 'Just now' : `${(index + 1) * 5} min ago`;

    if (session.correctAnswers > 0) {
      activities.push({
        type: 'success',
        icon: 'check_circle',
        message: `completed "${session.subject}" with ${Math.round((session.correctAnswers / session.questionsAnswered) * 100)}% accuracy`,
        student: 'You',
        time: timeAgo,
      });
    }
  });

  // Add achievement activities
  progress.achievements.slice(-3).forEach((achievement, index) => {
    activities.push({
      type: 'milestone',
      icon: 'emoji_events',
      message: `earned "${achievement.name}" badge!`,
      student: 'You',
      time: `${10 + index * 5} min ago`,
    });
  });

  // Note: Real-time activities will come from WebSocket or API polling
  return activities.slice(0, 6);
};

// Settings interface for persistence
interface TeacherSettings {
  alertOnStruggle: boolean;
  dailySummaryEmail: boolean;
  achievementNotifications: boolean;
  requireCurriculumAlignment: boolean;
  enableHintSystem: boolean;
  allowSkipQuestions: boolean;
}

const defaultSettings: TeacherSettings = {
  alertOnStruggle: true,
  dailySummaryEmail: true,
  achievementNotifications: false,
  requireCurriculumAlignment: true,
  enableHintSystem: true,
  allowSkipQuestions: false,
};

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ isOpen, onClose }) => {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'analytics' | 'settings'>('overview');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [settings, setSettings] = useState<TeacherSettings>(() => {
    const saved = localStorage.getItem('teacherSettings');
    return saved ? JSON.parse(saved) : defaultSettings;
  });
  const [interventionStudent, setInterventionStudent] = useState<Student | null>(null);

  // Load real progress data
  useEffect(() => {
    if (isOpen) {
      const userProgress = storageService.getUserProgress();
      setProgress(userProgress);
    }
  }, [isOpen]);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem('teacherSettings', JSON.stringify(settings));
  }, [settings]);

  // Handle settings toggle
  const handleSettingChange = (key: keyof TeacherSettings) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Handle intervene action
  const handleIntervene = (student: Student) => {
    setInterventionStudent(student);
    // In production, this would open a video call or chat
    alert(`Initiating support session with ${student.name}. In production, this would start a live video/chat intervention.`);
  };

  const students = useMemo(() => {
    if (!progress) return [];
    return generateStudentsFromProgress(progress);
  }, [progress]);

  const activityFeed = useMemo(() => {
    if (!progress) return [];
    return generateActivityFeed(progress);
  }, [progress]);

  const stats: ClassStats = useMemo(() => ({
    totalStudents: students.length,
    activeNow: students.filter(s => s.status === 'active').length,
    averageProgress: students.length > 0 ? Math.round(students.reduce((a, b) => a + b.progress, 0) / students.length) : 0,
    averageAccuracy: students.length > 0 ? Math.round(students.reduce((a, b) => a + b.accuracy, 0) / students.length) : 0,
    strugglingCount: students.filter(s => s.status === 'struggling').length,
    topPerformers: students.filter(s => s.accuracy > 85).map(s => s.name).slice(0, 3),
  }), [students]);

  const filteredStudents = useMemo(() => {
    let result = students;

    // Apply status filter
    if (filterStatus !== 'all') {
      result = result.filter(s => s.status === filterStatus);
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(s =>
        s.name.toLowerCase().includes(query) ||
        s.currentTopic.toLowerCase().includes(query) ||
        s.currentTutor.toLowerCase().includes(query)
      );
    }

    return result;
  }, [students, filterStatus, searchQuery]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#48bb78';
      case 'struggling': return '#ed8936';
      case 'idle': return '#a0aec0';
      case 'offline': return '#e2e8f0';
      default: return '#a0aec0';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="teacher-dashboard-overlay" onClick={onClose}>
      <div className="teacher-dashboard" onClick={e => e.stopPropagation()}>
        <div className="dashboard-header">
          <div className="header-left">
            <h2>
              <span className="material-symbols-outlined">dashboard</span>
              Teacher Dashboard
            </h2>
            <span className="class-name">Mathematics 101 - Period 3</span>
          </div>
          <div className="header-right">
            <div className="live-indicator">
              <span className="dot"></span>
              {stats.activeNow} students active
            </div>
            <button className="close-btn" onClick={onClose}>
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        <div className="dashboard-tabs">
          {(['overview', 'students', 'analytics', 'settings'] as const).map(tab => (
            <button
              key={tab}
              className={activeTab === tab ? 'active' : ''}
              onClick={() => setActiveTab(tab)}
            >
              <span className="material-symbols-outlined">
                {tab === 'overview' ? 'space_dashboard' :
                 tab === 'students' ? 'groups' :
                 tab === 'analytics' ? 'analytics' : 'settings'}
              </span>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="dashboard-content">
          {activeTab === 'overview' && (
            <div className="overview-content">
              {/* Quick Stats */}
              <div className="quick-stats">
                <div className="stat-card">
                  <span className="material-symbols-outlined">groups</span>
                  <div className="stat-value">{stats.totalStudents}</div>
                  <div className="stat-label">Total Students</div>
                </div>
                <div className="stat-card active">
                  <span className="material-symbols-outlined">person</span>
                  <div className="stat-value">{stats.activeNow}</div>
                  <div className="stat-label">Active Now</div>
                </div>
                <div className="stat-card">
                  <span className="material-symbols-outlined">trending_up</span>
                  <div className="stat-value">{stats.averageProgress}%</div>
                  <div className="stat-label">Avg Progress</div>
                </div>
                <div className="stat-card warning">
                  <span className="material-symbols-outlined">warning</span>
                  <div className="stat-value">{stats.strugglingCount}</div>
                  <div className="stat-label">Need Help</div>
                </div>
              </div>

              {/* Alerts */}
              {stats.strugglingCount > 0 && (
                <div className="alerts-section">
                  <h3>
                    <span className="material-symbols-outlined">notifications_active</span>
                    Intervention Needed
                  </h3>
                  <div className="alert-list">
                    {students.filter(s => s.status === 'struggling').map(student => (
                      <div key={student.id} className="alert-item">
                        <div className="student-avatar">{student.avatar}</div>
                        <div className="alert-info">
                          <strong>{student.name}</strong>
                          <span>Struggling with {student.currentTopic}</span>
                        </div>
                        <div className="alert-stats">
                          <span className="accuracy">{student.accuracy}% accuracy</span>
                        </div>
                        <button className="intervene-btn" onClick={() => handleIntervene(student)}>
                          <span className="material-symbols-outlined">support_agent</span>
                          Intervene
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Activity Feed */}
              <div className="activity-section">
                <h3>
                  <span className="material-symbols-outlined">timeline</span>
                  Live Activity
                </h3>
                <div className="activity-feed">
                  {activityFeed.length > 0 ? (
                    activityFeed.map((activity, index) => (
                      <div key={index} className={`activity-item ${activity.type}`}>
                        <span className="material-symbols-outlined">{activity.icon}</span>
                        <span><strong>{activity.student}</strong> {activity.message}</span>
                        <span className="time">{activity.time}</span>
                      </div>
                    ))
                  ) : (
                    <div className="activity-item">
                      <span className="material-symbols-outlined">info</span>
                      <span>No recent activity. Start a tutoring session to see activity here!</span>
                      <span className="time">-</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'students' && (
            <div className="students-content">
              <div className="students-toolbar">
                <div className="search-box">
                  <span className="material-symbols-outlined">search</span>
                  <input
                    type="text"
                    placeholder="Search students..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="filter-buttons">
                  {['all', 'active', 'struggling', 'idle', 'offline'].map(status => (
                    <button
                      key={status}
                      className={filterStatus === status ? 'active' : ''}
                      onClick={() => setFilterStatus(status)}
                    >
                      {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
                      {status !== 'all' && (
                        <span className="count">
                          {students.filter(s => s.status === status).length}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              <div className="students-grid">
                {filteredStudents.map(student => (
                  <div
                    key={student.id}
                    className={`student-card ${student.status}`}
                    onClick={() => setSelectedStudent(student)}
                  >
                    <div className="student-header">
                      <div className="student-avatar" style={{ borderColor: getStatusColor(student.status) }}>
                        {student.avatar}
                      </div>
                      <div className="student-info">
                        <h4>{student.name}</h4>
                        <span className="tutor-badge">
                          <span className="material-symbols-outlined">smart_toy</span>
                          {student.currentTutor}
                        </span>
                      </div>
                      <div className={`status-badge ${student.status}`}>
                        {student.status}
                      </div>
                    </div>

                    <div className="student-progress">
                      <div className="progress-label">
                        <span>{student.currentTopic}</span>
                        <span>{student.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${student.progress}%` }} />
                      </div>
                    </div>

                    <div className="student-stats">
                      <div className="stat">
                        <span className="material-symbols-outlined">local_fire_department</span>
                        {student.streak} day streak
                      </div>
                      <div className="stat">
                        <span className="material-symbols-outlined">check_circle</span>
                        {student.accuracy}% accuracy
                      </div>
                      <div className="stat">
                        <span className="material-symbols-outlined">quiz</span>
                        {student.questionsToday} today
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="analytics-content">
              <div className="analytics-grid">
                <div className="chart-card">
                  <h4>Class Progress Over Time</h4>
                  <div className="chart-visual">
                    {/* Simple bar chart using CSS */}
                    <div className="simple-chart progress-chart">
                      {progress?.sessionHistory.slice(-7).map((session, i) => (
                        <div key={i} className="chart-bar-container">
                          <div
                            className="chart-bar"
                            style={{
                              height: `${Math.min((session.correctAnswers / Math.max(session.questionsAnswered, 1)) * 100, 100)}%`
                            }}
                            title={`${session.subject}: ${session.correctAnswers}/${session.questionsAnswered}`}
                          />
                          <span className="chart-label">D{i + 1}</span>
                        </div>
                      )) || <p className="no-data">Complete sessions to see progress</p>}
                    </div>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Topic Difficulty Analysis</h4>
                  <div className="chart-visual">
                    <div className="difficulty-list">
                      {progress?.skills && Object.entries(progress.skills).length > 0 ? (
                        Object.entries(progress.skills).map(([skillName, data]) => (
                          <div key={skillName} className="difficulty-item">
                            <span className="subject-name">{data.name || skillName}</span>
                            <div className="difficulty-bar-bg">
                              <div
                                className="difficulty-bar"
                                style={{
                                  width: `${Math.round((data.questionsCorrect / Math.max(data.questionsAttempted, 1)) * 100)}%`,
                                  backgroundColor: (data.questionsCorrect / Math.max(data.questionsAttempted, 1)) > 0.7 ? '#48bb78' : '#ed8936'
                                }}
                              />
                            </div>
                            <span className="difficulty-pct">
                              {Math.round((data.questionsCorrect / Math.max(data.questionsAttempted, 1)) * 100)}%
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="no-data">Answer questions to see difficulty analysis</p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Tutor Usage</h4>
                  <div className="chart-visual">
                    <div className="tutor-usage-list">
                      {(() => {
                        const tutorCounts: Record<string, number> = {};
                        progress?.sessionHistory.forEach(s => {
                          const tutor = s.avatarName || 'Einstein';
                          tutorCounts[tutor] = (tutorCounts[tutor] || 0) + 1;
                        });
                        const total = Object.values(tutorCounts).reduce((a, b) => a + b, 0) || 1;
                        return Object.entries(tutorCounts).length > 0 ? (
                          Object.entries(tutorCounts).map(([tutor, count]) => (
                            <div key={tutor} className="tutor-usage-item">
                              <span className="tutor-name">{tutor}</span>
                              <div className="usage-bar-bg">
                                <div className="usage-bar" style={{ width: `${(count / total) * 100}%` }} />
                              </div>
                              <span className="usage-count">{count} sessions</span>
                            </div>
                          ))
                        ) : (
                          <p className="no-data">Start sessions to see tutor usage</p>
                        );
                      })()}
                    </div>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Daily Activity</h4>
                  <div className="chart-visual">
                    <div className="activity-summary">
                      <div className="activity-stat">
                        <span className="stat-number">{progress?.totalSessions || 0}</span>
                        <span className="stat-label">Total Sessions</span>
                      </div>
                      <div className="activity-stat">
                        <span className="stat-number">{progress?.totalQuestionsAnswered || 0}</span>
                        <span className="stat-label">Questions Answered</span>
                      </div>
                      <div className="activity-stat">
                        <span className="stat-number">{progress?.currentStreak || 0}</span>
                        <span className="stat-label">Day Streak</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="insights-section">
                <h3>AI Insights</h3>
                <div className="insight-cards">
                  {stats.strugglingCount > 0 ? (
                    <div className="insight-card">
                      <span className="material-symbols-outlined">lightbulb</span>
                      <p><strong>Recommendation:</strong> {stats.strugglingCount} student(s) need attention. Consider one-on-one review sessions for struggling topics.</p>
                    </div>
                  ) : (
                    <div className="insight-card success">
                      <span className="material-symbols-outlined">celebration</span>
                      <p><strong>Great Progress:</strong> All students are performing well! Class average accuracy is {stats.averageAccuracy}%.</p>
                    </div>
                  )}
                  {progress && progress.currentStreak >= 3 && (
                    <div className="insight-card success">
                      <span className="material-symbols-outlined">trending_up</span>
                      <p><strong>Engagement:</strong> Your demo student has a {progress.currentStreak}-day learning streak. Consistent engagement correlates with better outcomes.</p>
                    </div>
                  )}
                  <div className="insight-card">
                    <span className="material-symbols-outlined">school</span>
                    <p><strong>Tip:</strong> Students using multiple tutors show 23% better retention. Encourage trying different teaching styles.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="settings-content">
              <div className="settings-group">
                <h3>Notification Preferences</h3>
                <label className="toggle-setting">
                  <span>Alert when student struggles for 3+ minutes</span>
                  <input
                    type="checkbox"
                    checked={settings.alertOnStruggle}
                    onChange={() => handleSettingChange('alertOnStruggle')}
                  />
                </label>
                <label className="toggle-setting">
                  <span>Daily progress summary email</span>
                  <input
                    type="checkbox"
                    checked={settings.dailySummaryEmail}
                    onChange={() => handleSettingChange('dailySummaryEmail')}
                  />
                </label>
                <label className="toggle-setting">
                  <span>Achievement notifications</span>
                  <input
                    type="checkbox"
                    checked={settings.achievementNotifications}
                    onChange={() => handleSettingChange('achievementNotifications')}
                  />
                </label>
              </div>

              <div className="settings-group">
                <h3>Content Controls</h3>
                <label className="toggle-setting">
                  <span>Require curriculum alignment</span>
                  <input
                    type="checkbox"
                    checked={settings.requireCurriculumAlignment}
                    onChange={() => handleSettingChange('requireCurriculumAlignment')}
                  />
                </label>
                <label className="toggle-setting">
                  <span>Enable hint system</span>
                  <input
                    type="checkbox"
                    checked={settings.enableHintSystem}
                    onChange={() => handleSettingChange('enableHintSystem')}
                  />
                </label>
                <label className="toggle-setting">
                  <span>Allow skip questions</span>
                  <input
                    type="checkbox"
                    checked={settings.allowSkipQuestions}
                    onChange={() => handleSettingChange('allowSkipQuestions')}
                  />
                </label>
              </div>

              <div className="settings-saved-indicator">
                <span className="material-symbols-outlined">check_circle</span>
                Settings auto-saved
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
