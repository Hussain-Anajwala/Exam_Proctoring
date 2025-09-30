import React, { useState, useEffect } from 'react';
import { 
  Lock, 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Play,
  Square
} from 'lucide-react';
import { mutexApi } from '../../services/api';
import type { MutexRequest, MutexResponse, MutexStatus } from '../../types';

interface Student {
  id: string;
  name: string;
  timestamp: number;
  status: 'waiting' | 'active' | 'completed';
}

const MutualExclusion: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([
    { id: 's1', name: 'Student 1', timestamp: 1000, status: 'waiting' },
    { id: 's2', name: 'Student 2', timestamp: 1001, status: 'waiting' },
    { id: 's3', name: 'Student 3', timestamp: 1002, status: 'waiting' }
  ]);
  const [mutexStatus, setMutexStatus] = useState<MutexStatus | null>(null);
  const [responses, setResponses] = useState<MutexResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoSteps, setDemoSteps] = useState<string[]>([]);
  const [demoConfig, setDemoConfig] = useState({
    t1: 1000,
    t2: 1001,
    t3: 1002,
  });

  useEffect(() => {
    fetchMutexStatus();
    const interval = setInterval(fetchMutexStatus, 2000); // Refresh every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMutexStatus = async () => {
    console.log('Refresh button clicked - Mutual Exclusion');
    try {
      const status = await mutexApi.getMutexStatus();
      console.log('Mutex status refreshed:', status);
      setMutexStatus({...status}); // Force new object reference
    } catch (err) {
      console.error('Failed to fetch mutex status:', err);
    }
  };

  const requestCriticalSection = async (student: Student) => {
    setLoading(true);
    setError(null);

    try {
      const request: MutexRequest = {
        student_id: student.id,
        timestamp: student.timestamp
      };

      const response = await mutexApi.requestCriticalSection(request);
      setResponses(prev => [...prev, response]);

      // Update student status based on response
      if (response.status === 'granted') {
        setStudents(prev => prev.map(s => 
          s.id === student.id 
            ? { ...s, status: 'active' as const }
            : s.status === 'active' 
              ? { ...s, status: 'waiting' as const }
              : s
        ));
      } else if (response.status === 'queued') {
        setStudents(prev => prev.map(s => 
          s.id === student.id 
            ? { ...s, status: 'waiting' as const }
            : s
        ));
        // Start polling for grant
        pollForGrant(student.id);
      }
    } catch (err) {
      setError('Failed to request critical section');
      console.error('Request error:', err);
    } finally {
      setLoading(false);
    }
  };

  const pollForGrant = async (studentId: string) => {
    const maxAttempts = 30; // Poll for up to 60 seconds
    let attempts = 0;
    
    const poll = async () => {
      try {
        const data = await mutexApi.checkGrant(studentId);

        if (data.status === 'granted') {
          setStudents(prev => prev.map(s => 
            s.id === studentId ? { ...s, status: 'active' as const } : s
          ));
          setResponses(prev => [...prev, data]);
          return;
        }
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000); // Poll every 2 seconds
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };
    
    poll();
  };

  const releaseCriticalSection = async (studentId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await mutexApi.releaseCriticalSection(studentId);
      setResponses(prev => [...prev, response]);

      // Update student status back to waiting so they can request again
      setStudents(prev => prev.map(s => 
        s.id === studentId 
          ? { ...s, status: 'waiting' as const }
          : s
      ));
    } catch (err) {
      setError('Failed to release critical section');
      console.error('Release error:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetSimulation = async () => {
    console.log('Reset button clicked - Mutual Exclusion');
    setStudents([
      { id: 's1', name: 'Student 1', timestamp: 1000, status: 'waiting' },
      { id: 's2', name: 'Student 2', timestamp: 1001, status: 'waiting' },
      { id: 's3', name: 'Student 3', timestamp: 1002, status: 'waiting' }
    ]);
    setResponses([]);
    setError(null);
    setMutexStatus(null); // Clear first
    
    try {
      // Reset backend mutex state by releasing any current holder
      const status = await mutexApi.getMutexStatus();
      if (status.current_holder && status.current_holder !== 'Teacher') {
        await mutexApi.releaseCriticalSection(status.current_holder);
        console.log('Backend mutex reset - released current holder');
      }
    } catch (err) {
      console.error('Failed to reset backend mutex:', err);
    }
    
    setTimeout(() => fetchMutexStatus(), 100); // Then refresh
    console.log('Simulation reset complete');
  };

  const logDemo = (msg: string) => setDemoSteps(prev => [msg, ...prev].slice(0, 50));

  const resetDemo = () => {
    setDemoRunning(false);
    setDemoSteps([]);
    resetSimulation();
  };

  const runDemo = async () => {
    if (demoRunning) return;
    setDemoRunning(true);
    setDemoSteps([]);
    setError(null);
    try {
      // Request sequence s1 -> s2 -> s3, release in order
      const r1 = await mutexApi.requestCriticalSection({ student_id: 's1', timestamp: demoConfig.t1 });
      logDemo(`s1 request → ${r1.status}`);
      await new Promise(r => setTimeout(r, 600));
      const r2 = await mutexApi.requestCriticalSection({ student_id: 's2', timestamp: demoConfig.t2 });
      logDemo(`s2 request → ${r2.status}`);
      await new Promise(r => setTimeout(r, 600));
      const r3 = await mutexApi.requestCriticalSection({ student_id: 's3', timestamp: demoConfig.t3 });
      logDemo(`s3 request → ${r3.status}`);
      await new Promise(r => setTimeout(r, 1000));
      const rel1 = await mutexApi.releaseCriticalSection('s1');
      logDemo(`s1 release → ${rel1.status}`);
      await new Promise(r => setTimeout(r, 1000));
      const rel2 = await mutexApi.releaseCriticalSection('s2');
      logDemo(`s2 release → ${rel2.status}`);
      await new Promise(r => setTimeout(r, 1000));
      const rel3 = await mutexApi.releaseCriticalSection('s3');
      logDemo(`s3 release → ${rel3.status}`);
      fetchMutexStatus();
    } catch (e) {
      setError('Demo failed');
      console.error(e);
    } finally {
      setDemoRunning(false);
    }
  };

  const simulateSequence = async () => {
    setLoading(true);
    setError(null);
    setResponses([]);
    
    try {
      // Step 1: s1 requests CS
      await requestCriticalSection(students[0]);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Step 2: s2 and s3 request CS (while s1 is in CS)
      await requestCriticalSection(students[1]);
      await new Promise(resolve => setTimeout(resolve, 500));
      await requestCriticalSection(students[2]);
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Step 3: s1 releases CS (s2 should get it)
      await releaseCriticalSection('s1');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Step 4: s2 releases CS (s3 should get it)
      await releaseCriticalSection('s2');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Step 5: s3 releases CS
      await releaseCriticalSection('s3');
      
    } catch (err) {
      setError('Simulation failed');
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'waiting':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'completed':
        return <XCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <Lock className="h-5 w-5 text-blue-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'waiting':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getResponseStatusColor = (status: string) => {
    switch (status) {
      case 'granted':
        return 'bg-green-100 text-green-800';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      case 'transferred':
        return 'bg-blue-100 text-blue-800';
      case 'returned':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Lock className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Mutual Exclusion
              </h1>
              <p className="text-gray-600">
                Token-based mutual exclusion algorithm simulation
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchMutexStatus}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={simulateSequence}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              <span>Simulate Sequence</span>
            </button>
            <button
              onClick={resetSimulation}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <Square className="h-4 w-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Students Management */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Students
          </h2>

          <div className="space-y-4">
            {students.map((student) => (
              <div key={student.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(student.status)}
                    <div>
                      <h3 className="font-medium text-gray-900">{student.name}</h3>
                      <p className="text-sm text-gray-600">ID: {student.id}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(student.status)}`}>
                    {student.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Timestamp
                    </label>
                    <input
                      type="number"
                      value={student.timestamp}
                      onChange={(e) => setStudents(prev => prev.map(s => 
                        s.id === student.id 
                          ? { ...s, timestamp: Number(e.target.value) }
                          : s
                      ))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Actions
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => requestCriticalSection(student)}
                        disabled={loading || student.status === 'active' || student.status === 'completed'}
                        className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                      >
                        <Play className="h-3 w-3" />
                        <span>Request</span>
                      </button>
                      <button
                        onClick={() => releaseCriticalSection(student.id)}
                        disabled={loading || student.status !== 'active'}
                        className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                      >
                        <Square className="h-3 w-3" />
                        <span>Release</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
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

        {/* System Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            System Status
          </h2>

          {mutexStatus ? (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-md">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Current Holder</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {mutexStatus.current_holder}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Queue Length</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {mutexStatus.queue_length}
                  </span>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Request Queue
                </h3>
                {mutexStatus.queue.length > 0 ? (
                  <div className="space-y-2">
                    {mutexStatus.queue.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                        <span className="text-sm font-medium text-gray-900">
                          {item.student}
                        </span>
                        <span className="text-sm text-gray-600">
                          t={item.timestamp}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No requests in queue
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Lock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No system status available</p>
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
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getResponseStatusColor(response.status)}`}>
                    {response.status.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">{response.message}</p>
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                  {response.holder && (
                    <div>
                      <span className="font-medium">Holder:</span> {response.holder}
                    </div>
                  )}
                  {response.timestamp && (
                    <div>
                      <span className="font-medium">Timestamp:</span> {response.timestamp}
                    </div>
                  )}
                  {response.queue_position && (
                    <div>
                      <span className="font-medium">Queue Position:</span> {response.queue_position}
                    </div>
                  )}
                  {response.new_holder && (
                    <div>
                      <span className="font-medium">New Holder:</span> {response.new_holder}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No responses yet</p>
            <p className="text-sm mt-2">
              Request critical section access to see responses
            </p>
          </div>
        )}
      </div>

      {/* Demo Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Demo</h2>
          <div className="flex items-center space-x-2">
            <button onClick={runDemo} disabled={demoRunning} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">{demoRunning ? 'Running...' : 'Run Demo'}</button>
            <button onClick={resetDemo} className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Reset</button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timestamp s1</label>
            <input type="number" value={demoConfig.t1} onChange={(e)=>setDemoConfig(prev=>({...prev, t1: Number(e.target.value)}))} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timestamp s2</label>
            <input type="number" value={demoConfig.t2} onChange={(e)=>setDemoConfig(prev=>({...prev, t2: Number(e.target.value)}))} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timestamp s3</label>
            <input type="number" value={demoConfig.t3} onChange={(e)=>setDemoConfig(prev=>({...prev, t3: Number(e.target.value)}))} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 max-h-48 overflow-auto text-sm">
          {demoSteps.length === 0 ? <p className="text-gray-500">No demo steps yet.</p> : (
            <ul className="space-y-1">{demoSteps.map((s,i)=>(<li key={i}>{s}</li>))}</ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default MutualExclusion;
