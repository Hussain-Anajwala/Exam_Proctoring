import React, { useState, useEffect } from 'react';
import { 
  Database as DatabaseIcon, 
  Search, 
  Edit, 
  Save,
  RefreshCw,
  Download,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { databaseApi } from '../../services/api';
import type { StudentRecord, DatabaseUpdate } from '../../types';

const Database: React.FC = () => {
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

  useEffect(() => {
    fetchAllRecords();
  }, []);

  const fetchAllRecords = async () => {
    try {
      const response = await databaseApi.getAllRecords();
      setRecords(response.results || []);
    } catch (err) {
      setError('Failed to fetch records');
      console.error('Fetch records error:', err);
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
      setRecords(response.results || []);
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
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <DatabaseIcon className="h-8 w-8 text-blue-600" />
          <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Distributed Database
              </h1>
              <p className="text-gray-600">
                Student records with 2PC protocol for updates
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchAllRecords}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={exportRecords}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

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

      {/* Update Form */}
      {selectedRecord && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Update Record - {selectedRecord.name}
          </h2>

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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

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
    </div>
  );
};

export default Database;
