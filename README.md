# 🎓 Distributed Exam Proctoring System

A comprehensive, full-stack exam proctoring system built with **React**, **TypeScript**, **FastAPI**, and modern web technologies. Features role-based access control, real-time exam management, and a beautiful, professional UI.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![React](https://img.shields.io/badge/React-19-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)

---

## 📸 Screenshots

### Login Page
Modern login interface with role selection (Student, Teacher, Processor)

### Student Portal
Complete exam-taking experience with timer, progress tracking, and results display

### Teacher Dashboard
Manage student submissions, release marks, and reset exam attempts

### Submissions List
Real-time overview of all student submissions with statistics

---

## ✨ Features

### 🔐 **Role-Based Access Control**
- **Students**: Take exams, view results
- **Teachers**: Release marks, reset exams, edit database
- **Processors**: Auto-process submissions, view logs

### 📝 **Exam Management**
- 5 multiple-choice questions
- 30-minute timer with auto-submit
- Real-time progress tracking
- Percentage-based scoring (20% per question)
- Beautiful results display with progress bars

### 👨‍🏫 **Teacher Features**
- Release marks to individual students
- Reset exam attempts
- View all submissions with filters
- Edit student database records (teacher-only)
- Bulk operations support

### 🤖 **Processor Features**
- Automatic exam evaluation
- Manual processing capability
- Real-time processing logs
- Statistics dashboard

### 💾 **Database Management**
- Distributed database with 2PC protocol
- 30+ real student records
- Search and filter functionality
- Teacher-only editing permissions

### 🎨 **Modern UI/UX**
- Professional gradient designs
- Smooth animations and transitions
- Responsive layout (mobile-friendly)
- Consistent color palette
- Accessible design

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.9+
- **Git**

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/DS_Exam_Proctaring.git
cd DS_Exam_Proctaring/Exam-System
```

#### 2. Setup Backend (Python)
```bash
cd python_server
pip install -r requirements.txt
python start_server.py
```
Backend runs on: `http://localhost:8001`

#### 3. Setup Frontend (React)
```bash
cd client_frontend
npm install
npm run dev
```
Frontend runs on: `http://localhost:5173`

---

## 🔑 Login Credentials

### Students
- **Roll Number**: Any from database (e.g., `23102A0058`, `23102A0059`)
- **Name**: Auto-filled from database

### Teacher
- **ID**: `T001`
- **Name**: Any name

### Processor
- **ID**: `P001`
- **Name**: Any name

---

## 📖 Usage Guide

### Student Workflow
1. Login with your roll number
2. Click "Start Exam"
3. Answer 5 questions within 30 minutes
4. Submit exam
5. Wait for teacher to release marks
6. View your results

### Teacher Workflow
1. Login with ID `T001`
2. Go to "All Submissions" to see all students
3. Click "Release" to release marks for a student
4. Click "Reset" to allow a student to retake
5. Edit database records as needed

### Processor Workflow
1. Login with ID `P001`
2. Start auto-processing or process manually
3. View processing logs and statistics

---

## 🏗️ Project Structure

```
Exam-System/
├── client_frontend/          # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # UI Components
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Student/
│   │   │   ├── Teacher/
│   │   │   ├── Processor/
│   │   │   ├── Submissions/
│   │   │   └── Database/
│   │   ├── contexts/         # React Context (UserContext)
│   │   ├── services/         # API Services
│   │   ├── types/            # TypeScript Types
│   │   └── index.css         # Global Styles
│   ├── package.json
│   └── vite.config.mjs
│
├── python_server/            # FastAPI Backend
│   ├── unified_exam_server.py
│   ├── start_server.py
│   └── requirements.txt
│
└── README.md
```

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP Client
- **React Router** - Navigation

### Backend
- **FastAPI** - Python Web Framework
- **Uvicorn** - ASGI Server
- **Pydantic** - Data Validation
- **CORS Middleware** - Cross-Origin Support

---

## 📊 Features Breakdown

### Authentication & Authorization
- ✅ Role-based access control (RBAC)
- ✅ Persistent login (localStorage)
- ✅ Database validation for students
- ✅ Protected routes

### Exam System
- ✅ Timed exams (30 minutes)
- ✅ Auto-submit on timeout
- ✅ Progress tracking
- ✅ Percentage-based scoring
- ✅ Results with progress bars

### Database
- ✅ 30+ student records
- ✅ Teacher-only editing
- ✅ Search and filter
- ✅ 2PC protocol support

### UI/UX
- ✅ Gradient headers
- ✅ Animated components
- ✅ Responsive design
- ✅ Professional color palette
- ✅ Smooth transitions

---

## 🔧 Configuration

### Backend Port
Default: `8001`  
Change in: `python_server/start_server.py`

### Frontend Proxy
Configure in: `client_frontend/vite.config.mjs`
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
  }
}
```

---

## 🧪 Testing

### Manual Testing
1. Test student exam flow
2. Test teacher mark release
3. Test processor evaluation
4. Test exam reset functionality
5. Test database editing

### API Endpoints
- `GET /api/v1/exam/questions` - Get exam questions
- `POST /api/v1/exam/submit` - Submit exam
- `POST /api/v1/exam/release-marks/{student_id}` - Release marks
- `POST /api/v1/exam/reset/{student_id}` - Reset exam
- `GET /api/v1/database/records` - Get all records

---

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Your Name** - Initial work

---

## 🙏 Acknowledgments

- React Team for the amazing framework
- FastAPI for the excellent Python framework
- Tailwind CSS for the utility-first CSS framework
- Lucide for the beautiful icons

---

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.

---

## 🎯 Future Enhancements

- [ ] Add video proctoring
- [ ] Implement face recognition
- [ ] Add more question types (essay, true/false)
- [ ] Export results to PDF
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] Multi-language support

---

**⭐ If you find this project useful, please give it a star!**

---

Made with ❤️ for education
