import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Clock, 
  Lock, 
  BookOpen, 
  Loader, 
  Database, 
  Activity,
  Users,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { systemApi, healthCheck } from '../../services/api';
import type { SystemStatus } from '../../types';

const Dashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isHealthy, setIsHealthy] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        setLoading(true);
        const [health, status] = await Promise.all([
          healthCheck(),
          systemApi.getSystemStatus()
        ]);
        setIsHealthy(health);
        setSystemStatus(status);
        setError(null);
      } catch (err) {
        setError('Failed to fetch system status');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      name: 'Violation Detection',
      description: 'Real-time violation reporting and tracking',
      icon: Shield,
      status: systemStatus?.components.exam_proctoring || 'unknown',
      stats: {
        label: 'Violations Reported',
        value: systemStatus?.statistics.violations_reported || 0
      }
    },
    {
      name: 'Clock Synchronization',
      description: 'Berkeley clock synchronization system',
      icon: Clock,
      status: systemStatus?.components.clock_sync || 'unknown',
      stats: {
        label: 'Participants',
        value: 'Multi-participant'
      }
    },
    {
      name: 'Mutual Exclusion',
      description: 'Distributed mutual exclusion algorithm',
      icon: Lock,
      status: systemStatus?.components.mutual_exclusion || 'unknown',
      stats: {
        label: 'Active Sessions',
        value: 'Token-based'
      }
    },
    {
      name: 'Exam Processing',
      description: 'Automated exam processing and scoring',
      icon: BookOpen,
      status: systemStatus?.components.exam_processing || 'unknown',
      stats: {
        label: 'Exams Submitted',
        value: systemStatus?.statistics.exam_submissions || 0
      }
    },
    {
      name: 'Load Balancing',
      description: 'Dynamic load balancing with backup migration',
      icon: Loader,
      status: systemStatus?.components.load_balancing || 'unknown',
      stats: {
        label: 'Processing Mode',
        value: 'Auto-migration'
      }
    },
    {
      name: 'Distributed Database',
      description: 'Database with 2PC protocol',
      icon: Database,
      status: systemStatus?.components.distributed_database || 'unknown',
      stats: {
        label: 'Records',
        value: systemStatus?.statistics.database_records || 0
      }
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <XCircle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Exam Proctoring System
            </h1>
            <p className="mt-2 text-gray-600">
              Unified system combining all 8 exam proctoring tasks
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {isHealthy ? (
              <CheckCircle className="h-8 w-8 text-green-500" />
            ) : (
              <XCircle className="h-8 w-8 text-red-500" />
            )}
            <span className={`text-sm font-medium ${
              isHealthy ? 'text-green-700' : 'text-red-700'
            }`}>
              {isHealthy ? 'System Online' : 'System Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* System Statistics */}
      {systemStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Students</p>
                <p className="text-2xl font-bold text-gray-900">
                  {systemStatus.statistics.total_students}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Violations</p>
                <p className="text-2xl font-bold text-gray-900">
                  {systemStatus.statistics.violations_reported}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Terminated</p>
                <p className="text-2xl font-bold text-gray-900">
                  {systemStatus.statistics.terminated_students}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Exams</p>
                <p className="text-2xl font-bold text-gray-900">
                  {systemStatus.statistics.exam_submissions}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <div key={feature.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Icon className="h-8 w-8 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    {feature.name}
                  </h3>
                </div>
                {getStatusIcon(feature.status)}
              </div>
              
              <p className="text-gray-600 mb-4">{feature.description}</p>
              
              <div className="flex items-center justify-between">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(feature.status)}`}>
                  {feature.status}
                </span>
                <div className="text-right">
                  <p className="text-sm text-gray-600">{feature.stats.label}</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {feature.stats.value}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* System Info */}
      {systemStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            System Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Last Updated</p>
              <p className="text-sm font-medium text-gray-900">
                {new Date(systemStatus.timestamp).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Overall Status</p>
              <p className="text-sm font-medium text-gray-900">
                {systemStatus.system_status}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
