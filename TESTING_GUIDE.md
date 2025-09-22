# 🎯 Complete Testing Guide - Full Stack Exam Proctoring System

## 📋 Table of Contents
- [Overview](#overview)
- [Dashboard Tab](#1-dashboard-tab)
- [Violation Detection Tab](#2-violation-detection-tab)
- [Clock Synchronization Tab](#3-clock-synchronization-tab)
- [Mutual Exclusion Tab](#4-mutual-exclusion-tab)
- [Exam Processing Tab](#5-exam-processing-tab)
- [Load Balancing Tab](#6-load-balancing-tab)
- [Database Tab](#7-database-tab)
- [Quick Test Sequence](#quick-test-sequence-for-all-tabs)
- [Visual Indicators](#visual-indicators)
- [Troubleshooting](#troubleshooting-tips)
- [Success Criteria](#success-criteria)

## Overview

This guide provides comprehensive testing instructions for all features of the Full Stack Exam Proctoring System. The system consists of 7 main tabs, each implementing different distributed systems concepts and algorithms.

---

## 1. 🏠 Dashboard Tab

### What to Test

#### System Status Indicators
- **System Health**: Green "System Online" indicator
- **Real-time Statistics**: Live counters for students, violations, terminated students, and exams
- **Component Status**: Status badges for all 6 system components

#### Auto-refresh Features
- Statistics update every 30 seconds automatically
- Component status changes in real-time
- Overall system health monitoring

#### Visual Elements
- Feature cards with icons for each system component
- Status color coding (green/yellow/red)
- Statistics counters with live data

### Expected Behavior
- Dashboard loads with complete system overview
- Statistics display current system state
- All 6 feature cards show with appropriate status indicators
- Real-time updates without manual refresh

---

## 2. 🛡️ Violation Detection Tab

### Test Scenarios

#### Report Violations
1. **Select Student** from dropdown:
   - Hussain (Roll: 58)
   - Saish (Roll: 59)
   - Khushal (Roll: 65)
   - Hasnain (Roll: 75)
   - Amritesh (Roll: 68)

2. **Set Question Number** (1-50)

3. **Choose Violation Type**:
   - 1st Violation (Warning) - Student gets warning, marks reduced
   - 2nd Violation (Termination) - Student gets terminated, exam ends

4. **Customize Warning Message**

5. **Click "Report Violation"**

#### Expected Results
- ✅ **Warning**: Student receives warning, marks reduced by 10%
- ❌ **Termination**: Student gets terminated, exam session ends
- 📊 **Marksheet Updates**: Real-time updates to student records
- 📈 **Statistics**: Violation counts update automatically

#### Marksheet Features
- View current marks for all students
- See violation counts per student
- Identify terminated students (red background highlighting)
- Export marksheet data as JSON

---

## 3. 🕐 Clock Synchronization Tab

### Test Scenarios

#### Add Participants
1. **Enter Role** (e.g., "teacher", "student1", "student2", "proctor")
2. **Set Time** using HH:MM:SS format or click "Now" for current time
3. **Click "Add Participant"**
4. **Repeat** for multiple participants (minimum 2 required)

#### Synchronization Process
1. **Add 3-4 participants** with different times
2. **Click "Start Synchronization"**
3. **Watch the Berkeley Algorithm**:
   - Participants register with the system
   - Average time is calculated
   - Individual adjustments are computed
   - All clocks synchronize to the average

#### Expected Results
- ✅ All participant clocks synchronized to average time
- 📊 Time differences displayed with +/- indicators
- 🔄 Adjustment values shown for each participant
- 📈 Comparison chart updates with synchronized times

#### Time Comparison Features
- Visual comparison of all participant times
- Time difference calculations
- Color-coded adjustments (green for positive, red for negative)

---

## 4. 🔒 Mutual Exclusion Tab

### Test Scenarios

#### Request Critical Section
1. **Modify Timestamps** for students (e.g., 1000, 1001, 1002)
2. **Click "Request"** for different students
3. **Watch Token-Based System**:
   - First request gets granted immediately
   - Subsequent requests get queued
   - Token transfers between students
   - Only one student can be active at a time

#### System Status Monitoring
- **Current Holder**: Shows who currently has the token
- **Request Queue**: Displays waiting students with timestamps
- **Real-time Updates**: Status refreshes every 2 seconds
- **Response History**: Tracks all token transfers and requests

#### Expected Behavior
- 🎯 Only one student active in critical section at a time
- 📋 Queue management works with proper ordering
- 🔄 Token transfers happen automatically
- 📊 Status updates in real-time with visual indicators

#### Student Management
- Edit timestamps for different students
- Request and release critical section access
- View detailed response history
- Reset simulation to start over

---

## 5. 📚 Exam Processing Tab

### Test Scenarios

#### Complete Exam Flow
1. **Set Student ID** (e.g., "student1", "student2")
2. **Click "Start Exam"** - loads questions from backend
3. **Answer Questions** by selecting multiple choice options (A, B, C, D)
4. **Click "Submit Exam"** - processes answers automatically
5. **Click "Release Marks"** - displays results and scoring

#### Question Interaction
- Multiple choice questions load dynamically
- Select answers using radio buttons
- Questions become disabled after submission
- Correct answers revealed after submission
- Immediate feedback on answer correctness

#### Expected Results
- ✅ Questions load with 4 options each
- 📊 Automatic scoring based on correct answers
- 🎯 Marks calculated and displayed as fraction and percentage
- 📈 Response history tracks all exam actions
- 🏆 Grade color coding (green/yellow/red based on performance)

#### Exam Status Tracking
- Current exam status (not started, in progress, submitted, marked)
- Real-time marks display
- Progress tracking through exam stages
- Reset functionality to start new exam

---

## 6. ⚖️ Load Balancing Tab

### Test Scenarios

#### Single Submission
1. **Click "Submit Single"**
2. **Watch Load Balancing Decision**:
   - Request goes to main server if under threshold
   - Request migrates to backup if threshold exceeded
3. **Check Processing Server** in response

#### Multiple Submissions
1. **Set Number of Submissions** (1-50)
2. **Click "Submit Multiple"**
3. **Watch Load Distribution**:
   - Local processing (green indicators)
   - Migration to backup server (blue indicators)
   - Threshold-based automatic decisions

#### System Monitoring
- **Local Inflight Count**: Current requests being processed
- **Migration Threshold**: Limit before backup migration
- **Queue Sizes**: Local and backup queue lengths
- **Processing Mode**: Shows current load balancing strategy

#### Expected Behavior
- 🎯 Intelligent load balancing decisions
- 📊 Automatic migration when threshold reached
- 🔄 Real-time status updates every 3 seconds
- 📈 Comprehensive submission history tracking
- 🎛️ Visual load indicators with color coding

#### Advanced Features
- Auto-submit option for continuous testing
- Clear submission history
- Real-time load visualization
- Server status monitoring

---

## 7. 🗄️ Database Tab

### Test Scenarios

#### Search & Filter
1. **Search by Name**: Enter student names like "Hussain", "Saish", "Khushal"
2. **Filter by Minimum Total**: Set minimum marks (e.g., 80, 60, 40)
3. **Click "Search"** to apply filters
4. **Click "Show All"** to reset and view all records

#### Update Records (2PC Protocol)
1. **Click on Any Student Record** in the table
2. **Record Highlights** and update form appears
3. **Modify Scores**:
   - MSE (0-20 marks)
   - ESE (0-40 marks)
4. **Click "Update Record"**
5. **Watch 2PC Protocol** in action:
   - Prepare phase
   - Commit phase
   - Rollback if needed

#### Expected Results
- ✅ Real-time search results with instant filtering
- 🔄 Two-Phase Commit protocol ensures data consistency
- 📊 Statistics update automatically (total records, average, highest score)
- 📁 Export functionality downloads JSON data
- 🎨 Color-coded grade badges (green/yellow/orange/red)

#### Database Features
- Interactive record selection
- Form validation for score inputs
- Success/error message handling
- Real-time statistics calculation
- Data export capabilities

---

## 🎮 Quick Test Sequence for All Tabs

### Complete Workflow Test
```
1. 🏠 Dashboard → Check system status and statistics
2. 🛡️ Violation → Report violation for Hussain (1st violation)
3. 🕐 Clock Sync → Add 3 participants, synchronize clocks
4. 🔒 Mutual Exclusion → Request critical section for Student 1
5. 📚 Exam Processing → Complete exam for student1
6. ⚖️ Load Balancing → Submit 10 multiple requests
7. 🗄️ Database → Search for "Hussain" and update his MSE score
```

### Individual Tab Testing
```
Dashboard: Verify all components show "active" status
Violation: Test both warning and termination scenarios
Clock Sync: Test with 4+ participants with different times
Mutex: Test token passing between 3 students
Exam: Complete full exam cycle (start → answer → submit → release)
Load Balance: Test threshold crossing with multiple submissions
Database: Test search, filter, and update operations
```

---

## 🎨 Visual Indicators

### Color Coding System
- ✅ **Green**: Success, active, online, high performance
- ⚠️ **Yellow**: Warning, waiting, caution, medium performance
- ❌ **Red**: Error, terminated, offline, low performance
- 🔵 **Blue**: Processing, info, neutral, backup server
- 🟣 **Purple**: Special actions, marks release, admin functions

### Interactive Elements
- **Buttons**: Hover effects, loading spinners, disabled states
- **Forms**: Validation feedback, error highlighting, success messages
- **Tables**: Row selection, sorting indicators, status badges
- **Charts**: Real-time data updates, interactive tooltips
- **Cards**: Status indicators, progress bars, statistics

### Real-time Features
- **Auto-refresh**: Statistics and status updates
- **Live Updates**: Queue changes, token transfers, load balancing
- **Instant Feedback**: Success/error messages, validation
- **Responsive Design**: Mobile-friendly layout, adaptive components

---

## 🛠️ Troubleshooting Tips

### Common Issues and Solutions

#### If Something Doesn't Work:
1. **Check Browser Console** for JavaScript errors
2. **Verify Backend is Running** on port 8000 (or configured port)
3. **Check Network Tab** for failed API calls
4. **Refresh the Page** if data seems stale
5. **Check CORS Settings** if API calls fail

#### Backend Connection Issues:
- Ensure Python server is running: `python start_server.py`
- Check if port 8000 is available
- Verify virtual environment is activated
- Check firewall settings

#### Frontend Issues:
- Clear browser cache and reload
- Check if all dependencies are installed: `npm install`
- Verify Vite development server is running: `npm run dev`
- Check proxy configuration in `vite.config.ts`

#### Data Not Loading:
- Verify API endpoints are correct
- Check backend logs for errors
- Ensure database/state is properly initialized
- Test API endpoints directly (e.g., `http://localhost:8000/api/v1/`)

#### UI Not Updating:
- Check React state management
- Verify component re-rendering
- Check for JavaScript errors in console
- Ensure proper event handling

### Debugging Steps:
1. Open browser Developer Tools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Check Application tab for local storage issues
5. Use React Developer Tools if available

---

## ✅ Success Criteria

### You'll Know Everything is Working When:

#### Functional Requirements:
- ✅ All 7 tabs load without errors
- ✅ Forms accept input and show proper validation
- ✅ API calls return data successfully
- ✅ Real-time updates work across all components
- ✅ Export/download functions work properly
- ✅ Error handling displays appropriate messages
- ✅ Responsive design works on different screen sizes

#### Performance Requirements:
- ✅ Page loads within 3 seconds
- ✅ API responses within 1 second
- ✅ Real-time updates refresh smoothly
- ✅ No memory leaks or performance degradation
- ✅ Smooth transitions and animations

#### User Experience Requirements:
- ✅ Intuitive navigation between tabs
- ✅ Clear visual feedback for all actions
- ✅ Consistent design language throughout
- ✅ Accessible form controls and labels
- ✅ Mobile-friendly responsive design

#### Technical Requirements:
- ✅ TypeScript compilation without errors
- ✅ ESLint passes without warnings
- ✅ All API endpoints respond correctly
- ✅ CORS configuration works properly
- ✅ Proxy setup functions correctly

### Testing Checklist:
- [ ] Dashboard shows live system status
- [ ] Violation detection reports and tracks violations
- [ ] Clock synchronization works with multiple participants
- [ ] Mutual exclusion manages token passing correctly
- [ ] Exam processing handles complete exam lifecycle
- [ ] Load balancing distributes requests intelligently
- [ ] Database operations use 2PC protocol correctly
- [ ] All forms validate input properly
- [ ] Error handling works for all scenarios
- [ ] Export functions download correct data
- [ ] Real-time updates work across all tabs
- [ ] Responsive design works on mobile devices

---

## 📞 Support

If you encounter any issues not covered in this guide:

1. Check the browser console for error messages
2. Verify the backend server is running and accessible
3. Ensure all dependencies are properly installed
4. Review the API documentation in the backend
5. Check the network connectivity between frontend and backend

---

*This testing guide covers all features of the Full Stack Exam Proctoring System. Each tab implements different distributed systems concepts and should be tested thoroughly to ensure proper functionality.*
