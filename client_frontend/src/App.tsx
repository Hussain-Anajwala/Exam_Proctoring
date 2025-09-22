import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './components/Dashboard/Dashboard';
import ViolationDetection from './components/ViolationDetection/ViolationDetection';
import ClockSync from './components/ClockSync/ClockSync';
import MutualExclusion from './components/MutualExclusion/MutualExclusion';
import ExamProcessing from './components/ExamProcessing/ExamProcessing';
import LoadBalancing from './components/LoadBalancing/LoadBalancing';
import Database from './components/Database/Database';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/violations" element={<ViolationDetection />} />
          <Route path="/clock-sync" element={<ClockSync />} />
          <Route path="/mutex" element={<MutualExclusion />} />
          <Route path="/exam" element={<ExamProcessing />} />
          <Route path="/load-balance" element={<LoadBalancing />} />
          <Route path="/database" element={<Database />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
