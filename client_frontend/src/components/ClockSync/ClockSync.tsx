import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Users, 
  RefreshCw, 
  CheckCircle, 
  XCircle,
  Play,
  Plus,
  Trash2
} from 'lucide-react';
import { clockApi } from '../../services/api';
import type { ClockSyncRequest, ClockSyncResponse } from '../../types';

interface Participant {
  role: string;
  time: string;
}

const ClockSync: React.FC = () => {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [newParticipant, setNewParticipant] = useState<Participant>({
    role: '',
    time: ''
  });
  const [syncResult, setSyncResult] = useState<ClockSyncResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateCurrentTime = () => {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
  };

  const addParticipant = () => {
    if (newParticipant.role && newParticipant.time) {
      setParticipants(prev => [...prev, { ...newParticipant }]);
      setNewParticipant({ role: '', time: '' });
    }
  };

  const removeParticipant = (index: number) => {
    setParticipants(prev => prev.filter((_, i) => i !== index));
  };

  const registerAllParticipants = async () => {
    setLoading(true);
    setError(null);

    try {
      for (const participant of participants) {
        await clockApi.registerParticipant(participant);
      }
    } catch (err) {
      setError('Failed to register participants');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const startSynchronization = async () => {
    if (participants.length < 2) {
      setError('Need at least 2 participants for synchronization');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // First register all participants
      await registerAllParticipants();
      
      // Then start synchronization
      const result = await clockApi.startSynchronization();
      setSyncResult(result);
    } catch (err) {
      setError('Failed to start synchronization');
      console.error('Sync error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTimeDifference = (time1: string, time2: string) => {
    const [h1, m1, s1] = time1.split(':').map(Number);
    const [h2, m2, s2] = time2.split(':').map(Number);
    const seconds1 = h1 * 3600 + m1 * 60 + s1;
    const seconds2 = h2 * 3600 + m2 * 60 + s2;
    return seconds2 - seconds1;
  };

  const formatTimeDifference = (seconds: number) => {
    const sign = seconds >= 0 ? '+' : '';
    return `${sign}${seconds}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3">
          <Clock className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Berkeley Clock Synchronization
            </h1>
            <p className="text-gray-600">
              Synchronize clocks across multiple participants
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Participants Management */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Participants
          </h2>

          {/* Add New Participant */}
          <div className="space-y-4 mb-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role
                </label>
                <input
                  type="text"
                  value={newParticipant.role}
                  onChange={(e) => setNewParticipant(prev => ({
                    ...prev,
                    role: e.target.value
                  }))}
                  placeholder="e.g., teacher, student1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time (HH:MM:SS)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newParticipant.time}
                    onChange={(e) => setNewParticipant(prev => ({
                      ...prev,
                      time: e.target.value
                    }))}
                    placeholder="10:30:45"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => setNewParticipant(prev => ({
                      ...prev,
                      time: generateCurrentTime()
                    }))}
                    className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                  >
                    Now
                  </button>
                </div>
              </div>
            </div>
            <button
              onClick={addParticipant}
              disabled={!newParticipant.role || !newParticipant.time}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Add Participant</span>
            </button>
          </div>

          {/* Participants List */}
          <div className="space-y-2">
            {participants.map((participant, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-900">{participant.role}</p>
                    <p className="text-sm text-gray-600">{participant.time}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeParticipant(index)}
                  className="p-1 text-red-600 hover:bg-red-100 rounded-md transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {participants.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No participants added yet</p>
            </div>
          )}

          <div className="mt-6">
            <button
              onClick={startSynchronization}
              disabled={loading || participants.length < 2}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>
                {loading ? 'Synchronizing...' : 'Start Synchronization'}
              </span>
            </button>
          </div>
        </div>

        {/* Synchronization Results */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Synchronization Results
          </h2>

          {syncResult ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-sm font-medium text-green-800">
                    Synchronization Complete
                  </span>
                </div>
                <p className="text-sm text-green-700">
                  All clocks have been synchronized successfully
                </p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Average Time
                </h3>
                <p className="text-lg font-mono font-semibold text-gray-900">
                  {syncResult.average_time}
                </p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Adjustments Made
                </h3>
                <div className="space-y-2">
                  {syncResult.adjustments && Object.entries(syncResult.adjustments).map(([role, adjustment]) => (
                    <div key={role} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                      <span className="text-sm font-medium text-gray-900">{role}</span>
                      <span className={`text-sm font-mono ${
                        adjustment >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatTimeDifference(adjustment)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Updated Times
                </h3>
                <div className="space-y-2">
                  {syncResult.updated_times && Object.entries(syncResult.updated_times).map(([role, time]) => (
                    <div key={role} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                      <span className="text-sm font-medium text-gray-900">{role}</span>
                      <span className="text-sm font-mono text-gray-900">{time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No synchronization results yet</p>
              <p className="text-sm mt-2">
                Add participants and start synchronization to see results
              </p>
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
      </div>

      {/* Time Comparison Chart */}
      {participants.length > 1 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Time Comparison
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {participants.map((participant, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-md">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    {participant.role}
                  </span>
                  <span className="text-xs text-gray-500">
                    {participant.time}
                  </span>
                </div>
                <div className="space-y-1">
                  {participants.map((other, otherIndex) => {
                    if (index === otherIndex) return null;
                    const diff = getTimeDifference(participant.time, other.time);
                    return (
                      <div key={otherIndex} className="flex justify-between text-xs">
                        <span className="text-gray-600">vs {other.role}:</span>
                        <span className={`font-mono ${
                          diff >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatTimeDifference(diff)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClockSync;
