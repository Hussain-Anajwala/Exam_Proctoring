import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  User, 
  BookOpen, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Download
} from 'lucide-react';
import { violationApi } from '../../services/api';
import type { ViolationReport, ViolationResponse, Marksheet } from '../../types';

const ViolationDetection: React.FC = () => {
  const [violationForm, setViolationForm] = useState<ViolationReport>({
    roll: 58,
    name: 'Hussain',
    warning: 'Please focus, exam in progress!',
    question_no: 1,
    violation_no: 1
  });
  const [violationResponse, setViolationResponse] = useState<ViolationResponse | null>(null);
  const [marksheet, setMarksheet] = useState<Marksheet | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoSteps, setDemoSteps] = useState<string[]>([]);
  const [demoConfig, setDemoConfig] = useState({
    studentRoll: 58,
    violationsToSimulate: 2,
  });

  const students = [
    { roll: 58, name: 'Hussain' },
    { roll: 59, name: 'Saish' },
    { roll: 65, name: 'Khushal' },
    { roll: 75, name: 'Hasnain' },
    { roll: 68, name: 'Amritesh' }
  ];

  useEffect(() => {
    fetchMarksheet();
  }, []);

  const fetchMarksheet = async () => {
    console.log('Refresh button clicked - Violation Detection');
    try {
      const data = await violationApi.getMarksheet();
      setMarksheet({...data}); // Force new object reference
      console.log('Marksheet refreshed:', data);
    } catch (err) {
      setError('Failed to fetch marksheet');
      console.error('Marksheet error:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await violationApi.reportViolation(violationForm);
      setViolationResponse(response);
      await fetchMarksheet(); // Refresh marksheet
    } catch (err) {
      setError('Failed to report violation');
      console.error('Violation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentChange = (roll: number) => {
    const student = students.find(s => s.roll === roll);
    if (student) {
      setViolationForm(prev => ({
        ...prev,
        roll,
        name: student.name
      }));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'terminated':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'ignored':
        return <CheckCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <Shield className="h-5 w-5 text-blue-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'terminated':
        return 'bg-red-100 text-red-800';
      case 'ignored':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const logDemo = (msg: string) => setDemoSteps(prev => [msg, ...prev].slice(0, 50));

  const resetDemo = async () => {
    console.log('Reset button clicked - Violation Detection');
    setDemoRunning(false);
    setDemoSteps([]);
    setViolationResponse(null);
    setError(null);
    setMarksheet(null); // Clear first
    
    try {
      // Call backend reset endpoint to clear all violations
      await fetch('/api/v1/session/reset', { method: 'POST' });
      console.log('Backend reset successful');
    } catch (err) {
      console.error('Failed to reset backend:', err);
    }
    
    setTimeout(() => fetchMarksheet(), 100); // Then refresh
  };

  const runDemo = async () => {
    if (demoRunning) return;
    setDemoRunning(true);
    setDemoSteps([]);
    try {
      const student = students.find(s => s.roll === demoConfig.studentRoll) || students[0];
      // Simulate one or two violations
      for (let i = 1; i <= demoConfig.violationsToSimulate; i++) {
        const payload: ViolationReport = {
          roll: student.roll,
          name: student.name,
          warning: `Violation ${i} demo`,
          question_no: i,
          violation_no: i,
        };
        const res = await violationApi.reportViolation(payload);
        setViolationResponse(res);
        logDemo(`Step ${i}: ${res.status} → marks ${res.current_marks}%`);
        await fetchMarksheet();
      }
    } catch (e) {
      setError('Demo failed');
      console.error(e);
    } finally {
      setDemoRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Violation Detection
              </h1>
              <p className="text-gray-600">
                Report and track exam violations in real-time
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchMarksheet}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={resetDemo}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <XCircle className="h-4 w-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Violation Report Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Report Violation
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Student
              </label>
              <select
                value={violationForm.roll}
                onChange={(e) => handleStudentChange(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {students.map(student => (
                  <option key={student.roll} value={student.roll}>
                    {student.name} (Roll: {student.roll})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Question Number
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={violationForm.question_no}
                onChange={(e) => setViolationForm(prev => ({
                  ...prev,
                  question_no: Number(e.target.value)
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Violation Number
              </label>
              <select
                value={violationForm.violation_no}
                onChange={(e) => setViolationForm(prev => ({
                  ...prev,
                  violation_no: Number(e.target.value)
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>1st Violation (Warning)</option>
                <option value={2}>2nd Violation (Termination)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Warning Message
              </label>
              <textarea
                value={violationForm.warning}
                onChange={(e) => setViolationForm(prev => ({
                  ...prev,
                  warning: e.target.value
                }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <AlertTriangle className="h-4 w-4" />
              )}
              <span>{loading ? 'Reporting...' : 'Report Violation'}</span>
            </button>
          </form>

          {/* Response Display */}
          {violationResponse && (
            <div className="mt-6 p-4 bg-gray-50 rounded-md">
              <div className="flex items-center space-x-2 mb-2">
                {getStatusIcon(violationResponse.status)}
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(violationResponse.status)}`}>
                  {violationResponse.status.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-2">{violationResponse.message}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Violation Count:</span>
                  <span className="ml-2 font-medium">{violationResponse.violation_count}</span>
                </div>
                <div>
                  <span className="text-gray-600">Current Marks:</span>
                  <span className="ml-2 font-medium">{violationResponse.current_marks}%</span>
                </div>
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

        {/* Marksheet */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Current Marksheet
            </h2>
            <button
              onClick={() => {
                const data = marksheet ? JSON.stringify(marksheet, null, 2) : '';
                const blob = new Blob([data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'marksheet.json';
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>

          {marksheet ? (
            <div className="space-y-4">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Roll
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Violations
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Marks
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(marksheet.marksheet).map(([roll, marks]) => {
                      const student = students.find(s => s.roll === Number(roll));
                      const violations = marksheet.violations[roll] || 0;
                      const isTerminated = marksheet.terminated_students.includes(Number(roll));
                      
                      return (
                        <tr key={roll} className={isTerminated ? 'bg-red-50' : ''}>
                          <td className="px-4 py-2 text-sm font-medium text-gray-900">
                            {roll}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-900">
                            {student?.name || 'Unknown'}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-900">
                            {violations}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-900">
                            {marks}%
                          </td>
                          <td className="px-4 py-2 text-sm">
                            {isTerminated ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Terminated
                              </span>
                            ) : violations > 0 ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                Warning
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Clean
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {marksheet.terminated_students.length}
                  </p>
                  <p className="text-sm text-gray-600">Terminated Students</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">
                    {(Object.values(marksheet.violations) as number[]).reduce((sum, count) => sum + count, 0)}
                  </p>
                  <p className="text-sm text-gray-600">Total Violations</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Shield className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No marksheet data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Demo Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Demo</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={runDemo}
              disabled={demoRunning}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {demoRunning ? 'Running...' : 'Run Demo'}
            </button>
            <button
              onClick={resetDemo}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Reset
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Student</label>
            <select
              value={demoConfig.studentRoll}
              onChange={(e) => setDemoConfig(prev => ({ ...prev, studentRoll: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {students.map(s => (
                <option key={s.roll} value={s.roll}>{s.name} (Roll: {s.roll})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Violations</label>
            <select
              value={demoConfig.violationsToSimulate}
              onChange={(e) => setDemoConfig(prev => ({ ...prev, violationsToSimulate: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
            </select>
          </div>
        </div>

        <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 max-h-48 overflow-auto text-sm">
          {demoSteps.length === 0 ? (
            <p className="text-gray-500">No demo steps yet.</p>
          ) : (
            <ul className="space-y-1">
              {demoSteps.map((s, i) => (<li key={i}>{s}</li>))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default ViolationDetection;
