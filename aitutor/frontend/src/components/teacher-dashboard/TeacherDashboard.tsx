/**
 * TeacherDashboard Component
 * Comprehensive class management - SUPERIOR to 2wai
 * Real-time monitoring, intervention alerts, analytics
 */

import React, { useState, useEffect } from 'react';
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

interface TeacherDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

// Sample data - in production, this comes from API
const SAMPLE_STUDENTS: Student[] = [
  { id: '1', name: 'Emma Johnson', avatar: 'EJ', currentTutor: 'Einstein', status: 'active', currentTopic: 'Quadratic Equations', progress: 78, streak: 5, lastActive: 'Now', questionsToday: 12, accuracy: 85 },
  { id: '2', name: 'Liam Smith', avatar: 'LS', currentTutor: 'Curie', status: 'struggling', currentTopic: 'Chemical Bonding', progress: 45, streak: 2, lastActive: 'Now', questionsToday: 8, accuracy: 52 },
  { id: '3', name: 'Olivia Brown', avatar: 'OB', currentTutor: 'Shakespeare', status: 'active', currentTopic: 'Sonnets', progress: 92, streak: 14, lastActive: 'Now', questionsToday: 15, accuracy: 94 },
  { id: '4', name: 'Noah Davis', avatar: 'ND', currentTutor: 'Ada', status: 'idle', currentTopic: 'Python Loops', progress: 67, streak: 3, lastActive: '5 min ago', questionsToday: 6, accuracy: 78 },
  { id: '5', name: 'Ava Wilson', avatar: 'AW', currentTutor: 'Socrates', status: 'active', currentTopic: 'Ethics', progress: 81, streak: 8, lastActive: 'Now', questionsToday: 9, accuracy: 89 },
  { id: '6', name: 'James Miller', avatar: 'JM', currentTutor: 'Einstein', status: 'offline', currentTopic: 'Relativity', progress: 34, streak: 0, lastActive: '2 hours ago', questionsToday: 0, accuracy: 65 },
];

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ isOpen, onClose }) => {
  const [students, setStudents] = useState<Student[]>(SAMPLE_STUDENTS);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'analytics' | 'settings'>('overview');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const stats: ClassStats = {
    totalStudents: students.length,
    activeNow: students.filter(s => s.status === 'active').length,
    averageProgress: Math.round(students.reduce((a, b) => a + b.progress, 0) / students.length),
    averageAccuracy: Math.round(students.reduce((a, b) => a + b.accuracy, 0) / students.length),
    strugglingCount: students.filter(s => s.status === 'struggling').length,
    topPerformers: students.filter(s => s.accuracy > 85).map(s => s.name).slice(0, 3),
  };

  const filteredStudents = filterStatus === 'all'
    ? students
    : students.filter(s => s.status === filterStatus);

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
                        <button className="intervene-btn">
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
                  <div className="activity-item success">
                    <span className="material-symbols-outlined">check_circle</span>
                    <span><strong>Olivia</strong> completed "Sonnets" with 94% accuracy</span>
                    <span className="time">Just now</span>
                  </div>
                  <div className="activity-item">
                    <span className="material-symbols-outlined">play_circle</span>
                    <span><strong>Emma</strong> started learning Quadratic Equations</span>
                    <span className="time">2 min ago</span>
                  </div>
                  <div className="activity-item warning">
                    <span className="material-symbols-outlined">help</span>
                    <span><strong>Liam</strong> requested a hint for Chemical Bonding</span>
                    <span className="time">5 min ago</span>
                  </div>
                  <div className="activity-item milestone">
                    <span className="material-symbols-outlined">emoji_events</span>
                    <span><strong>Ava</strong> achieved 8-day streak!</span>
                    <span className="time">10 min ago</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'students' && (
            <div className="students-content">
              <div className="students-toolbar">
                <div className="search-box">
                  <span className="material-symbols-outlined">search</span>
                  <input type="text" placeholder="Search students..." />
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
                  <div className="chart-placeholder">
                    <span className="material-symbols-outlined">show_chart</span>
                    <p>Progress chart visualization</p>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Topic Difficulty Analysis</h4>
                  <div className="chart-placeholder">
                    <span className="material-symbols-outlined">bar_chart</span>
                    <p>Topics ranked by difficulty</p>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Tutor Usage</h4>
                  <div className="chart-placeholder">
                    <span className="material-symbols-outlined">pie_chart</span>
                    <p>Which tutors are most popular</p>
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Engagement Heatmap</h4>
                  <div className="chart-placeholder">
                    <span className="material-symbols-outlined">grid_view</span>
                    <p>Peak learning times</p>
                  </div>
                </div>
              </div>

              <div className="insights-section">
                <h3>AI Insights</h3>
                <div className="insight-cards">
                  <div className="insight-card">
                    <span className="material-symbols-outlined">lightbulb</span>
                    <p><strong>Recommendation:</strong> Consider reviewing Chemical Bonding concepts. 3 students are struggling with this topic.</p>
                  </div>
                  <div className="insight-card success">
                    <span className="material-symbols-outlined">trending_up</span>
                    <p><strong>Success:</strong> Sonnets module has 94% average completion. Consider advancing to more complex poetry.</p>
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
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="toggle-setting">
                  <span>Daily progress summary email</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="toggle-setting">
                  <span>Achievement notifications</span>
                  <input type="checkbox" />
                </label>
              </div>

              <div className="settings-group">
                <h3>Content Controls</h3>
                <label className="toggle-setting">
                  <span>Require curriculum alignment</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="toggle-setting">
                  <span>Enable hint system</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="toggle-setting">
                  <span>Allow skip questions</span>
                  <input type="checkbox" />
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
