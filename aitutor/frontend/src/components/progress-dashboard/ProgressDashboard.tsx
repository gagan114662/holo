/**
 * ProgressDashboard Component
 * Shows student learning progress with visual analytics
 * Uses real data from StorageService
 */

import React, { useState, useEffect } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { storageService, UserProgress, SkillProgress as StoredSkill, Achievement as StoredAchievement } from '../../services/StorageService';
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
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
}

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

  // Load progress data from storage
  useEffect(() => {
    if (!isOpen) return;

    const loadProgress = () => {
      setLoading(true);
      try {
        // Get real user progress from localStorage
        const progress = storageService.getUserProgress();

        // Calculate stats from real data
        const skillValues = Object.values(progress.skills);
        const skillsMastered = skillValues.filter(s => s.level >= 5).length;
        const skillsInProgress = skillValues.filter(s => s.level < 5 && s.level > 0).length;

        // Estimate time spent (3 min average per session)
        const timeSpent = progress.totalSessions * 3;

        setStats({
          total_questions: progress.totalQuestionsAnswered,
          correct_answers: progress.totalCorrectAnswers,
          current_streak: progress.currentStreak,
          longest_streak: progress.longestStreak,
          time_spent_minutes: timeSpent,
          skills_mastered: skillsMastered,
          skills_in_progress: skillsInProgress,
        });

        // Convert stored skills to display format
        const displaySkills: SkillProgress[] = skillValues.map((skill, index) => ({
          skill_id: String(index + 1),
          name: skill.name,
          proficiency: skill.questionsAttempted > 0
            ? skill.questionsCorrect / skill.questionsAttempted
            : 0,
          practice_count: skill.questionsAttempted,
          last_practiced: skill.lastPracticed,
          streak: Math.floor(skill.xp / 50), // Rough streak estimate
        }));
        setSkills(displaySkills);

        // Get achievements - combine unlocked with available
        const allAchievementDefs = storageService.getAchievementDefinitions();
        const unlockedIds = new Set(progress.achievements.map(a => a.id));

        const displayAchievements: Achievement[] = allAchievementDefs.map(def => {
          const unlocked = unlockedIds.has(def.id);
          const storedAchievement = progress.achievements.find(a => a.id === def.id);

          // Calculate progress for locked achievements
          let progressValue: number | undefined;
          let maxProgress: number | undefined;

          if (!unlocked) {
            switch (def.id) {
              case 'five_correct':
                progressValue = Math.min(progress.totalCorrectAnswers, 5);
                maxProgress = 5;
                break;
              case 'ten_sessions':
                progressValue = Math.min(progress.totalSessions, 10);
                maxProgress = 10;
                break;
              case 'streak_3':
                progressValue = Math.min(progress.currentStreak, 3);
                maxProgress = 3;
                break;
              case 'streak_7':
                progressValue = Math.min(progress.currentStreak, 7);
                maxProgress = 7;
                break;
              case 'streak_30':
                progressValue = Math.min(progress.currentStreak, 30);
                maxProgress = 30;
                break;
              case 'multi_subject':
                const subjects = new Set(progress.sessionHistory.map(s => s.subject));
                progressValue = subjects.size;
                maxProgress = 3;
                break;
              case 'all_avatars':
                const avatars = new Set(progress.sessionHistory.map(s => s.avatarId));
                progressValue = avatars.size;
                maxProgress = 8;
                break;
            }
          }

          return {
            id: def.id,
            name: def.name,
            description: def.description,
            icon: def.icon,
            unlocked,
            unlockedAt: storedAchievement?.unlockedAt,
            progress: progressValue,
            maxProgress,
          };
        });

        setAchievements(displayAchievements);
      } catch (error) {
        console.error('Failed to load progress:', error);
        // Set empty defaults on error
        setStats({
          total_questions: 0,
          correct_answers: 0,
          current_streak: 0,
          longest_streak: 0,
          time_spent_minutes: 0,
          skills_mastered: 0,
          skills_in_progress: 0,
        });
        setSkills([]);
        setAchievements([]);
      } finally {
        setLoading(false);
      }
    };

    loadProgress();
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
