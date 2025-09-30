import React, { useState, useEffect } from 'react';
import { 
  Database as DatabaseIcon, 
  Search, 
  Edit, 
  Save,
  RefreshCw,
  Download,
  CheckCircle,
  XCircle,
  Lock
} from 'lucide-react';
import { databaseApi } from '../../services/api';
import type { StudentRecord, DatabaseUpdate } from '../../types';
import { useUser } from '../../contexts/UserContext';

const Database = () => {
  const { user, isTeacher } = useUser();
  const [records, setRecords] = useState<StudentRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<StudentRecord | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [minTotal, setMinTotal] = useState<number | ''>('');
  const [updateForm, setUpdateForm] = useState<DatabaseUpdate>({
    roll_number: '',
    mse: 0,
    ese: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [replicaStatus, setReplicaStatus] = useState<any>(null);
  const [showReplicaInfo, setShowReplicaInfo] = useState(false);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoSteps, setDemoSteps] = useState<string[]>([]);
  const [demoConfig, setDemoConfig] = useState({ failReplica: 'R1' });

  useEffect(() => {
    fetchAllRecords();
    fetchReplicaStatus();
  }, []);

  const fetchAllRecords = async () => {
    try {
      const response = await databaseApi.getAllRecords();
      setRecords(response.records || []);
    } catch (err) {
      setError('Failed to fetch records');
      console.error('Fetch records error:', err);
    }
  };

  const fetchReplicaStatus = async () => {
    try {
      const data = await databaseApi.getReplicaStatus();
      setReplicaStatus(data);
    } catch (err) {
      console.error('Failed to fetch replica status:', err);
    }
  };

  const simulateReplicaFailure = async (replicaName: string) => {
    try {
      await databaseApi.failReplica(replicaName);
      await fetchReplicaStatus();
    } catch (err) {
      console.error('Failed to simulate replica failure:', err);
    }
  };

  const simulateReplicaRecovery = async (replicaName: string) => {
    try {
      await databaseApi.recoverReplica(replicaName);
      await fetchReplicaStatus();
    } catch (err) {
      console.error('Failed to simulate replica recovery:', err);
    }
  };

  const searchRecords = async () => {
    setLoading(true);
    setError(null);

    try {
      const params: { name?: string; min_total?: number } = {};
      if (searchTerm) params.name = searchTerm;
      if (minTotal !== '') params.min_total = Number(minTotal);

      const response = await databaseApi.searchRecords(params);
      
      // Filter records based on replica status - only show if replica is online
      const filteredRecords = (response.records || []).filter(record => {
        // Check which replica contains this record
        const recordIndex = (response.records || []).indexOf(record);
        const replicaIndex = recordIndex % 3; // Assuming 3 replicas (R1, R2, R3)
        const replicaName = ['R1', 'R2', 'R3'][replicaIndex];
        
        // Only show if replica is online
        if (replicaStatus && replicaStatus.replicas) {
          const replica = replicaStatus.replicas[replicaName];
          return replica && replica.status === 'online';
        }
        return true; // If no replica status, show all
      });
      
      setRecords(filteredRecords);
      
      // Show message if some records were filtered out
      const totalRecords = response.records?.length || 0;
      if (filteredRecords.length < totalRecords) {
        setError(`Showing ${filteredRecords.length} of ${totalRecords} records. Some replicas are offline.`);
      }
    } catch (err) {
      setError('Failed to search records');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateRecord = async () => {
    if (!updateForm.roll_number) {
      setError('Please select a record to update');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await databaseApi.updateRecord(updateForm);
      setSuccess('Record updated successfully');
      await fetchAllRecords(); // Refresh the list
      setSelectedRecord(null);
      setUpdateForm({ roll_number: '', mse: 0, ese: 0 });
    } catch (err) {
      setError('Failed to update record');
      console.error('Update error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordSelect = (record: StudentRecord) => {
    setSelectedRecord(record);
    setUpdateForm({
      roll_number: record.rn,
      mse: record.mse,
      ese: record.ese
    });
  };

  const exportRecords = () => {
    const data = JSON.stringify(records, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'student_records.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const getGradeColor = (total: number) => {
    if (total >= 80) return 'text-green-600';
    if (total >= 60) return 'text-yellow-600';
    if (total >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getGradeBackground = (total: number) => {
    if (total >= 80) return 'bg-green-100';
    if (total >= 60) return 'bg-yellow-100';
    if (total >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-lg">
              <DatabaseIcon className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">
                Distributed Database
              </h1>
              <p className="text-blue-100 text-lg">
                Student records with 2PC protocol for updates
              </p>
              {!isTeacher && (
                <p className="text-blue-200 text-sm mt-1 flex items-center">
                  <Lock className="h-4 w-4 mr-1" />
                  Read-Only Mode
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchAllRecords}
              className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-all duration-200 border border-white/30"
            >
              <RefreshCw className="h-5 w-5" />
              <span className="font-medium">Refresh</span>
            </button>
            <button
              onClick={() => {
                setSelectedRecord(null);
                setUpdateForm({ roll_number: '', mse: 0, ese: 0 });
                setError(null);
                setSuccess(null);
                setSearchTerm('');
                setMinTotal('');
                fetchAllRecords();
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <XCircle className="h-4 w-4" />
              <span>Reset</span>
            </button>
            <button
              onClick={exportRecords}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            <button
              onClick={() => setShowReplicaInfo(!showReplicaInfo)}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
            >
              <DatabaseIcon className="h-4 w-4" />
              <span>{showReplicaInfo ? 'Hide' : 'Show'} Replicas</span>
            </button>
          </div>
        </div>
      </div>

      {/* Replica Management Section */}
      {showReplicaInfo && replicaStatus && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Replica Management & Chunk Distribution
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {Object.entries(replicaStatus.replicas || {}).map(([replicaName, info]: [string, any]) => (
              <div key={replicaName} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{replicaName}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    info.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {info.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-3">
                  Records: {info.record_count} | Chunks: {info.chunks?.length || 0}
                </div>
                
                {/* Show student names stored in this replica - ONLY if online */}
                {info.record_count > 0 && info.status === 'online' ? (
                  <div className="mb-3 p-2 bg-gray-50 rounded max-h-32 overflow-y-auto">
                    <p className="text-xs font-medium text-gray-700 mb-1">Students:</p>
                    <div className="flex flex-wrap gap-1">
                      {records
                        .filter(record => {
                          // Check if this record is in this replica
                          // For simplicity, we'll show all records divided by replica count
                          const replicaIndex = ['R1', 'R2', 'R3'].indexOf(replicaName);
                          const recordIndex = records.indexOf(record);
                          return recordIndex % 3 === replicaIndex || (recordIndex + 1) % 3 === replicaIndex;
                        })
                        .slice(0, 10)
                        .map((record, idx) => (
                          <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">
                            {record.name}
                          </span>
                        ))}
                      {info.record_count > 10 && (
                        <span className="text-xs text-gray-500">+{info.record_count - 10} more</span>
                      )}
                    </div>
                  </div>
                ) : info.status === 'offline' && info.record_count > 0 ? (
                  <div className="mb-3 p-2 bg-red-50 rounded border border-red-200">
                    <p className="text-xs font-medium text-red-700">
                      ⚠ Replica Offline - {info.record_count} records unavailable
                    </p>
                  </div>
                ) : null}
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => simulateReplicaFailure(replicaName)}
                    disabled={info.status === 'offline'}
                    className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Fail
                  </button>
                  <button
                    onClick={() => simulateReplicaRecovery(replicaName)}
                    disabled={info.status === 'online'}
                    className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Recover
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Chunk Distribution</h3>
              <div className="text-sm text-gray-600">
                <div>Total Chunks: {replicaStatus.total_chunks}</div>
                <div>Chunk Size: {replicaStatus.chunk_size} records</div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">2PC Protocol Status</h3>
              <div className="text-sm text-gray-600">
                <div>Replication Factor: 2</div>
                <div>Consistency: Strong</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Search & Filter
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="search-name" className="block text-sm font-medium text-gray-700 mb-2">
                Search by Name
              </label>
              <input
                id="search-name"
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter student name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="min-total" className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Total Marks
              </label>
              <input
                id="min-total"
                type="number"
                min="0"
                max="100"
                value={minTotal}
                onChange={(e) => setMinTotal(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="Enter minimum total..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={searchRecords}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              <span>{loading ? 'Searching...' : 'Search'}</span>
            </button>

            <button
              onClick={fetchAllRecords}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Show All</span>
            </button>
          </div>

          {/* Statistics */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Statistics</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Total Records:</span>
                <span className="font-medium text-gray-900">{records.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Average Total:</span>
                <span className="font-medium text-gray-900">
                  {records.length > 0 
                    ? Math.round(records.reduce((sum, r) => sum + r.total, 0) / records.length)
                    : 0}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Highest Score:</span>
                <span className="font-medium text-gray-900">
                  {records.length > 0 ? Math.max(...records.map(r => r.total)) : 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Records List */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Student Records ({records.length})
          </h2>

          {records.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Roll Number
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ISA
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      MSE
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ESE
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {records.map((record) => (
                    <tr 
                      key={record.rn} 
                      className={`hover:bg-gray-50 cursor-pointer ${
                        selectedRecord?.rn === record.rn ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleRecordSelect(record)}
                    >
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {record.rn}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {record.name}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {record.isa}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {record.mse}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {record.ese}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getGradeBackground(record.total)} ${getGradeColor(record.total)}`}>
                          {record.total}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRecordSelect(record);
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <DatabaseIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No records found</p>
              <p className="text-sm mt-2">
                Try adjusting your search criteria
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Update Form - Teacher Only */}
      {selectedRecord && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Update Record - {selectedRecord.name}
            </h2>
            {!isTeacher && (
              <div className="flex items-center space-x-2 px-3 py-1 bg-yellow-50 border border-yellow-200 rounded-md">
                <Lock className="h-4 w-4 text-yellow-600" />
                <span className="text-sm text-yellow-700">Read-Only (Teacher Access Required)</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="roll-number" className="block text-sm font-medium text-gray-700 mb-2">
                Roll Number
              </label>
              <input
                id="roll-number"
                type="text"
                value={updateForm.roll_number}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
              />
            </div>

            <div>
              <label htmlFor="mse-score" className="block text-sm font-medium text-gray-700 mb-2">
                MSE (0-20)
              </label>
              <input
                id="mse-score"
                type="number"
                min="0"
                max="20"
                value={updateForm.mse}
                onChange={(e) => setUpdateForm(prev => ({
                  ...prev,
                  mse: Number(e.target.value)
                }))}
                disabled={!isTeacher}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${!isTeacher ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''}`}
              />
            </div>

            <div>
              <label htmlFor="ese-score" className="block text-sm font-medium text-gray-700 mb-2">
                ESE (0-40)
              </label>
              <input
                id="ese-score"
                type="number"
                min="0"
                max="40"
                value={updateForm.ese}
                onChange={(e) => setUpdateForm(prev => ({
                  ...prev,
                  ese: Number(e.target.value)
                }))}
                disabled={!isTeacher}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${!isTeacher ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''}`}
              />
            </div>
          </div>

          {isTeacher && (
            <div className="mt-4 flex items-center space-x-4">
              <button
                onClick={updateRecord}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{loading ? 'Updating...' : 'Update Record'}</span>
            </button>

              <button
                onClick={() => {
                  setSelectedRecord(null);
                  setUpdateForm({ roll_number: '', mse: 0, ese: 0 });
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <XCircle className="h-4 w-4" />
                <span>Cancel</span>
              </button>
            </div>
          )}

          {success && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <div className="flex">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div className="ml-3">
                  <p className="text-sm text-green-700">{success}</p>
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
      )}

      {/* Demo Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Demo</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={async ()=>{
                if (demoRunning) return; setDemoRunning(true); setDemoSteps([]);
                try {
                  // Read → Update → Fail replica → Read
                  const all = await databaseApi.getAllRecords();
                  const rec = all.records && all.records[0];
                  if (!rec) { setDemoSteps(['No records']); setDemoRunning(false); return; }
                  setDemoSteps(prev=>[`Read ${rec.rn} total=${rec.total}`, ...prev]);
                  await databaseApi.updateRecord({ roll_number: rec.rn, mse: rec.mse, ese: rec.ese });
                  setDemoSteps(prev=>[`2PC update on ${rec.rn}`, ...prev]);
                  await databaseApi.failReplica(demoConfig.failReplica);
                  setDemoSteps(prev=>[`Replica ${demoConfig.failReplica} failed`, ...prev]);
                  await fetchReplicaStatus();
                  const read = await databaseApi.readRecord(rec.rn);
                  setDemoSteps(prev=>[`Read after failure via ${read.replica}`, ...prev]);
                } catch (e) {
                  console.error(e);
                  setDemoSteps(prev=>['Demo error - see console', ...prev]);
                } finally {
                  setDemoRunning(false);
                }
              }}
              disabled={demoRunning}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {demoRunning ? 'Running...' : 'Run Demo'}
            </button>
            <button 
              onClick={() => {
                setDemoSteps([]);
                setError(null);
                setSuccess(null);
                fetchAllRecords();
                fetchReplicaStatus();
              }} 
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Reset
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Fail Replica</label>
            <select value={demoConfig.failReplica} onChange={(e)=>setDemoConfig({ failReplica: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-md">
              <option value="R1">R1</option>
              <option value="R2">R2</option>
              <option value="R3">R3</option>
            </select>
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

export default Database;
