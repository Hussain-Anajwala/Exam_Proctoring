import axios from 'axios';
import type {
  ViolationReport,
  ViolationResponse,
  Marksheet,
  ClockSyncRequest,
  ClockSyncResponse,
  MutexRequest,
  MutexResponse,
  MutexStatus,
  ExamSubmission,
  ExamResponse,
  ExamStatus,
  LoadBalanceSubmission,
  LoadBalanceResponse,
  LoadBalanceStatus,
  DatabaseUpdate,
  DatabaseResponse,
  SystemStatus
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Task 1-3: Violation Detection API
export const violationApi = {
  reportViolation: async (violation: ViolationReport): Promise<ViolationResponse> => {
    const response = await api.post('/violation/report', violation);
    return response.data;
  },

  getViolationStatus: async (roll: number): Promise<ViolationResponse> => {
    const response = await api.get(`/violation/status/${roll}`);
    return response.data;
  },

  getMarksheet: async (): Promise<Marksheet> => {
    const response = await api.get('/violation/marksheet');
    return response.data;
  },
};

// Task 4: Clock Synchronization API
export const clockApi = {
  registerParticipant: async (request: ClockSyncRequest): Promise<ClockSyncResponse> => {
    const response = await api.post('/clock/register', request);
    return response.data;
  },

  startSynchronization: async (): Promise<ClockSyncResponse> => {
    const response = await api.post('/clock/sync');
    return response.data;
  },

  getClockStatus: async (): Promise<ClockSyncResponse> => {
    const response = await api.get('/clock/status');
    return response.data;
  },
};

// Task 5: Mutual Exclusion API
export const mutexApi = {
  requestCriticalSection: async (request: MutexRequest): Promise<MutexResponse> => {
    const response = await api.post('/mutex/request', request);
    return response.data;
  },

  releaseCriticalSection: async (studentId: string): Promise<MutexResponse> => {
    const response = await api.post('/mutex/release', { student_id: studentId });
    return response.data;
  },

  getMutexStatus: async (): Promise<MutexStatus> => {
    const response = await api.get('/mutex/status');
    return response.data;
  },
  checkGrant: async (studentId: string): Promise<MutexResponse> => {
    const response = await api.get(`/mutex/check/${studentId}`);
    return response.data;
  },
};

// Task 6: Exam Processing API
export const examApi = {
  getQuestions: async (): Promise<{ questions: any[] }> => {
    const response = await api.get('/exam/questions');
    return response.data;
  },

  startExam: async (studentId: string): Promise<ExamResponse> => {
    const response = await api.post(`/exam/start/${studentId}`);
    return response.data;
  },

  submitExam: async (submission: ExamSubmission): Promise<ExamResponse> => {
    const response = await api.post('/exam/submit', submission);
    return response.data;
  },

  releaseMarks: async (studentId: string): Promise<ExamResponse> => {
    const response = await api.post(`/exam/release-marks/${studentId}`);
    return response.data;
  },

  getExamStatus: async (studentId: string): Promise<ExamStatus> => {
    const response = await api.get(`/exam/status/${studentId}`);
    return response.data;
  },
};

// Task 7: Load Balancing API
export const loadBalanceApi = {
  submitForProcessing: async (submission: LoadBalanceSubmission): Promise<LoadBalanceResponse> => {
    const response = await api.post('/load-balance/submit', submission);
    return response.data;
  },

  getLoadBalanceStatus: async (): Promise<LoadBalanceStatus> => {
    const response = await api.get('/load-balance/status');
    return response.data;
  },
};

// Task 8: Database API
export const databaseApi = {
  readRecord: async (rollNumber: string): Promise<DatabaseResponse> => {
    const response = await api.get(`/database/read/${rollNumber}`);
    return response.data;
  },

  updateRecord: async (update: DatabaseUpdate): Promise<DatabaseResponse> => {
    const response = await api.post('/database/update', update);
    return response.data;
  },

  getAllRecords: async (): Promise<DatabaseResponse> => {
    const response = await api.get('/database/all');
    return response.data;
  },

  searchRecords: async (params: { name?: string; min_total?: number }): Promise<DatabaseResponse> => {
    const response = await api.get('/database/search', { params });
    return response.data;
  },
  getReplicaStatus: async (): Promise<any> => {
    const response = await api.get('/database/replicas');
    return response.data;
  },
  failReplica: async (replicaName: string): Promise<any> => {
    const response = await api.post(`/database/replica/${replicaName}/fail`);
    return response.data;
  },
  recoverReplica: async (replicaName: string): Promise<any> => {
    const response = await api.post(`/database/replica/${replicaName}/recover`);
    return response.data;
  },
};

// System Status API
export const systemApi = {
  getSystemStatus: async (): Promise<SystemStatus> => {
    const response = await api.get('/status');
    return response.data;
  },

  getApiDocs: async (): Promise<any> => {
    const response = await api.get('/docs');
    return response.data;
  },
  startSession: async (durationMinutes: number): Promise<any> => {
    const response = await api.post('/session/start', null, { params: { duration_minutes: durationMinutes } });
    return response.data;
  },
  stopSession: async (): Promise<any> => {
    const response = await api.post('/session/stop');
    return response.data;
  },
  resetSession: async (): Promise<any> => {
    const response = await api.post('/session/reset');
    return response.data;
  },
  getSessionStatus: async (): Promise<any> => {
    const response = await api.get('/session/status');
    return response.data;
  },
};

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    // Use absolute /api to avoid /api/v1 prefix for health endpoint
    const response = await axios.get('/api/health');
    return response.status === 200 && response.data.status === 'ok';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

export default api;
