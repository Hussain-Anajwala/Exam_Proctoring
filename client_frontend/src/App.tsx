import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';
import Layout from './components/Layout/Layout';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';
import ViolationDetection from './components/ViolationDetection/ViolationDetection';
import ClockSync from './components/ClockSync/ClockSync';
import MutualExclusion from './components/MutualExclusion/MutualExclusion';
import ExamProcessing from './components/ExamProcessing/ExamProcessing';
import LoadBalancing from './components/LoadBalancing/LoadBalancing';
import Database from './components/Database/Database';
import TeacherDashboard from './components/Teacher/TeacherDashboard';
import ProcessorControl from './components/Processor/ProcessorControl';
import StudentPortal from './components/Student/StudentPortal';
import SubmissionsList from './components/Submissions/SubmissionsList';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <Router>
      <UserProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/teacher" element={<TeacherDashboard />} />
                  <Route path="/processor" element={<ProcessorControl />} />
                  <Route path="/student" element={<StudentPortal />} />
                  <Route path="/submissions" element={<SubmissionsList />} />
                  <Route path="/violations" element={<ViolationDetection />} />
                  <Route path="/clock-sync" element={<ClockSync />} />
                  <Route path="/mutex" element={<MutualExclusion />} />
                  <Route path="/exam" element={<ExamProcessing />} />
                  <Route path="/load-balance" element={<LoadBalancing />} />
                  <Route path="/database" element={<Database />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </UserProvider>
    </Router>
  );
}

export default App;
