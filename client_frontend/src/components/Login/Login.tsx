import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { databaseApi } from '../../services/api';
import { Shield, User, Cpu, LogIn, AlertCircle, RefreshCw } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useUser();
  const [selectedRole, setSelectedRole] = useState<'student' | 'teacher' | 'processor'>('student');
  const [id, setId] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // For students, only ID is required. For others, both ID and name required.
    if (!id) return;
    if (selectedRole !== 'student' && !name) return;

    setError('');
    setLoading(true);

    try {
      // Validate based on role
      if (selectedRole === 'student') {
        // Check if student exists in database
        const dbResponse = await databaseApi.getAllRecords();
        const students = dbResponse.records || [];
        const studentExists = students.some(s => s.rn === id);
        
        if (!studentExists) {
          setError('Student roll number not found in database. Please check your roll number.');
          setLoading(false);
          return;
        }
        
        // Get student name from database
        const student = students.find(s => s.rn === id);
        if (student) {
          login(selectedRole, id, student.name);
        }
      } else if (selectedRole === 'teacher') {
        // Validate teacher ID
        if (id !== 'T001') {
          setError('Invalid Teacher ID. Use T001 for teacher access.');
          setLoading(false);
          return;
        }
        login(selectedRole, id, name);
      } else if (selectedRole === 'processor') {
        // Validate processor ID
        if (id !== 'P001') {
          setError('Invalid Processor ID. Use P001 for processor access.');
          setLoading(false);
          return;
        }
        login(selectedRole, id, name);
      }
      
      // Navigate based on role
      if (selectedRole === 'student') {
        navigate('/student');
      } else if (selectedRole === 'teacher') {
        navigate('/teacher');
      } else {
        navigate('/processor');
      }
    } catch (err) {
      setError('Failed to validate credentials. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const roles = [
    {
      value: 'student' as const,
      label: 'Student',
      icon: User,
      description: 'Take exams and view results',
      color: 'blue'
    },
    {
      value: 'teacher' as const,
      label: 'Teacher',
      icon: Shield,
      description: 'Manage exams and release marks',
      color: 'green'
    },
    {
      value: 'processor' as const,
      label: 'Processor',
      icon: Cpu,
      description: 'Process and evaluate submissions',
      color: 'purple'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-100 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Pattern/Texture */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
      </div>
      
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full transform transition-all hover:scale-[1.01] relative z-10 backdrop-blur-sm">
        <div className="text-center mb-8">
          <div className="inline-block p-3 bg-blue-100 rounded-full mb-4">
            <Shield className="h-12 w-12 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Exam Proctoring System
          </h1>
          <p className="text-gray-600">Secure • Reliable • Efficient</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          {/* Role Selection */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Role
            </label>
            {roles.map((role) => {
              const Icon = role.icon;
              return (
                <div
                  key={role.value}
                  onClick={() => setSelectedRole(role.value)}
                  className={`p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 transform hover:scale-[1.02] ${
                    selectedRole === role.value
                      ? 'border-blue-500 bg-blue-50 shadow-md'
                      : 'border-gray-200 hover:border-blue-300 hover:shadow-sm'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      selectedRole === role.value ? 'bg-blue-100' : 'bg-gray-100'
                    }`}>
                      <Icon className={`h-6 w-6 ${
                        selectedRole === role.value ? 'text-blue-600' : 'text-gray-500'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{role.label}</h3>
                      <p className="text-sm text-gray-600">{role.description}</p>
                    </div>
                    {selectedRole === role.value && (
                      <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* ID Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {selectedRole === 'student' ? 'Roll Number' : 
               selectedRole === 'teacher' ? 'Teacher ID' : 'Processor ID'}
            </label>
            <input
              type="text"
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder={
                selectedRole === 'student' ? 'e.g., 23102A0058' : 
                selectedRole === 'teacher' ? 'Enter T001' : 
                'Enter P001'
              }
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              required
            />
          </div>

          {/* Name Input - Only for Teacher/Processor */}
          {selectedRole !== 'student' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                required
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <p className="ml-2 text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            {loading ? (
              <>
                <RefreshCw className="h-5 w-5 animate-spin" />
                <span>Validating...</span>
              </>
            ) : (
              <>
                <LogIn className="h-5 w-5" />
                <span>Login as {roles.find(r => r.value === selectedRole)?.label}</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
            <Shield className="h-4 w-4" />
            <p>Secure Authentication • No Password Required</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
