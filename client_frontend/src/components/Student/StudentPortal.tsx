import React, { useState, useEffect } from 'react';
import { 
  User, 
  Clock, 
  BookOpen, 
  CheckCircle, 
  XCircle, 
  Award,
  AlertTriangle,
  Play
} from 'lucide-react';
import { examApi } from '../../services/api';
import { useUser } from '../../contexts/UserContext';

interface Question {
  q: string;
  options: string[];
  ans: string;
}

interface ExamStatus {
  student_id: string;
  status: string;
  marks?: number;
  total_questions?: number;
  correct_answers?: number;
}

const StudentPortal = () => {
  const { user } = useUser();
  const [examStarted, setExamStarted] = useState(false);
  const [questions, setQuestions] = useState([] as Question[]);
  const [answers, setAnswers] = useState([] as string[]);
  const [submitted, setSubmitted] = useState(false);
  const [examStatus, setExamStatus] = useState(null as ExamStatus | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);
  const [timeRemaining, setTimeRemaining] = useState(1800); // 30 minutes

  const studentId = user?.id || 'guest';

  useEffect(() => {
    fetchExamStatus();
  }, []);

  useEffect(() => {
    // Check if marks are released and update submitted state
    if (examStatus && examStatus.marks !== undefined) {
      setSubmitted(true);
    }
  }, [examStatus]);

  useEffect(() => {
    if (examStarted && !submitted) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [examStarted, submitted]);

  const fetchExamStatus = async () => {
    try {
      const status = await examApi.getExamStatus(studentId);
      setExamStatus(status);
      // If exam is submitted OR marks are released, show results
      if (status.status === 'submitted' || status.status === 'completed' || status.marks !== undefined) {
        setSubmitted(true);
      }
    } catch (err) {
      console.error('Failed to fetch exam status:', err);
    }
  };

  const startExam = async () => {
    setLoading(true);
    setError(null);
    try {
      await examApi.startExam(studentId);
      const questionsData = await examApi.getQuestions();
      setQuestions(questionsData.questions);
      setAnswers(new Array(questionsData.questions.length).fill(''));
      setExamStarted(true);
      setTimeRemaining(1800); // Reset timer
    } catch (err) {
      setError('Failed to start exam');
      console.error('Start exam error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await examApi.submitExam({
        student_id: studentId,
        answers: answers
      });
      setSubmitted(true);
      await fetchExamStatus();
    } catch (err) {
      setError('Failed to submit exam');
      console.error('Submit error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
              <User className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">Student Portal</h1>
              <p className="text-blue-100 text-lg">
                Welcome, {user?.name || 'Student'}
              </p>
              <p className="text-blue-200 text-sm">Roll Number: {studentId}</p>
            </div>
          </div>
          {examStarted && !submitted && (
            <div className="flex items-center space-x-3 px-6 py-4 bg-red-500/90 backdrop-blur-sm rounded-lg border-2 border-red-300 animate-pulse">
              <Clock className="h-6 w-6 text-white" />
              <div>
                <p className="text-xs text-red-100">Time Remaining</p>
                <p className="text-2xl font-mono font-bold text-white">
                  {formatTime(timeRemaining)}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Exam Status */}
      {!examStarted && !submitted && (
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <BookOpen className="h-7 w-7 text-blue-600 mr-3" />
            Available Exam
          </h2>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className="p-4 bg-blue-600 rounded-xl">
                  <BookOpen className="h-10 w-10 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Final Examination</h3>
                  <div className="flex items-center space-x-4 mt-2">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-600" />
                      <span className="text-sm text-gray-700 font-medium">30 minutes</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-gray-600" />
                      <span className="text-sm text-gray-700 font-medium">5 questions</span>
                    </div>
                  </div>
                </div>
              </div>
              <button
                onClick={startExam}
                disabled={loading}
                className="flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all duration-200 font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <Play className="h-6 w-6" />
                <span>{loading ? 'Starting...' : 'Start Exam'}</span>
              </button>
            </div>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-yellow-800">
                    Important: Once you start, the timer will begin immediately. You cannot pause the exam.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Exam Questions */}
      {examStarted && !submitted && (
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <BookOpen className="h-7 w-7 text-blue-600 mr-3" />
              Exam Questions
            </h2>
            <div className="px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-gray-600">Progress: <span className="font-bold text-blue-600">{answers.filter(a => a).length}/{questions.length}</span></p>
            </div>
          </div>
          <div className="space-y-6">
            {questions.map((q, idx) => (
              <div key={idx} className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-300 transition-colors bg-gradient-to-br from-white to-gray-50">
                <div className="flex items-start space-x-3 mb-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold">
                    {idx + 1}
                  </div>
                  <h3 className="font-semibold text-gray-900 text-lg flex-1">
                    {q.q}
                  </h3>
                </div>
                <div className="space-y-3 ml-11">
                  {q.options.map((option, optIdx) => (
                    <label
                      key={optIdx}
                      className={`flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                        answers[idx] === option.split(')')[0]
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${idx}`}
                        value={option.split(')')[0]}
                        checked={answers[idx] === option.split(')')[0]}
                        onChange={(e) => {
                          const newAnswers = [...answers];
                          newAnswers[idx] = e.target.value;
                          setAnswers(newAnswers);
                        }}
                        className="h-5 w-5 text-blue-600"
                      />
                      <span className={`flex-1 ${answers[idx] === option.split(')')[0] ? 'font-medium text-blue-900' : 'text-gray-700'}`}>
                        {option}
                      </span>
                      {answers[idx] === option.split(')')[0] && (
                        <CheckCircle className="h-5 w-5 text-blue-600" />
                      )}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 p-6 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border-2 border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Exam Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {answers.filter(a => a).length} / {questions.length} <span className="text-base font-normal text-gray-600">answered</span>
                </p>
              </div>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition-all duration-200 font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <CheckCircle className="h-6 w-6" />
                <span>{loading ? 'Submitting...' : 'Submit Exam'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {submitted && (
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <div className="text-center">
            {examStatus.marks !== undefined ? (
              <>
                <div className="inline-block p-4 bg-green-100 rounded-full mb-6">
                  <Award className="h-20 w-20 text-green-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Exam Completed!
                </h2>
                <p className="text-gray-600 mb-8">Congratulations on completing your examination</p>
                
                <div className="max-w-md mx-auto bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-8 shadow-lg">
                  <p className="text-sm font-medium text-gray-600 mb-3">Your Final Score</p>
                  <div className="mb-6">
                    <p className="text-7xl font-bold text-green-600 mb-2">
                      {examStatus.marks}<span className="text-4xl">%</span>
                    </p>
                    <div className="w-full bg-gray-200 rounded-full h-3 mt-4">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${examStatus.marks}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-gray-700">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <p className="text-lg font-medium">
                      {examStatus.correct_answers} out of {examStatus.total_questions} correct
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="inline-block p-4 bg-blue-100 rounded-full mb-6 animate-pulse">
                  <CheckCircle className="h-20 w-20 text-blue-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Exam Submitted Successfully!
                </h2>
                <p className="text-gray-600 mb-8">
                  Your answers have been recorded and are being evaluated
                </p>
                <div className="max-w-md mx-auto p-6 bg-blue-50 border-2 border-blue-200 rounded-xl">
                  <div className="flex items-center justify-center space-x-3 mb-3">
                    <Clock className="h-5 w-5 text-blue-600 animate-spin" />
                    <p className="text-lg font-medium text-blue-900">
                      Awaiting Results
                    </p>
                  </div>
                  <p className="text-sm text-blue-700">
                    Your teacher will release the marks soon. Please check back later.
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentPortal;


