import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  XCircle,
  ArrowRight
} from 'lucide-react';
import { systemApi, healthCheck } from '../../services/api';
import type { SystemStatus } from '../../types';

const Dashboard = () => {
  const navigate = useNavigate();
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

  const navigateToTask = (taskPath: string) => {
    navigate(taskPath);
  };

  const features = [
    {
      name: 'Violation Detection',
      description: 'Real-time violation reporting and tracking',
      icon: Shield,
      status: systemStatus?.components.exam_proctoring || 'unknown',
      path: '/violations',
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
      path: '/clock-sync',
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
      path: '/mutex',
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
      path: '/exam',
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
      path: '/load-balance',
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
      path: '/database',
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
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Exam Proctoring System
            </h1>
            <p className="text-blue-100 text-lg">
              Unified distributed system for secure exam management
            </p>
          </div>
          <div className="flex items-center space-x-3 bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
            {isHealthy ? (
              <CheckCircle className="h-8 w-8 text-green-300" />
            ) : (
              <XCircle className="h-8 w-8 text-red-300" />
            )}
            <div>
              <p className="text-xs text-blue-100">System Status</p>
              <p className="text-sm font-bold">
                {isHealthy ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* System Statistics */}
      {systemStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total Students</p>
                <p className="text-3xl font-bold text-gray-900">
                  {systemStatus.statistics.total_students}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Violations</p>
                <p className="text-3xl font-bold text-gray-900">
                  {systemStatus.statistics.violations_reported}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Terminated</p>
                <p className="text-3xl font-bold text-gray-900">
                  {systemStatus.statistics.terminated_students}
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Exams</p>
                <p className="text-3xl font-bold text-gray-900">
                  {systemStatus.statistics.exam_submissions}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <BookOpen className="h-8 w-8 text-green-600" />
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
            <div 
              key={feature.name} 
              onClick={() => navigateToTask(feature.path)}
              className="group bg-white rounded-xl shadow-md hover:shadow-xl cursor-pointer transition-all duration-300 overflow-hidden border border-gray-100 hover:border-blue-300"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                    <Icon className="h-8 w-8 text-blue-600" />
                  </div>
                  {getStatusIcon(feature.status)}
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {feature.name}
                </h3>
                
                <p className="text-gray-600 mb-4 text-sm">{feature.description}</p>
                
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(feature.status)}`}>
                    {feature.status}
                  </span>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">{feature.stats.label}</p>
                    <p className="text-lg font-bold text-gray-900">
                      {feature.stats.value}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="px-6 py-3 bg-gray-50 group-hover:bg-blue-50 transition-colors">
                <div className="flex items-center justify-between text-blue-600 text-sm font-medium">
                  <span>Open Task</span>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
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
