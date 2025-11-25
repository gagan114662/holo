/**
 * AvatarSelector Component
 * Allows users to select from historical figure avatars
 */

import React, { useEffect, useState } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { HistoricalFigure } from './types';
import './AvatarSelector.scss';

interface AvatarSelectorProps {
  onSelect?: (avatar: HistoricalFigure) => void;
  filterSubject?: string;
  className?: string;
}

const AVATAR_SERVICE_URL = process.env.REACT_APP_AVATAR_SERVICE_URL || 'http://localhost:8001';

// Subject icons mapping
const SUBJECT_ICONS: Record<string, string> = {
  physics: 'science',
  chemistry: 'science',
  biology: 'biotech',
  mathematics: 'calculate',
  computer_science: 'code',
  literature: 'menu_book',
  philosophy: 'psychology',
  art: 'palette',
  history: 'history_edu',
  writing: 'edit_note',
  default: 'school',
};

// Era colors for visual distinction
const ERA_COLORS: Record<string, string> = {
  Ancient: '#8B4513',
  '16th-17th Century': '#4A5568',
  '19th Century': '#2C5282',
  '19th-20th Century': '#553C9A',
  '20th Century': '#2F855A',
  default: '#718096',
};

const AvatarSelector: React.FC<AvatarSelectorProps> = ({
  onSelect,
  filterSubject,
  className = '',
}) => {
  const { selectAvatar, currentAvatar, state } = useAvatarContext();
  const [avatars, setAvatars] = useState<HistoricalFigure[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string | null>(filterSubject || null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch available avatars
  useEffect(() => {
    const fetchAvatars = async () => {
      try {
        setLoading(true);
        const endpoint = selectedSubject
          ? `${AVATAR_SERVICE_URL}/avatars/by-subject/${selectedSubject}`
          : `${AVATAR_SERVICE_URL}/avatars/historical`;

        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error('Failed to fetch avatars');
        }
        const data = await response.json();
        setAvatars(data.avatars);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load avatars');
      } finally {
        setLoading(false);
      }
    };

    fetchAvatars();
  }, [selectedSubject]);

  // Get unique subjects from avatars
  const allSubjects = React.useMemo(() => {
    const subjects = new Set<string>();
    avatars.forEach((avatar) => {
      avatar.subjects?.forEach((s) => subjects.add(s));
    });
    return Array.from(subjects).sort();
  }, [avatars]);

  // Filter avatars based on search
  const filteredAvatars = React.useMemo(() => {
    if (!searchQuery) return avatars;
    const query = searchQuery.toLowerCase();
    return avatars.filter(
      (avatar) =>
        avatar.name.toLowerCase().includes(query) ||
        avatar.subject.toLowerCase().includes(query) ||
        avatar.era.toLowerCase().includes(query)
    );
  }, [avatars, searchQuery]);

  const handleSelectAvatar = async (avatar: HistoricalFigure) => {
    await selectAvatar(avatar.id);
    onSelect?.(avatar);
  };

  const getSubjectIcon = (subject: string) => {
    return SUBJECT_ICONS[subject] || SUBJECT_ICONS.default;
  };

  const getEraColor = (era: string) => {
    return ERA_COLORS[era] || ERA_COLORS.default;
  };

  if (loading) {
    return (
      <div className={`avatar-selector ${className} loading`}>
        <div className="loading-spinner">
          <span className="material-symbols-outlined spinning">sync</span>
          <p>Loading tutors...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`avatar-selector ${className} error`}>
        <span className="material-symbols-outlined">error</span>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className={`avatar-selector ${className}`}>
      <div className="selector-header">
        <h2>Choose Your Tutor</h2>
        <p>Learn from history's greatest minds</p>
      </div>

      <div className="selector-controls">
        {/* Search */}
        <div className="search-box">
          <span className="material-symbols-outlined">search</span>
          <input
            type="text"
            placeholder="Search tutors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              className="clear-search"
              onClick={() => setSearchQuery('')}
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          )}
        </div>

        {/* Subject filter */}
        <div className="subject-filters">
          <button
            className={`filter-chip ${!selectedSubject ? 'active' : ''}`}
            onClick={() => setSelectedSubject(null)}
          >
            All Subjects
          </button>
          {['physics', 'mathematics', 'literature', 'biology', 'philosophy', 'art', 'computer_science'].map(
            (subject) => (
              <button
                key={subject}
                className={`filter-chip ${selectedSubject === subject ? 'active' : ''}`}
                onClick={() => setSelectedSubject(subject)}
              >
                <span className="material-symbols-outlined">
                  {getSubjectIcon(subject)}
                </span>
                {subject.replace('_', ' ')}
              </button>
            )
          )}
        </div>
      </div>

      <div className="avatars-grid">
        {filteredAvatars.map((avatar) => (
          <div
            key={avatar.id}
            className={`avatar-card ${currentAvatar?.id === avatar.id ? 'selected' : ''}`}
            onClick={() => handleSelectAvatar(avatar)}
          >
            <div className="avatar-image">
              {avatar.image && avatar.image.startsWith('http') ? (
                <img
                  src={avatar.image}
                  alt={avatar.name}
                  className="avatar-portrait"
                  onError={(e) => {
                    // Fallback to initials if image fails to load
                    (e.target as HTMLImageElement).style.display = 'none';
                    (e.target as HTMLImageElement).parentElement?.querySelector('.avatar-fallback')?.classList.remove('hidden');
                  }}
                />
              ) : null}
              <div
                className={`avatar-fallback ${avatar.image?.startsWith('http') ? 'hidden' : ''}`}
                style={{ backgroundColor: getEraColor(avatar.era) }}
              >
                <span className="initials">
                  {avatar.name
                    .split(' ')
                    .map((n) => n[0])
                    .join('')}
                </span>
              </div>
              <div className="era-badge" style={{ backgroundColor: getEraColor(avatar.era) }}>
                {avatar.era}
              </div>
            </div>

            <div className="avatar-details">
              <h3 className="avatar-name">{avatar.name}</h3>

              <div className="avatar-subjects">
                {avatar.subjects?.slice(0, 3).map((subject) => (
                  <span key={subject} className="subject-tag">
                    <span className="material-symbols-outlined">
                      {getSubjectIcon(subject)}
                    </span>
                    {subject.replace('_', ' ')}
                  </span>
                ))}
              </div>

              <p className="avatar-greeting">"{avatar.greeting?.slice(0, 80)}..."</p>
            </div>

            <div className="avatar-actions">
              <button
                className="select-button"
                disabled={state.isLoading}
              >
                {state.isLoading && currentAvatar?.id === avatar.id ? (
                  <>
                    <span className="material-symbols-outlined spinning">sync</span>
                    Loading...
                  </>
                ) : currentAvatar?.id === avatar.id ? (
                  <>
                    <span className="material-symbols-outlined">check_circle</span>
                    Selected
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined">play_circle</span>
                    Start Learning
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredAvatars.length === 0 && (
        <div className="no-results">
          <span className="material-symbols-outlined">search_off</span>
          <p>No tutors found matching your criteria</p>
          <button onClick={() => { setSearchQuery(''); setSelectedSubject(null); }}>
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
};

export default AvatarSelector;
