/**
 * Avatar Selector Component
 * Character selection UI for HoloAvatar
 */
import React, { useState } from 'react';
import './holoavatar.scss';

interface Character {
  id: string;
  name: string;
  description: string;
  subjects?: string[];
  image?: string;
}

interface AvatarSelectorProps {
  characters: Character[];
  selectedId: string | null;
  onSelect: (characterId: string) => void;
  onClose?: () => void;
}

export const AvatarSelector: React.FC<AvatarSelectorProps> = ({
  characters,
  selectedId,
  onSelect,
  onClose
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Default characters if none provided
  const defaultCharacters: Character[] = [
    {
      id: 'teacher',
      name: 'Friendly Teacher',
      description: 'Warm and encouraging teacher',
      subjects: ['all'],
    },
    {
      id: 'einstein',
      name: 'Albert Einstein',
      description: 'Physics and math genius',
      subjects: ['physics', 'mathematics'],
    },
    {
      id: 'curie',
      name: 'Marie Curie',
      description: 'Science pioneer',
      subjects: ['chemistry', 'physics'],
    },
    {
      id: 'lovelace',
      name: 'Ada Lovelace',
      description: 'Computing pioneer',
      subjects: ['computer science', 'mathematics'],
    },
  ];

  const displayCharacters = characters.length > 0 ? characters : defaultCharacters;

  return (
    <div className="avatar-selector-overlay">
      <div className="avatar-selector-modal">
        <div className="selector-header">
          <h2>Choose Your Tutor</h2>
          {onClose && (
            <button className="close-btn" onClick={onClose}>×</button>
          )}
        </div>

        <div className="character-selector">
          {displayCharacters.map(char => (
            <div
              key={char.id}
              className={`character-card ${selectedId === char.id ? 'selected' : ''}`}
              onClick={() => onSelect(char.id)}
              onMouseEnter={() => setHoveredId(char.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <div
                className="character-avatar"
                style={{
                  backgroundImage: char.image ? `url(${char.image})` : undefined,
                  backgroundColor: !char.image ? getAvatarColor(char.id) : undefined
                }}
              >
                {!char.image && (
                  <span className="avatar-initial">
                    {char.name.charAt(0)}
                  </span>
                )}
              </div>

              <div className="character-name">{char.name}</div>
              <div className="character-description">{char.description}</div>

              {char.subjects && char.subjects.length > 0 && (
                <div className="character-subjects">
                  {char.subjects.slice(0, 3).map(subject => (
                    <span key={subject} className="subject-tag">
                      {subject}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {hoveredId && (
          <div className="character-preview">
            <p>
              {displayCharacters.find(c => c.id === hoveredId)?.description}
            </p>
          </div>
        )}
      </div>

      <style>{`
        .avatar-selector-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .avatar-selector-modal {
          background: var(--Neutral-15, #1a1a1a);
          border-radius: 12px;
          max-width: 600px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .selector-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--Neutral-30, #333);

          h2 {
            margin: 0;
            font-size: 18px;
            color: var(--Neutral-90, #fff);
          }

          .close-btn {
            background: none;
            border: none;
            color: var(--Neutral-60, #888);
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            line-height: 1;

            &:hover {
              color: var(--Neutral-90, #fff);
            }
          }
        }

        .character-avatar {
          display: flex;
          align-items: center;
          justify-content: center;
          background-size: cover;
          background-position: center;

          .avatar-initial {
            font-size: 32px;
            font-weight: bold;
            color: rgba(255, 255, 255, 0.8);
          }
        }

        .character-subjects {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-top: 8px;
          justify-content: center;

          .subject-tag {
            font-size: 9px;
            padding: 2px 6px;
            background: var(--Neutral-30, #333);
            border-radius: 10px;
            color: var(--Neutral-70, #aaa);
            text-transform: capitalize;
          }
        }

        .character-preview {
          padding: 12px 20px;
          border-top: 1px solid var(--Neutral-30, #333);

          p {
            margin: 0;
            font-size: 12px;
            color: var(--Neutral-60, #888);
            font-style: italic;
          }
        }
      `}</style>
    </div>
  );
};

// Helper to generate consistent colors for avatars
function getAvatarColor(id: string): string {
  const colors = [
    '#3b82f6', // blue
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#f59e0b', // amber
    '#10b981', // emerald
    '#6366f1', // indigo
  ];

  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }

  return colors[Math.abs(hash) % colors.length];
}

export default AvatarSelector;
