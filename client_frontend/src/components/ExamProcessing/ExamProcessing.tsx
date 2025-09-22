import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Play, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Download,
  Award,
  Clock
} from 'lucide-react';
import { examApi } from '../../services/api';
import type { ExamQuestion, ExamSubmission, ExamResponse, ExamStatus } from '../../types';

const ExamProcessing: React.FC = () => {
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [currentStudent, setCurrentStudent] = useState('student1');
  const [answers, setAnswers] = useState<string[]>([]);
  const [examStatus, setExamStatus] = useState<ExamStatus | null>(null);
  const [responses, setResponses] = useState<ExamResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [examStarted, setExamStarted] = useState(false);
  const [examSubmitted, setExamSubmitted] = useState(false);

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const data = await examApi.getQuestions();
      setQuestions(data.questions);
      setAnswers(new Array(data.questions.length).fill(''));
    } catch (err) {
      setError('Failed to fetch questions');
      console.error('Questions error:', err);
    }
  };

  const startExam = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await examApi.startExam(currentStudent);
      setResponses(prev => [...prev, response]);
      setExamStarted(true);
      setExamSubmitted(false);
    } catch (err) {
      setError('Failed to start exam');
      console.error('Start exam error:', err);
    } finally {
      setLoading(false);
    }
  };

  const submitExam = async () => {
    if (answers.some(answer => answer === '')) {
      setError('Please answer all questions before submitting');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const submission: ExamSubmission = {
        student_id: currentStudent,
        answers: answers
      };

      const response = await examApi.submitExam(submission);
      setResponses(prev => [...prev, response]);
      setExamSubmitted(true);
    } catch (err) {
      setError('Failed to submit exam');
      console.error('Submit exam error:', err);
    } finally {
      setLoading(false);
    }
  };

  const releaseMarks = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await examApi.releaseMarks(currentStudent);
      setResponses(prev => [...prev, response]);
      await fetchExamStatus();
    } catch (err) {
      setError('Failed to release marks');
      console.error('Release marks error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchExamStatus = async () => {
    try {
      const status = await examApi.getExamStatus(currentStudent);
      setExamStatus(status);
    } catch (err) {
      console.error('Failed to fetch exam status:', err);
    }
  };

  const resetExam = () => {
    setAnswers(new Array(questions.length).fill(''));
    setExamStarted(false);
    setExamSubmitted(false);
    setExamStatus(null);
    setResponses([]);
    setError(null);
  };

  const handleAnswerChange = (questionIndex: number, answer: string) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answer;
    setAnswers(newAnswers);
  };

  const calculateScore = () => {
    if (!examStatus?.marks) return 0;
    return examStatus.marks;
  };

  const getScoreColor = (score: number, total: number) => {
    const percentage = (score / total) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Exam Processing
              </h1>
              <p className="text-gray-600">
                Automated exam processing with automatic mark release
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchExamStatus}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh Status</span>
            </button>
            <button
              onClick={resetExam}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <XCircle className="h-4 w-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Exam Controls */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Exam Controls
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Student ID
              </label>
              <input
                type="text"
                value={currentStudent}
                onChange={(e) => setCurrentStudent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="space-y-2">
              <button
                onClick={startExam}
                disabled={loading || examStarted}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="h-4 w-4" />
                <span>{loading ? 'Starting...' : 'Start Exam'}</span>
              </button>

              <button
                onClick={submitExam}
                disabled={loading || !examStarted || examSubmitted}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <CheckCircle className="h-4 w-4" />
                <span>{loading ? 'Submitting...' : 'Submit Exam'}</span>
              </button>

              <button
                onClick={releaseMarks}
                disabled={loading || !examSubmitted}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Award className="h-4 w-4" />
                <span>{loading ? 'Releasing...' : 'Release Marks'}</span>
              </button>
            </div>
          </div>

          {/* Exam Status */}
          {examStatus && (
            <div className="mt-6 p-4 bg-gray-50 rounded-md">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Current Status</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className="text-sm font-medium text-gray-900">{examStatus.status}</span>
                </div>
                {examStatus.marks !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Marks:</span>
                    <span className={`text-sm font-medium ${getScoreColor(examStatus.marks, questions.length)}`}>
                      {examStatus.marks}/{questions.length}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex">
                <XCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Questions */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Exam Questions
          </h2>

          {questions.length > 0 ? (
            <div className="space-y-6">
              {questions.map((question, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">
                    Question {index + 1}
                  </h3>
                  <p className="text-gray-700 mb-4">{question.q}</p>
                  
                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <label key={optionIndex} className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name={`question-${index}`}
                          value={option.split(')')[0]}
                          checked={answers[index] === option.split(')')[0]}
                          onChange={(e) => handleAnswerChange(index, e.target.value)}
                          disabled={!examStarted || examSubmitted}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <span className="text-sm text-gray-700">{option}</span>
                      </label>
                    ))}
                  </div>

                  {examSubmitted && (
                    <div className="mt-3 p-2 bg-gray-50 rounded-md">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Correct Answer:</span>
                        <span className="font-medium text-gray-900">{question.ans}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Your Answer:</span>
                        <span className={`font-medium ${
                          answers[index] === question.ans ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {answers[index] || 'Not answered'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No questions loaded</p>
              <p className="text-sm mt-2">Click "Start Exam" to load questions</p>
            </div>
          )}
        </div>
      </div>

      {/* Response History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Response History
        </h2>

        {responses.length > 0 ? (
          <div className="space-y-3">
            {responses.slice().reverse().map((response, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-md">
                <div className="flex items-center justify-between mb-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    response.status === 'started' ? 'bg-green-100 text-green-800' :
                    response.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                    response.status === 'released' ? 'bg-purple-100 text-purple-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {response.status.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">{response.message}</p>
                {response.marks !== undefined && (
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-1">
                      <Award className="h-4 w-4 text-yellow-500" />
                      <span className="text-gray-600">Marks:</span>
                      <span className={`font-medium ${getScoreColor(response.marks, questions.length)}`}>
                        {response.marks}/{questions.length}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className="text-gray-600">Percentage:</span>
                      <span className={`font-medium ${getScoreColor(response.marks, questions.length)}`}>
                        {Math.round((response.marks / questions.length) * 100)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No responses yet</p>
            <p className="text-sm mt-2">
              Start an exam to see response history
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExamProcessing;
