import React, { useState, useEffect } from 'react';
import './question-display.scss';

interface Question {
  question_id: string;
  skill_ids: string[];
  content: string;
  difficulty: number;
}

const QuestionDisplay: React.FC = () => {
  const [question, setQuestion] = useState<Question | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const userId = "1"; // Hardcoded for now

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/next-question/${userId}`);
        if (!response.ok) {
          throw new Error('No recommended question found or API error.');
        }
        const data: Question = await response.json();
        setQuestion(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
        setQuestion(null);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [userId]);

  if (loading) {
    return <div className="question-display">Loading question...</div>;
  }

  if (error) {
    return <div className="question-display error">Error: {error}</div>;
  }

  return (
    <div className="question-display">
      <h2 className="question-title">Here's your next question:</h2>
      {question && <p className="question-text">{question.content}</p>}
    </div>
  );
};

export default QuestionDisplay;
