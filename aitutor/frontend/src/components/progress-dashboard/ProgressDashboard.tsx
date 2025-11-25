/**
 * ProgressDashboard Component
 * Shows student learning progress with visual analytics
 * Superior to 2wai: includes skill trees, streaks, and achievements
 */

import React, { useState, useEffect } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import './ProgressDashboard.scss';

interface SkillProgress {
  skill_id: string;
  name: string;
  proficiency: number;
  practice_count: number;
  last_practiced: string;
  streak: number;
}

interface DashboardStats {
  total_questions: number;
  correct_answers: number;
  current_streak: number;
  longest_streak: number;
  time_spent_minutes: number;
  skills_mastered: number;
  skills_in_progress: number;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  progress?: number;
  maxProgress?: number;
}

const DASH_API_URL = process.env.REACT_APP_DASH_API_URL || 'http://localhost:8000';

const ProgressDashboard: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  const { currentAvatar } = useAvatarContext();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [skills, setSkills] = useState<SkillProgress[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'achievements'>('overview');

  // Sample achievements (would come from API in production)
  const sampleAchievements: Achievement[] = [
    { id: 'first_lesson', name: 'First Steps', description: 'Complete your first lesson', icon: 'school', unlocked: true },
    { id: 'streak_7', name: 'Week Warrior', description: 'Maintain a 7-day streak', icon: 'local_fire_department', unlocked: false, progress: 3, maxProgress: 7 },
    { id: 'perfect_10', name: 'Perfect 10', description: 'Answer 10 questions correctly in a row', icon: 'stars', unlocked: false, progress: 6, maxProgress: 10 },
    { id: 'explorer', name: 'Explorer', description: 'Learn from 5 different tutors', icon: 'explore', unlocked: false, progress: 1, maxProgress: 5 },
    { id: 'night_owl', name: 'Night Owl', description: 'Study after 10 PM', icon: 'nightlight', unlocked: true },
    { id: 'speed_demon', name: 'Speed Demon', description: 'Answer correctly in under 5 seconds', icon: 'bolt', unlocked: false },
  ];

  useEffect(() => {
    if (!isOpen) return;

    const fetchProgress = async () => {
      setLoading(true);
      try {
        // Fetch user stats
        const statsResponse = await fetch(`${DASH_API_URL}/user/1/stats`);
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          setStats(statsData);
        } else {
          // Use sample data if API not available
          setStats({
            total_questions: 47,
            correct_answers: 38,
            current_streak: 3,
            longest_streak: 12,
            time_spent_minutes: 156,
            skills_mastered: 5,
            skills_in_progress: 8,
          });
        }

        // Fetch skills progress
        const skillsResponse = await fetch(`${DASH_API_URL}/user/1/skills`);
        if (skillsResponse.ok) {
          const skillsData = await skillsResponse.json();
          setSkills(skillsData.skills || []);
        } else {
          // Sample skills data
          setSkills([
            { skill_id: '1', name: 'Basic Addition', proficiency: 0.95, practice_count: 25, last_practiced: '2024-01-15', streak: 5 },
            { skill_id: '2', name: 'Multiplication', proficiency: 0.78, practice_count: 18, last_practiced: '2024-01-14', streak: 3 },
            { skill_id: '3', name: 'Fractions', proficiency: 0.45, practice_count: 8, last_practiced: '2024-01-13', streak: 1 },
            { skill_id: '4', name: 'Algebra Basics', proficiency: 0.32, practice_count: 5, last_practiced: '2024-01-12', streak: 0 },
            { skill_id: '5', name: 'Geometry', proficiency: 0.15, practice_count: 2, last_practiced: '2024-01-10', streak: 0 },
          ]);
        }

        setAchievements(sampleAchievements);
      } catch (error) {
        console.error('Failed to fetch progress:', error);
        // Use sample data on error
        setStats({
          total_questions: 47,
          correct_answers: 38,
          current_streak: 3,
          longest_streak: 12,
          time_spent_minutes: 156,
          skills_mastered: 5,
          skills_in_progress: 8,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [isOpen]);

  if (!isOpen) return null;

  const accuracy = stats ? Math.round((stats.correct_answers / stats.total_questions) * 100) : 0;

  return (
    <div className="progress-dashboard-overlay" onClick={onClose}>
      <div className="progress-dashboard" onClick={(e) => e.stopPropagation()}>
        <div className="dashboard-header">
          <h2>
            <span className="material-symbols-outlined">insights</span>
            Your Progress
          </h2>
          <button className="close-button" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="dashboard-tabs">
          <button
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            <span className="material-symbols-outlined">dashboard</span>
            Overview
          </button>
          <button
            className={activeTab === 'skills' ? 'active' : ''}
            onClick={() => setActiveTab('skills')}
          >
            <span className="material-symbols-outlined">psychology</span>
            Skills
          </button>
          <button
            className={activeTab === 'achievements' ? 'active' : ''}
            onClick={() => setActiveTab('achievements')}
          >
            <span className="material-symbols-outlined">emoji_events</span>
            Achievements
          </button>
        </div>

        {loading ? (
          <div className="loading-state">
            <span className="material-symbols-outlined spinning">sync</span>
            <p>Loading your progress...</p>
          </div>
        ) : (
          <div className="dashboard-content">
            {activeTab === 'overview' && stats && (
              <div className="overview-tab">
                <div className="stats-grid">
                  <div className="stat-card primary">
                    <span className="material-symbols-outlined">local_fire_department</span>
                    <div className="stat-value">{stats.current_streak}</div>
                    <div className="stat-label">Day Streak</div>
                  </div>
                  <div className="stat-card">
                    <span className="material-symbols-outlined">check_circle</span>
                    <div className="stat-value">{accuracy}%</div>
                    <div className="stat-label">Accuracy</div>
                  </div>
                  <div className="stat-card">
                    <span className="material-symbols-outlined">quiz</span>
                    <div className="stat-value">{stats.total_questions}</div>
                    <div className="stat-label">Questions</div>
                  </div>
                  <div className="stat-card">
                    <span className="material-symbols-outlined">schedule</span>
                    <div className="stat-value">{Math.round(stats.time_spent_minutes / 60)}h</div>
                    <div className="stat-label">Time Spent</div>
                  </div>
                </div>

                <div className="mastery-section">
                  <h3>Skill Mastery</h3>
                  <div className="mastery-bars">
                    <div className="mastery-item">
                      <span>Mastered</span>
                      <div className="mastery-bar">
                        <div
                          className="mastery-fill mastered"
                          style={{ width: `${(stats.skills_mastered / (stats.skills_mastered + stats.skills_in_progress)) * 100}%` }}
                        />
                      </div>
                      <span className="mastery-count">{stats.skills_mastered}</span>
                    </div>
                    <div className="mastery-item">
                      <span>In Progress</span>
                      <div className="mastery-bar">
                        <div
                          className="mastery-fill in-progress"
                          style={{ width: `${(stats.skills_in_progress / (stats.skills_mastered + stats.skills_in_progress)) * 100}%` }}
                        />
                      </div>
                      <span className="mastery-count">{stats.skills_in_progress}</span>
                    </div>
                  </div>
                </div>

                {currentAvatar && (
                  <div className="tutor-message">
                    <div className="tutor-avatar">
                      {currentAvatar.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <p>
                      "{stats.current_streak >= 3
                        ? `Excellent dedication! ${stats.current_streak} days of learning shows real commitment.`
                        : `Keep going! Build your streak to unlock greater understanding.`}"
                      <span className="tutor-name">— {currentAvatar.name}</span>
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'skills' && (
              <div className="skills-tab">
                <div className="skills-list">
                  {skills.map((skill) => (
                    <div key={skill.skill_id} className="skill-item">
                      <div className="skill-info">
                        <h4>{skill.name}</h4>
                        <div className="skill-meta">
                          <span>{skill.practice_count} practices</span>
                          {skill.streak > 0 && (
                            <span className="streak-badge">
                              <span className="material-symbols-outlined">local_fire_department</span>
                              {skill.streak}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="skill-progress">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${skill.proficiency * 100}%` }}
                          />
                        </div>
                        <span className="progress-percent">{Math.round(skill.proficiency * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'achievements' && (
              <div className="achievements-tab">
                <div className="achievements-grid">
                  {achievements.map((achievement) => (
                    <div
                      key={achievement.id}
                      className={`achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}`}
                    >
                      <div className="achievement-icon">
                        <span className="material-symbols-outlined">{achievement.icon}</span>
                      </div>
                      <div className="achievement-info">
                        <h4>{achievement.name}</h4>
                        <p>{achievement.description}</p>
                        {!achievement.unlocked && achievement.progress !== undefined && (
                          <div className="achievement-progress">
                            <div className="progress-bar">
                              <div
                                className="progress-fill"
                                style={{ width: `${(achievement.progress / (achievement.maxProgress || 1)) * 100}%` }}
                              />
                            </div>
                            <span>{achievement.progress}/{achievement.maxProgress}</span>
                          </div>
                        )}
                      </div>
                      {achievement.unlocked && (
                        <span className="unlocked-badge">
                          <span className="material-symbols-outlined">verified</span>
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressDashboard;
