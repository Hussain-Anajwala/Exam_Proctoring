// API Response Types
export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}

// Task 1-3: Violation Detection Types
export interface ViolationReport {
  roll: number;
  name: string;
  warning: string;
  question_no: number;
  violation_no: number;
}

export interface ViolationResponse {
  status: string;
  message: string;
  violation_count: number;
  current_marks: number;
  student_name: string;
}

export interface Marksheet {
  marksheet: Record<string, number>;
  violations: Record<string, number>;
  terminated_students: number[];
}

// Task 4: Clock Synchronization Types
export interface ClockSyncRequest {
  role: string;
  time: string;
}

export interface ClockSyncResponse {
  status: string;
  participants?: string[];
  average_time?: string;
  adjustments?: Record<string, number>;
  updated_times?: Record<string, string>;
}

// Task 5: Mutual Exclusion Types
export interface MutexRequest {
  student_id: string;
  timestamp: number;
}

export interface MutexResponse {
  status: string;
  holder?: string;
  current_holder?: string;
  queue_position?: number;
  message: string;
  timestamp?: number;
  new_holder?: string;
}

export interface MutexStatus {
  current_holder: string;
  queue: Array<{ student: string; timestamp: number }>;
  queue_length: number;
}

// Task 6: Exam Processing Types
export interface ExamQuestion {
  q: string;
  options: string[];
  ans: string;
}

export interface ExamSubmission {
  student_id: string;
  answers: string[];
}

export interface ExamResponse {
  status: string;
  student_id?: string;
  questions?: ExamQuestion[];
  marks?: number;
  message: string;
}

export interface ExamStatus {
  student_id: string;
  status: string;
  marks?: number;
}

// Task 7: Load Balancing Types
export interface LoadBalanceSubmission {
  student_id: string;
  payload: Record<string, any>;
}

export interface LoadBalanceResponse {
  status: string;
  student_id: string;
  via: string;
  message: string;
}

export interface LoadBalanceStatus {
  local_inflight: number;
  received_count: number;
  migrate_threshold: number;
  local_queue_size: number;
  backup_queue_size: number;
}

// Task 8: Database Types
export interface StudentRecord {
  rn: string;
  name: string;
  isa: number;
  mse: number;
  ese: number;
  total: number;
}

export interface DatabaseUpdate {
  roll_number: string;
  mse: number;
  ese: number;
}

export interface DatabaseResponse {
  status: string;
  record?: StudentRecord;
  message?: string;
  updated_record?: StudentRecord;
  results?: StudentRecord[];
  count?: number;
  total_records?: number;
}

// System Status Types
export interface SystemStatus {
  system_status: string;
  timestamp: string;
  components: {
    exam_proctoring: string;
    clock_sync: string;
    mutual_exclusion: string;
    exam_processing: string;
    load_balancing: string;
    distributed_database: string;
  };
  statistics: {
    total_students: number;
    violations_reported: number;
    terminated_students: number;
    exam_submissions: number;
    database_records: number;
  };
}
