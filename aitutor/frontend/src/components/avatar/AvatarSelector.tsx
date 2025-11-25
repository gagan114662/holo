/**
 * AvatarSelector Component
 * Allows users to select from historical figure avatars
 * Includes built-in fallback data when API is unavailable
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

// Built-in avatars with real Wikipedia Commons images for offline/demo use
const BUILT_IN_AVATARS: HistoricalFigure[] = [
  {
    id: 'einstein',
    name: 'Albert Einstein',
    subject: 'physics',
    era: '20th Century',
    subjects: ['physics', 'mathematics'],
    greeting: "Imagination is more important than knowledge. Let's explore the wonders of the universe together!",
    personality: 'Curious, playful, and encouraging. Uses thought experiments and analogies.',
    voice_id: 'en-US-GuyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/440px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg',
  },
  {
    id: 'curie',
    name: 'Marie Curie',
    subject: 'chemistry',
    era: '19th-20th Century',
    subjects: ['chemistry', 'physics'],
    greeting: "Nothing in life is to be feared, it is only to be understood. Let's discover science together!",
    personality: 'Determined, precise, and inspiring. Encourages scientific rigor.',
    voice_id: 'en-US-JennyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/440px-Marie_Curie_c._1920s.jpg',
  },
  {
    id: 'shakespeare',
    name: 'William Shakespeare',
    subject: 'literature',
    era: '16th-17th Century',
    subjects: ['literature', 'writing', 'history'],
    greeting: "All the world's a stage, and all the men and women merely players. Let us write our story together!",
    personality: 'Eloquent, dramatic, and witty. Uses metaphors and storytelling.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/440px-Shakespeare.jpg',
  },
  {
    id: 'hypatia',
    name: 'Hypatia of Alexandria',
    subject: 'mathematics',
    era: 'Ancient',
    subjects: ['mathematics', 'philosophy', 'astronomy'],
    greeting: 'Reserve your right to think, for even to think wrongly is better than not to think at all.',
    personality: 'Wise, patient, and philosophical. Encourages logical thinking.',
    voice_id: 'en-US-AriaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Hypatia_portrait.png/440px-Hypatia_portrait.png',
  },
  {
    id: 'darwin',
    name: 'Charles Darwin',
    subject: 'biology',
    era: '19th Century',
    subjects: ['biology', 'science'],
    greeting: 'In the long history of humankind, those who learned to collaborate most effectively have prevailed.',
    personality: 'Observant, methodical, and gentle. Encourages natural curiosity.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Charles_Darwin_seated_crop.jpg/440px-Charles_Darwin_seated_crop.jpg',
  },
  {
    id: 'ada',
    name: 'Ada Lovelace',
    subject: 'computer_science',
    era: '19th Century',
    subjects: ['computer_science', 'mathematics'],
    greeting: 'The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves.',
    personality: 'Visionary, analytical, and poetic. Bridges math and imagination.',
    voice_id: 'en-GB-SoniaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Ada_Lovelace_portrait.jpg/440px-Ada_Lovelace_portrait.jpg',
  },
  {
    id: 'socrates',
    name: 'Socrates',
    subject: 'philosophy',
    era: 'Ancient',
    subjects: ['philosophy', 'ethics'],
    greeting: 'The only true wisdom is in knowing you know nothing. Let us question everything together.',
    personality: 'Questioning, humble, and challenging. Uses Socratic method.',
    voice_id: 'en-US-GuyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Socrate_du_Louvre.jpg/440px-Socrate_du_Louvre.jpg',
  },
  {
    id: 'frida',
    name: 'Frida Kahlo',
    subject: 'art',
    era: '20th Century',
    subjects: ['art', 'history'],
    greeting: 'I paint myself because I am so often alone and because I am the subject I know best.',
    personality: 'Passionate, honest, and expressive. Encourages self-expression.',
    voice_id: 'es-MX-DaliaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg/440px-Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg',
  },
];

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
  const [selectedSubject, setSelectedSubject] = useState<string | null>(filterSubject || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [usingFallback, setUsingFallback] = useState(false);

  // Fetch available avatars with fallback
  useEffect(() => {
    const fetchAvatars = async () => {
      try {
        setLoading(true);
        const endpoint = selectedSubject
          ? `${AVATAR_SERVICE_URL}/avatars/by-subject/${selectedSubject}`
          : `${AVATAR_SERVICE_URL}/avatars/historical`;

        // Use AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);

        const response = await fetch(endpoint, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error('Failed to fetch avatars');
        }
        const data = await response.json();
        setAvatars(data.avatars);
        setUsingFallback(false);
      } catch (err) {
        // Use built-in avatars as fallback
        console.log('Using built-in avatars (API unavailable)');
        let fallbackAvatars = BUILT_IN_AVATARS;
        if (selectedSubject) {
          fallbackAvatars = BUILT_IN_AVATARS.filter(
            (a) => a.subject === selectedSubject || a.subjects?.includes(selectedSubject)
          );
        }
        setAvatars(fallbackAvatars);
        setUsingFallback(true);
      } finally {
        setLoading(false);
      }
    };

    fetchAvatars();
  }, [selectedSubject]);

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
    try {
      await selectAvatar(avatar.id);
    } catch {
      // If selectAvatar fails (API down), manually set the avatar via context workaround
      console.log('Direct avatar selection');
    }
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

  return (
    <div className={`avatar-selector ${className}`}>
      <div className="selector-header">
        <h2>Choose Your Tutor</h2>
        <p>Learn from history's greatest minds</p>
        {usingFallback && (
          <span className="offline-badge">
            <span className="material-symbols-outlined">cloud_off</span>
            Offline Mode
          </span>
        )}
      </div>

      <div className="selector-controls" role="search">
        {/* Search */}
        <div className="search-box">
          <span className="material-symbols-outlined" aria-hidden="true">search</span>
          <input
            type="text"
            placeholder="Search tutors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search for tutors"
          />
          {searchQuery && (
            <button
              className="clear-search"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          )}
        </div>

        {/* Subject filter */}
        <div className="subject-filters" role="group" aria-label="Filter by subject">
          <button
            className={`filter-chip ${!selectedSubject ? 'active' : ''}`}
            onClick={() => setSelectedSubject(null)}
            aria-pressed={!selectedSubject}
          >
            All Subjects
          </button>
          {['physics', 'mathematics', 'literature', 'biology', 'philosophy', 'art', 'computer_science'].map(
            (subject) => (
              <button
                key={subject}
                className={`filter-chip ${selectedSubject === subject ? 'active' : ''}`}
                onClick={() => setSelectedSubject(subject)}
                aria-pressed={selectedSubject === subject}
              >
                <span className="material-symbols-outlined" aria-hidden="true">
                  {getSubjectIcon(subject)}
                </span>
                {subject.replace('_', ' ')}
              </button>
            )
          )}
        </div>
      </div>

      <div className="avatars-grid" role="list" aria-label="Available tutors">
        {filteredAvatars.map((avatar) => (
          <div
            key={avatar.id}
            className={`avatar-card ${currentAvatar?.id === avatar.id ? 'selected' : ''}`}
            onClick={() => handleSelectAvatar(avatar)}
            role="listitem"
            tabIndex={0}
            onKeyPress={(e) => e.key === 'Enter' && handleSelectAvatar(avatar)}
            aria-selected={currentAvatar?.id === avatar.id}
            aria-label={`Select ${avatar.name} as tutor`}
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
