import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Send, CheckCircle, XCircle, RotateCcw, Users, Award, List } from 'lucide-react';
import { examApi } from '../../services/api';
import { useUser } from '../../contexts/UserContext';

const TeacherDashboard = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [studentId, setStudentId] = useState('');
  const [resetStudentId, setResetStudentId] = useState('');
  const [message, setMessage] = useState('');
  const [resetMessage, setResetMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  const releaseMarks = async () => {
    if (!studentId) return;
    setLoading(true);
    try {
      await examApi.releaseMarks(studentId);
      setMessage(`✓ Marks released for ${studentId}`);
      setStudentId('');
    } catch (err) {
      setMessage(`✗ Error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const resetExam = async () => {
    if (!resetStudentId) return;
    setResetLoading(true);
    setResetMessage('');
    try {
      // Call backend to reset exam for this student
      await fetch(`/api/v1/exam/reset/${resetStudentId}`, {
        method: 'POST'
      });
      setResetMessage(`✓ Exam reset for ${resetStudentId}. Student can now retake the exam.`);
      setResetStudentId('');
    } catch (err) {
      setResetMessage(`✗ Failed to reset exam: ${err}`);
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
              <Shield className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">Teacher Dashboard</h1>
              <p className="text-blue-100 text-lg">Manage exams and release marks to students</p>
              <p className="text-blue-200 text-sm mt-1">Welcome, {user?.name}</p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/submissions')}
              className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-all duration-200 border border-white/30"
            >
              <List className="h-5 w-5" />
              <span>View All Submissions</span>
            </button>
          </div>
        </div>
      </div>

      {/* Release Marks */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-green-100 rounded-lg">
            <Award className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Release Marks</h2>
            <p className="text-sm text-gray-600">
              Enter a student ID to release their exam marks
            </p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
          <div className="flex space-x-4">
            <input
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="Enter Student ID (e.g., 23102A0058)"
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
            />
            <button
              onClick={releaseMarks}
              disabled={!studentId || loading}
              className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all duration-200 font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
            >
            <Send className="h-5 w-5" />
            <span>{loading ? 'Releasing...' : 'Release Marks'}</span>
          </button>
        </div>
          {message && (
            <div className={`mt-4 p-4 rounded-lg ${
              message.startsWith('✓') ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'
            }`}>
              <div className="flex items-center">
                {message.startsWith('✓') ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
                <p className={`ml-3 text-sm font-medium ${
                  message.startsWith('✓') ? 'text-green-700' : 'text-red-700'
                }`}>
                  {message}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Reset Exam */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-orange-100 rounded-lg">
            <RotateCcw className="h-6 w-6 text-orange-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Reset Exam Attempt</h2>
            <p className="text-sm text-gray-600">
              Clear a student's exam to allow retake
            </p>
          </div>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-200 rounded-xl p-6">
          <div className="flex space-x-4">
            <input
              type="text"
              value={resetStudentId}
              onChange={(e) => setResetStudentId(e.target.value)}
              placeholder="Enter Student ID (e.g., 23102A0058)"
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all"
            />
            <button
              onClick={resetExam}
              disabled={!resetStudentId || resetLoading}
              className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-700 text-white rounded-lg hover:from-orange-700 hover:to-orange-800 disabled:opacity-50 transition-all duration-200 font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
            >
              <RotateCcw className="h-5 w-5" />
              <span>{resetLoading ? 'Resetting...' : 'Reset Exam'}</span>
            </button>
          </div>
          {resetMessage && (
            <div className={`mt-4 p-4 rounded-lg ${
              resetMessage.startsWith('✓') ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'
            }`}>
              <div className="flex items-center">
                {resetMessage.startsWith('✓') ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
                <p className={`ml-3 text-sm font-medium ${
                  resetMessage.startsWith('✓') ? 'text-green-700' : 'text-red-700'
                }`}>
                  {resetMessage}
                </p>
              </div>
            </div>
          )}
          <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg">
            <div className="flex items-center">
              <XCircle className="h-5 w-5 text-yellow-600" />
              <p className="ml-3 text-sm font-medium text-yellow-800">
                Warning: This will permanently delete the student's submission and marks
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Common Student IDs</h3>
            <div className="space-y-2">
              {['student1', 'student2', 'student3', user?.id].filter(Boolean).map((id) => (
                <button
                  key={id}
                  onClick={() => setStudentId(id || '')}
                  className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                >
                  {id}
                </button>
              ))}
            </div>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Instructions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Students must submit exam first</li>
              <li>• Processor evaluates submissions</li>
              <li>• Teacher releases marks</li>
              <li>• Students can then view results</li>
            </ul>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Other Actions</h3>
            <div className="space-y-2">
              <button 
                onClick={() => navigate('/submissions')}
                className="block w-full text-left px-3 py-2 text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-md transition-colors"
              >
                View All Submissions
              </button>
              <button 
                onClick={() => navigate('/database')}
                className="block w-full text-left px-3 py-2 text-sm bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-md transition-colors"
              >
                Edit Database Records
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;


