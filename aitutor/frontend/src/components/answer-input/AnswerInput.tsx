/**
 * AnswerInput Component
 * Allows students to submit answers with multiple input types
 * Superior to 2wai: supports voice, text, drawing, and multiple choice
 */

import React, { useState, useRef, useCallback } from 'react';
import { useLiveAPIContext } from '../../contexts/LiveAPIContext';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { storageService } from '../../services/StorageService';
import { ttsService } from '../../services/TTSService';
import './AnswerInput.scss';

interface AnswerInputProps {
  questionId?: string;
  questionType?: 'multiple_choice' | 'free_text' | 'numeric' | 'drawing';
  options?: string[];
  skill?: string;
  subject?: string;
  correctAnswer?: string;
  onSubmit?: (answer: string, isCorrect?: boolean) => void;
  disabled?: boolean;
}

const DASH_API_URL = process.env.REACT_APP_DASH_API_URL || 'http://localhost:8000';

const AnswerInput: React.FC<AnswerInputProps> = ({
  questionId,
  questionType = 'free_text',
  options = [],
  skill,
  subject,
  correctAnswer,
  onSubmit,
  disabled = false,
}) => {
  const { client, connected } = useLiveAPIContext();
  const { setEmotion, currentAvatar } = useAvatarContext();

  const [answer, setAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'correct' | 'incorrect' | 'partial'; message: string } | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const speakFeedback = async (text: string) => {
    if (currentAvatar) {
      await ttsService.speakAsAvatar(text, currentAvatar.id);
    }
  };

  const handleSubmit = useCallback(async () => {
    const submittedAnswer = questionType === 'multiple_choice'
      ? (selectedOption !== null ? options[selectedOption] : '')
      : answer;

    if (!submittedAnswer.trim()) return;

    setIsSubmitting(true);
    setFeedback(null);

    let isCorrect = false;

    try {
      // First try to evaluate locally if we have the correct answer
      if (correctAnswer) {
        const normalizedSubmitted = submittedAnswer.toLowerCase().trim();
        const normalizedCorrect = correctAnswer.toLowerCase().trim();
        isCorrect = normalizedSubmitted === normalizedCorrect ||
                   normalizedCorrect.includes(normalizedSubmitted) ||
                   normalizedSubmitted.includes(normalizedCorrect);
      }

      // Try DASH API for evaluation
      try {
        const response = await fetch(`${DASH_API_URL}/submit-answer`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: storageService.getUserProgress().odUserId,
            question_id: questionId,
            answer: submittedAnswer,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          isCorrect = result.correct;

          if (result.correct) {
            setEmotion('happy');
            setFeedback({ type: 'correct', message: result.feedback || 'Excellent work!' });
            speakFeedback("That's correct! Well done!");
          } else if (result.partial) {
            setEmotion('encouraging');
            setFeedback({ type: 'partial', message: result.feedback || 'You\'re on the right track!' });
            speakFeedback("You're getting there! Let me help you.");
          } else {
            setEmotion('encouraging');
            setFeedback({ type: 'incorrect', message: result.feedback || 'Let\'s try again.' });
            speakFeedback("Not quite. Let me explain.");
          }
        }
      } catch {
        // API not available, use local evaluation
        if (isCorrect) {
          setEmotion('happy');
          setFeedback({ type: 'correct', message: 'Great job! That\'s the right answer!' });
          speakFeedback("Excellent! That's correct!");
        } else if (correctAnswer) {
          setEmotion('encouraging');
          setFeedback({ type: 'incorrect', message: `Not quite. The answer was: ${correctAnswer}` });
          speakFeedback("Not quite, but don't worry. Let's learn from this!");
        } else {
          // Send to Gemini for evaluation if available
          if (connected && client) {
            client.send({
              text: `The student answered: "${submittedAnswer}". Please evaluate and provide feedback.`,
            });
          }
          setFeedback({ type: 'partial', message: 'Answer submitted! Let me check that for you.' });
        }
      }

      // Record the answer in storage
      storageService.recordAnswer(isCorrect, skill, subject);

      // Add to conversation history
      storageService.addConversationMessage({
        role: 'user',
        content: submittedAnswer,
        timestamp: new Date().toISOString(),
        questionId,
        wasCorrect: isCorrect,
      });

      onSubmit?.(submittedAnswer, isCorrect);
    } catch (error) {
      console.error('Failed to submit answer:', error);
      onSubmit?.(submittedAnswer);
    } finally {
      setIsSubmitting(false);
      setAnswer('');
      setSelectedOption(null);
    }
  }, [answer, selectedOption, questionType, options, questionId, correctAnswer, skill, subject, connected, client, setEmotion, currentAvatar, onSubmit]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleVoiceInput = async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice input is not supported in this browser');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setAnswer(transcript);
    };

    recognition.start();
  };

  const clearFeedback = () => setFeedback(null);

  return (
    <div className={`answer-input ${disabled ? 'disabled' : ''}`}>
      {feedback && (
        <div className={`feedback-banner ${feedback.type}`} onClick={clearFeedback}>
          <span className="material-symbols-outlined">
            {feedback.type === 'correct' ? 'check_circle' :
             feedback.type === 'partial' ? 'info' : 'error'}
          </span>
          <p>{feedback.message}</p>
          <button className="close-feedback">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
      )}

      {questionType === 'multiple_choice' && options.length > 0 ? (
        <div className="multiple-choice-options">
          {options.map((option, index) => (
            <button
              key={index}
              className={`option-button ${selectedOption === index ? 'selected' : ''}`}
              onClick={() => setSelectedOption(index)}
              disabled={disabled || isSubmitting}
            >
              <span className="option-letter">{String.fromCharCode(65 + index)}</span>
              <span className="option-text">{option}</span>
              {selectedOption === index && (
                <span className="material-symbols-outlined check">check</span>
              )}
            </button>
          ))}
        </div>
      ) : (
        <div className="text-input-container">
          <input
            ref={inputRef}
            type={questionType === 'numeric' ? 'number' : 'text'}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              questionType === 'numeric'
                ? 'Enter your answer...'
                : 'Type your answer or use voice...'
            }
            disabled={disabled || isSubmitting}
            className="answer-text-input"
          />

          <button
            className={`voice-button ${isRecording ? 'recording' : ''}`}
            onClick={handleVoiceInput}
            disabled={disabled || isSubmitting}
            title="Voice input"
          >
            <span className="material-symbols-outlined">
              {isRecording ? 'graphic_eq' : 'mic'}
            </span>
          </button>
        </div>
      )}

      <div className="answer-actions">
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={disabled || isSubmitting || (!answer.trim() && selectedOption === null)}
        >
          {isSubmitting ? (
            <>
              <span className="material-symbols-outlined spinning">sync</span>
              Checking...
            </>
          ) : (
            <>
              <span className="material-symbols-outlined">send</span>
              Submit Answer
            </>
          )}
        </button>

        <button
          className="hint-button"
          onClick={() => {
            if (connected && client) {
              client.send({ text: "I'm stuck. Can you give me a hint?" });
              setEmotion('thinking');
            }
          }}
          disabled={disabled}
        >
          <span className="material-symbols-outlined">lightbulb</span>
          Get Hint
        </button>

        <button
          className="skip-button"
          onClick={() => {
            if (connected && client) {
              client.send({ text: "I'd like to skip this question and try a different one." });
            }
          }}
          disabled={disabled}
        >
          <span className="material-symbols-outlined">skip_next</span>
          Skip
        </button>
      </div>
    </div>
  );
};

export default AnswerInput;
