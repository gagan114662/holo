/**
 * QuestionDisplay Component
 * Displays adaptive questions with avatar voice support
 * Falls back to curated questions when API unavailable
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { storageService } from '../../services/StorageService';
import './question-display.scss';

interface Question {
  question_id: string;
  skill_ids: string[];
  content: string;
  difficulty: number;
  subject: string;
  type: 'multiple_choice' | 'free_text' | 'math';
  options?: string[];
  correctAnswer?: string;
  hint?: string;
}

// Offline fallback questions - used when backend API is unavailable
const OFFLINE_FALLBACK_QUESTIONS: Record<string, Question[]> = {
  physics: [
    { question_id: 'p1', skill_ids: ['motion'], content: 'If a car travels 100 km in 2 hours, what is its average speed?', difficulty: 1, subject: 'physics', type: 'free_text', correctAnswer: '50 km/h', hint: 'Speed = Distance / Time' },
    { question_id: 'p2', skill_ids: ['motion'], content: 'What is Newton\'s First Law of Motion?', difficulty: 2, subject: 'physics', type: 'free_text', hint: 'Think about what happens to an object when no forces act on it' },
    { question_id: 'p3', skill_ids: ['energy'], content: 'A 2 kg ball is lifted 5 meters. Calculate its potential energy (g = 10 m/s²)', difficulty: 2, subject: 'physics', type: 'free_text', correctAnswer: '100 J', hint: 'PE = mgh' },
  ],
  mathematics: [
    { question_id: 'm1', skill_ids: ['algebra'], content: 'Solve for x: 2x + 5 = 13', difficulty: 1, subject: 'mathematics', type: 'free_text', correctAnswer: '4', hint: 'Isolate x by subtracting 5 from both sides, then divide' },
    { question_id: 'm2', skill_ids: ['algebra'], content: 'What is the quadratic formula?', difficulty: 2, subject: 'mathematics', type: 'free_text', hint: 'x = (-b ± √(b²-4ac)) / 2a' },
    { question_id: 'm3', skill_ids: ['geometry'], content: 'Calculate the area of a circle with radius 7 cm (use π = 3.14)', difficulty: 2, subject: 'mathematics', type: 'free_text', correctAnswer: '153.86 cm²', hint: 'Area = πr²' },
  ],
  literature: [
    { question_id: 'l1', skill_ids: ['poetry'], content: 'What is a sonnet?', difficulty: 1, subject: 'literature', type: 'free_text', hint: 'A 14-line poem with a specific rhyme scheme' },
    { question_id: 'l2', skill_ids: ['drama'], content: 'In Shakespeare\'s Hamlet, what is the famous opening line of the "To be or not to be" soliloquy about?', difficulty: 2, subject: 'literature', type: 'free_text', hint: 'It contemplates existence and mortality' },
    { question_id: 'l3', skill_ids: ['rhetoric'], content: 'What is the difference between a metaphor and a simile?', difficulty: 1, subject: 'literature', type: 'free_text', hint: 'One uses "like" or "as", the other does not' },
  ],
  biology: [
    { question_id: 'b1', skill_ids: ['cells'], content: 'What is the powerhouse of the cell?', difficulty: 1, subject: 'biology', type: 'free_text', correctAnswer: 'mitochondria', hint: 'It produces ATP' },
    { question_id: 'b2', skill_ids: ['genetics'], content: 'What does DNA stand for?', difficulty: 1, subject: 'biology', type: 'free_text', correctAnswer: 'Deoxyribonucleic acid', hint: 'It contains the genetic code' },
    { question_id: 'b3', skill_ids: ['evolution'], content: 'Who proposed the theory of natural selection?', difficulty: 1, subject: 'biology', type: 'free_text', correctAnswer: 'Charles Darwin', hint: 'He wrote "On the Origin of Species"' },
  ],
  philosophy: [
    { question_id: 'ph1', skill_ids: ['ethics'], content: 'What is the Socratic method?', difficulty: 2, subject: 'philosophy', type: 'free_text', hint: 'A form of cooperative argumentative dialogue' },
    { question_id: 'ph2', skill_ids: ['logic'], content: 'What is the difference between deductive and inductive reasoning?', difficulty: 2, subject: 'philosophy', type: 'free_text', hint: 'One goes from general to specific, the other from specific to general' },
    { question_id: 'ph3', skill_ids: ['ethics'], content: 'Explain the trolley problem and its ethical implications.', difficulty: 3, subject: 'philosophy', type: 'free_text', hint: 'A thought experiment about utilitarian vs deontological ethics' },
  ],
  general: [
    { question_id: 'g1', skill_ids: ['critical_thinking'], content: 'What makes a good argument?', difficulty: 2, subject: 'general', type: 'free_text', hint: 'Consider evidence, logic, and clear premises' },
    { question_id: 'g2', skill_ids: ['research'], content: 'How can you evaluate if a source is reliable?', difficulty: 2, subject: 'general', type: 'free_text', hint: 'Check credentials, citations, bias, and peer review' },
    { question_id: 'g3', skill_ids: ['learning'], content: 'What is the most effective study technique according to research?', difficulty: 2, subject: 'general', type: 'free_text', hint: 'Active recall and spaced repetition are highly effective' },
  ],
};

interface QuestionDisplayProps {
  onQuestionLoaded?: (question: Question) => void;
}

const QuestionDisplay: React.FC<QuestionDisplayProps> = ({ onQuestionLoaded }) => {
  const [question, setQuestion] = useState<Question | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const { currentAvatar } = useAvatarContext();

  // Get current subject from session or avatar
  const getCurrentSubject = useCallback(() => {
    const session = storageService.getCurrentSession();
    if (session?.subject) return session.subject;
    if (currentAvatar?.subject) return currentAvatar.subject;
    return 'general';
  }, [currentAvatar]);

  // Make avatar speak the question
  const speakQuestion = useCallback((text: string) => {
    window.dispatchEvent(new CustomEvent('avatar-speak', {
      detail: { text, emotion: 'neutral' }
    }));
  }, []);

  // Fetch or generate question
  const fetchQuestion = useCallback(async () => {
    try {
      setLoading(true);
      setShowHint(false);

      const subject = getCurrentSubject();
      const progress = storageService.getUserProgress();

      // Try backend API first
      const API_URL = process.env.REACT_APP_DASH_API_URL || 'http://localhost:8000/api';
      try {
        const response = await fetch(`${API_URL}/questions/next?subject_id=${subject}`, {
          signal: AbortSignal.timeout(3000), // 3 second timeout
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
          const apiData = await response.json();
          // Map API response to local Question interface
          const data: Question = {
            question_id: apiData.id,
            skill_ids: apiData.skill_id ? [apiData.skill_id] : [],
            content: apiData.question_text,
            difficulty: apiData.difficulty === 'easy' ? 1 : apiData.difficulty === 'medium' ? 2 : 3,
            subject: apiData.subject_name || subject,
            type: apiData.question_type || 'free_text',
            options: apiData.options,
            hint: apiData.hints?.[0],
          };
          setQuestion(data);
          setError(null);
          onQuestionLoaded?.(data);

          // Avatar speaks the question
          const intro = questionIndex === 0
            ? `Let's begin! Here's your question: ${data.content}`
            : `Next question: ${data.content}`;
          speakQuestion(intro);
          return;
        }
      } catch {
        // API not available, use offline fallback questions
      }

      // Offline fallback - use curated questions when API unavailable
      const subjectQuestions = OFFLINE_FALLBACK_QUESTIONS[subject] || OFFLINE_FALLBACK_QUESTIONS.general;

      // Select based on difficulty progression
      const answeredCount = progress.totalQuestionsAnswered;
      const difficultyLevel = Math.min(3, 1 + Math.floor(answeredCount / 3));

      // Filter by appropriate difficulty
      const appropriateQuestions = subjectQuestions.filter(q => q.difficulty <= difficultyLevel);
      const selectedQuestion = appropriateQuestions[questionIndex % appropriateQuestions.length] || subjectQuestions[0];

      setQuestion(selectedQuestion);
      setError(null);
      onQuestionLoaded?.(selectedQuestion);

      // Avatar speaks the question with personality
      const greetings = [
        `Here's a question for you: ${selectedQuestion.content}`,
        `Let's try this one: ${selectedQuestion.content}`,
        `Consider this: ${selectedQuestion.content}`,
        `Think about this: ${selectedQuestion.content}`,
      ];
      const intro = questionIndex === 0
        ? `Welcome! Let's start learning. ${selectedQuestion.content}`
        : greetings[Math.floor(Math.random() * greetings.length)];

      speakQuestion(intro);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load question');
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  }, [getCurrentSubject, questionIndex, onQuestionLoaded, speakQuestion]);

  // Load first question on mount
  useEffect(() => {
    fetchQuestion();
  }, []); // Only on mount

  // Reload when subject changes
  useEffect(() => {
    if (currentAvatar) {
      setQuestionIndex(0);
      fetchQuestion();
    }
  }, [currentAvatar?.id]);

  const handleNextQuestion = () => {
    setQuestionIndex(prev => prev + 1);
    fetchQuestion();
  };

  const handleShowHint = () => {
    setShowHint(true);
    if (question?.hint) {
      speakQuestion(`Here's a hint: ${question.hint}`);
    }
  };

  if (loading) {
    return (
      <div className="question-display loading">
        <span className="material-symbols-outlined spinning">sync</span>
        <p>Preparing your question...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="question-display error">
        <span className="material-symbols-outlined">error</span>
        <p>Error: {error}</p>
        <button onClick={fetchQuestion}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="question-display">
      <div className="question-header">
        <div className="question-meta">
          {question?.subject && (
            <span className="subject-badge">{question.subject}</span>
          )}
          <span className="difficulty-badge">
            {'⭐'.repeat(question?.difficulty || 1)}
          </span>
        </div>
        <div className="question-actions">
          <button
            className="hint-button"
            onClick={handleShowHint}
            disabled={!question?.hint || showHint}
            title="Get a hint"
          >
            <span className="material-symbols-outlined">lightbulb</span>
          </button>
          <button
            className="skip-button"
            onClick={handleNextQuestion}
            title="Skip question"
          >
            <span className="material-symbols-outlined">skip_next</span>
          </button>
        </div>
      </div>

      <div className="question-content">
        <h2 className="question-title">Question</h2>
        {question && <p className="question-text">{question.content}</p>}
      </div>

      {showHint && question?.hint && (
        <div className="hint-box">
          <span className="material-symbols-outlined">lightbulb</span>
          <p>{question.hint}</p>
        </div>
      )}
    </div>
  );
};

export default QuestionDisplay;
