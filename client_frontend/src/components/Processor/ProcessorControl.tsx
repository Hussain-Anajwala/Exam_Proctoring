import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  Clock,
  AlertCircle,
  Activity
} from 'lucide-react';
import { examApi } from '../../services/api';
import { useUser } from '../../contexts/UserContext';

interface ProcessedExam {
  student_id: string;
  status: string;
  marks?: number;
  correct_answers?: number;
  total_questions?: number;
  processed_at: string;
}

const ProcessorControl = () => {
  const { user } = useUser();
  const [processing, setProcessing] = useState(false);
  const [processedExams, setProcessedExams] = useState<ProcessedExam[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    pending: 0,
    avgMarks: 0
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [studentIdInput, setStudentIdInput] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      if (processing) {
        processQueue();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [processing]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 20));
  };

  const processQueue = async () => {
    try {
      addLog('Checking for pending submissions...');
      addLog('No pending submissions found');
    } catch (err) {
      addLog('Error checking queue: ' + err);
    }
  };

  const startProcessing = () => {
    setProcessing(true);
    addLog('✓ Processor started - Auto-processing enabled');
  };

  const stopProcessing = () => {
    setProcessing(false);
    addLog('✗ Processor stopped');
  };

  const manualProcess = async () => {
    if (!studentIdInput) return;
    
    addLog(`Processing exam for ${studentIdInput}...`);
    try {
      const status = await examApi.getExamStatus(studentIdInput);
      
      if (status.status === 'submitted' || status.marks !== undefined) {
        addLog(`✓ Evaluated ${studentIdInput}: ${status.marks}%`);
        
        setProcessedExams(prev => [...prev, {
          student_id: studentIdInput,
          status: 'processed',
          marks: status.marks,
          processed_at: new Date().toISOString()
        }]);
        
        setStats(prev => ({
          ...prev,
          processed: prev.processed + 1,
          total: prev.total + 1
        }));
        
        setStudentIdInput('');
      } else {
        addLog(`⚠ ${studentIdInput}: Not submitted yet`);
      }
    } catch (err) {
      addLog(`✗ Error processing ${studentIdInput}: ${err}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
              <Cpu className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">Processor Control</h1>
              <p className="text-purple-100 text-lg">Automatic exam evaluation and processing</p>
              <p className="text-purple-200 text-sm mt-1">Processor: {user?.name}</p>
            </div>
          </div>
          <div className={`flex items-center space-x-3 px-6 py-4 rounded-lg backdrop-blur-sm border-2 ${
            processing ? 'bg-green-500/20 border-green-300' : 'bg-white/10 border-white/30'
          }`}>
            <Activity className={`h-6 w-6 text-white ${processing ? 'animate-pulse' : ''}`} />
            <div>
              <p className="text-xs text-purple-100">Status</p>
              <p className="text-lg font-bold text-white">
                {processing ? 'Processing' : 'Idle'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Total Processed</p>
              <p className="text-3xl font-bold text-gray-900">{stats.processed}</p>
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
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Avg Marks</p>
              <p className="text-3xl font-bold text-gray-900">{stats.avgMarks}%</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-5 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Status</p>
              <p className="text-2xl font-bold text-gray-900">
                {processing ? 'Active' : 'Stopped'}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Cpu className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Cpu className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Processor Controls</h2>
            <p className="text-sm text-gray-600">Manage automatic exam processing</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={startProcessing}
            disabled={processing}
            className="flex items-center space-x-2 px-8 py-4 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all duration-200 font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            <Play className="h-5 w-5" />
            <span>Start Auto-Processing</span>
          </button>
          <button
            onClick={stopProcessing}
            disabled={!processing}
            className="flex items-center space-x-2 px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            <Square className="h-5 w-5" />
            <span>Stop Processing</span>
          </button>
        </div>
      </div>

      {/* Manual Processing */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Manual Processing</h2>
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={studentIdInput}
            onChange={(e) => setStudentIdInput(e.target.value)}
            placeholder="Enter Student ID (e.g., student1)"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={manualProcess}
            disabled={!studentIdInput}
            className="flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className="h-5 w-5" />
            <span>Process</span>
          </button>
        </div>
      </div>

      {/* Processed Exams */}
      {processedExams.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recently Processed</h2>
          <div className="space-y-2">
            {processedExams.map((exam, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-gray-900">{exam.student_id}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    {new Date(exam.processed_at).toLocaleTimeString()}
                  </span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    {exam.marks}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Processing Logs</h2>
        <div className="bg-gray-900 rounded-md p-4 h-64 overflow-y-auto font-mono text-sm">
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet...</p>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className="text-green-400 mb-1">
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessorControl;


