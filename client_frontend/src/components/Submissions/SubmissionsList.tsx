import React, { useState, useEffect } from 'react';
import { 
  Users, 
  RefreshCw, 
  Send, 
  CheckCircle, 
  Clock,
  XCircle,
  Award,
  Filter,
  RotateCcw,
  TrendingUp,
  FileText
} from 'lucide-react';
import { examApi, databaseApi } from '../../services/api';
import { useUser } from '../../contexts/UserContext';

interface StudentSubmission {
  student_id: string;
  student_name: string;
  roll_number: string;
  status: string;
  marks?: number;
  submitted_at?: string;
  marks_released: boolean;
}

const SubmissionsList = () => {
  const { user } = useUser();
  const [submissions, setSubmissions] = useState<StudentSubmission[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'submitted' | 'pending' | 'released'>('all');
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    submitted: 0,
    pending: 0,
    released: 0,
    avgMarks: 0
  });

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    setLoading(true);
    try {
      // Fetch real students from database
      const dbResponse = await databaseApi.getAllRecords();
      const students = dbResponse.records || [];
      
      const submissionData: StudentSubmission[] = [];
      let totalMarks = 0;
      let marksCount = 0;
      let submitted = 0;
      let released = 0;

      // Fetch exam status for each student from database
      for (const student of students) {
        const studentId = student.rn; // Use roll number as student ID
        
        try {
          const status = await examApi.getExamStatus(studentId);
          const isReleased = status.marks !== undefined;
          
          submissionData.push({
            student_id: studentId,
            student_name: student.name,
            roll_number: student.rn,
            status: status.status || 'not_started',
            marks: status.marks,
            marks_released: isReleased
          });

          if (status.status === 'submitted' || isReleased) submitted++;
          if (isReleased) {
            released++;
            if (status.marks) {
              totalMarks += status.marks;
              marksCount++;
            }
          }
        } catch (err) {
          // Student hasn't started exam yet
          submissionData.push({
            student_id: studentId,
            student_name: student.name,
            roll_number: student.rn,
            status: 'not_started',
            marks_released: false
          });
        }
      }

      setSubmissions(submissionData);
      setStats({
        total: students.length,
        submitted,
        pending: students.length - submitted,
        released,
        avgMarks: marksCount > 0 ? Math.round(totalMarks / marksCount) : 0
      });
    } catch (err) {
      console.error('Failed to fetch submissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const releaseMarks = async (studentId: string) => {
    try {
      await examApi.releaseMarks(studentId);
      setMessage(`✓ Marks released for ${studentId}`);
      setTimeout(() => setMessage(''), 3000);
      await fetchSubmissions();
    } catch (err) {
      setMessage(`✗ Failed to release marks for ${studentId}`);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const releaseAllMarks = async () => {
    setLoading(true);
    const submitted = submissions.filter(s => s.status === 'submitted' && !s.marks_released);
    
    for (const submission of submitted) {
      try {
        await examApi.releaseMarks(submission.student_id);
      } catch (err) {
        console.error(`Failed to release for ${submission.student_id}`);
      }
    }
    
    setMessage(`✓ Released marks for ${submitted.length} students`);
    setTimeout(() => setMessage(''), 3000);
    await fetchSubmissions();
    setLoading(false);
  };

  const resetExam = async (studentId: string) => {
    try {
      await fetch(`/api/v1/exam/reset/${studentId}`, {
        method: 'POST'
      });
      
      // Update the local state immediately for instant UI feedback
      setSubmissions(prev => prev.map(s => 
        s.student_id === studentId 
          ? { ...s, status: 'not_started', marks: undefined, marks_released: false }
          : s
      ));
      
      // Update stats
      setStats(prev => ({
        ...prev,
        submitted: prev.submitted - 1,
        pending: prev.pending + 1,
        released: prev.released - (submissions.find(s => s.student_id === studentId)?.marks_released ? 1 : 0)
      }));
      
      setMessage(`✓ Exam reset for ${studentId}. Student can now retake the exam.`);
      setTimeout(() => setMessage(''), 3000);
      
      // Fetch fresh data from server after a short delay
      setTimeout(() => fetchSubmissions(), 500);
    } catch (err) {
      setMessage(`✗ Failed to reset exam for ${studentId}`);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const getStatusBadge = (status: string, released: boolean) => {
    if (released) {
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Released</span>;
    }
    
    switch (status) {
      case 'submitted':
        return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">Submitted</span>;
      case 'not_started':
        return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">Not Started</span>;
      default:
        return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">{status}</span>;
    }
  };

  const filteredSubmissions = submissions.filter(s => {
    if (filter === 'all') return true;
    if (filter === 'submitted') return s.status === 'submitted' && !s.marks_released;
    if (filter === 'pending') return s.status === 'not_started';
    if (filter === 'released') return s.marks_released;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
              <FileText className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">All Submissions</h1>
              <p className="text-blue-100 text-lg">View and manage student exam submissions</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchSubmissions}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 disabled:opacity-50 transition-all duration-200 border border-white/30"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
              <span className="font-medium">Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Students</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Submitted</p>
              <p className="text-3xl font-bold text-gray-900">{stats.submitted}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Pending</p>
              <p className="text-3xl font-bold text-gray-900">{stats.pending}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Released</p>
              <p className="text-3xl font-bold text-gray-900">{stats.released}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Award className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-emerald-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Avg Marks</p>
              <p className="text-3xl font-bold text-gray-900">{stats.avgMarks}%</p>
            </div>
            <div className="p-3 bg-emerald-100 rounded-lg">
              <TrendingUp className="h-8 w-8 text-emerald-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Bulk Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-2">
              {(['all', 'submitted', 'pending', 'released'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    filter === f
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <button
            onClick={releaseAllMarks}
            disabled={loading || submissions.filter(s => s.status === 'submitted' && !s.marks_released).length === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <Send className="h-4 w-4" />
            <span>Release All Pending</span>
          </button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-md ${
          message.startsWith('✓') ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <p className={`text-sm ${message.startsWith('✓') ? 'text-green-700' : 'text-red-700'}`}>
            {message}
          </p>
        </div>
      )}

      {/* Submissions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Student
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Marks
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredSubmissions.map((submission) => (
              <tr key={submission.student_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-medium">
                        {submission.student_name.charAt(0)}
                      </span>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {submission.student_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        Roll: {submission.roll_number}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(submission.status, submission.marks_released)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {submission.marks !== undefined ? (
                    <div className="flex items-center space-x-2">
                      <Award className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm font-medium text-gray-900">
                        {submission.marks}%
                      </span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex items-center space-x-2">
                    {submission.status === 'submitted' && !submission.marks_released ? (
                      <button
                        onClick={() => releaseMarks(submission.student_id)}
                        className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                      >
                        <Send className="h-3 w-3" />
                        <span>Release</span>
                      </button>
                    ) : submission.marks_released ? (
                      <div className="flex items-center space-x-1 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span>Released</span>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                    
                    {/* Reset button - show for submitted or released exams */}
                    {(submission.status === 'submitted' || submission.marks_released) && (
                      <button
                        onClick={() => resetExam(submission.student_id)}
                        className="flex items-center space-x-1 px-3 py-1 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                        title="Reset exam attempt"
                      >
                        <RotateCcw className="h-3 w-3" />
                        <span>Reset</span>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredSubmissions.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No submissions found for this filter</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmissionsList;
