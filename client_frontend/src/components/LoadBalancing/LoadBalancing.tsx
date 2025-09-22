import React, { useState, useEffect } from 'react';
import { 
  Loader, 
  Server, 
  Database,
  RefreshCw,
  Play,
  BarChart3,
  Activity,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { loadBalanceApi } from '../../services/api';
import type { LoadBalanceSubmission, LoadBalanceResponse, LoadBalanceStatus } from '../../types';

interface Submission {
  id: string;
  student_id: string;
  payload: Record<string, any>;
  response?: LoadBalanceResponse;
  timestamp: Date;
}

const LoadBalancing: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loadBalanceStatus, setLoadBalanceStatus] = useState<LoadBalanceStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoSubmit, setAutoSubmit] = useState(false);
  const [submissionCount, setSubmissionCount] = useState(12);

  useEffect(() => {
    fetchLoadBalanceStatus();
    const interval = setInterval(fetchLoadBalanceStatus, 3000); // Refresh every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchLoadBalanceStatus = async () => {
    try {
      const status = await loadBalanceApi.getLoadBalanceStatus();
      setLoadBalanceStatus(status);
    } catch (err) {
      console.error('Failed to fetch load balance status:', err);
    }
  };

  const submitForProcessing = async (studentId: string, payload: Record<string, any>) => {
    setLoading(true);
    setError(null);

    try {
      const submission: LoadBalanceSubmission = {
        student_id: studentId,
        payload: payload
      };

      const response = await loadBalanceApi.submitForProcessing(submission);
      
      const newSubmission: Submission = {
        id: Date.now().toString(),
        student_id: studentId,
        payload: payload,
        response: response,
        timestamp: new Date()
      };

      setSubmissions(prev => [newSubmission, ...prev]);
    } catch (err) {
      setError('Failed to submit for processing');
      console.error('Submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const submitMultiple = async () => {
    setLoading(true);
    setError(null);

    try {
      const promises = [];
      for (let i = 0; i < submissionCount; i++) {
        const studentId = `student_${i}`;
        const payload = {
          data: `test_data_${i}`,
          timestamp: Date.now(),
          type: 'exam_submission'
        };
        
        promises.push(
          loadBalanceApi.submitForProcessing({
            student_id: studentId,
            payload: payload
          }).then(response => ({
            id: `${Date.now()}_${i}`,
            student_id: studentId,
            payload: payload,
            response: response,
            timestamp: new Date()
          }))
        );
      }

      const results = await Promise.all(promises);
      setSubmissions(prev => [...results, ...prev]);
    } catch (err) {
      setError('Failed to submit multiple requests');
      console.error('Multiple submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearSubmissions = () => {
    setSubmissions([]);
    setError(null);
  };

  const getStatusIcon = (via: string) => {
    switch (via) {
      case 'main':
        return <Server className="h-4 w-4 text-green-500" />;
      case 'backup':
        return <Database className="h-4 w-4 text-blue-500" />;
      default:
        return <Loader className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'migrated':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLoadColor = (current: number, threshold: number) => {
    const percentage = (current / threshold) * 100;
    if (percentage >= 100) return 'text-red-600';
    if (percentage >= 80) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Loader className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Load Balancing
              </h1>
              <p className="text-gray-600">
                Dynamic load balancing with backup server migration
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchLoadBalanceStatus}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={clearSubmissions}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <XCircle className="h-4 w-4" />
              <span>Clear</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Load Balance Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            System Status
          </h2>

          {loadBalanceStatus ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">Local Inflight</span>
                    <span className={`text-sm font-semibold ${getLoadColor(loadBalanceStatus.local_inflight, loadBalanceStatus.migrate_threshold)}`}>
                      {loadBalanceStatus.local_inflight}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        loadBalanceStatus.local_inflight >= loadBalanceStatus.migrate_threshold 
                          ? 'bg-red-500' 
                          : loadBalanceStatus.local_inflight >= loadBalanceStatus.migrate_threshold * 0.8
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ 
                        width: `${Math.min((loadBalanceStatus.local_inflight / loadBalanceStatus.migrate_threshold) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>

                <div className="p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">Threshold</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {loadBalanceStatus.migrate_threshold}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Migration threshold
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Received</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {loadBalanceStatus.received_count}
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Local Queue</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {loadBalanceStatus.local_queue_size}
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-md">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Backup Queue</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {loadBalanceStatus.backup_queue_size}
                  </span>
                </div>
              </div>

              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">
                    {loadBalanceStatus.local_inflight >= loadBalanceStatus.migrate_threshold 
                      ? 'Migration Active' 
                      : 'Local Processing'}
                  </span>
                </div>
                <p className="text-xs text-blue-600 mt-1">
                  {loadBalanceStatus.local_inflight >= loadBalanceStatus.migrate_threshold 
                    ? 'New requests will be migrated to backup server'
                    : 'New requests will be processed locally'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No status data available</p>
            </div>
          )}
        </div>

        {/* Submission Controls */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Submission Controls
          </h2>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Submissions
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={submissionCount}
                  onChange={(e) => setSubmissionCount(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={submitMultiple}
                  disabled={loading}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  <span>{loading ? 'Submitting...' : 'Submit Multiple'}</span>
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => submitForProcessing('single_student', { data: 'single_test', type: 'manual' })}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="h-4 w-4" />
                <span>Submit Single</span>
              </button>

              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={autoSubmit}
                  onChange={(e) => setAutoSubmit(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">Auto-submit every 5s</span>
              </label>
            </div>
          </div>

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
      </div>

      {/* Submission History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Submission History
        </h2>

        {submissions.length > 0 ? (
          <div className="space-y-3">
            {submissions.slice(0, 20).map((submission) => (
              <div key={submission.id} className="p-4 border border-gray-200 rounded-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(submission.response?.via || 'unknown')}
                    <span className="text-sm font-medium text-gray-900">
                      {submission.student_id}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(submission.response?.status || 'unknown')}`}>
                      {submission.response?.status || 'pending'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {submission.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Via:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {submission.response?.via || 'unknown'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {submission.payload.type || 'unknown'}
                    </span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mt-2">
                  {submission.response?.message || 'Processing...'}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Loader className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No submissions yet</p>
            <p className="text-sm mt-2">
              Submit requests to see load balancing in action
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadBalancing;
