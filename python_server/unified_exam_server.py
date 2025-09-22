#!/usr/bin/env python3
"""
Unified Exam Proctoring System Server
Combines all 8 tasks into a single FastAPI server with REST API endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import threading
import time
import random
import heapq
import json
import logging
from datetime import datetime
from collections import deque, defaultdict
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import socket
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified Exam Proctoring System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class ViolationReport(BaseModel):
    roll: int
    name: str
    warning: str
    question_no: int
    violation_no: int

class ClockSyncRequest(BaseModel):
    role: str  # "teacher" or "student"
    time: str  # "HH:MM:SS"

class MutualExclusionRequest(BaseModel):
    student_id: str
    timestamp: int

class ExamSubmission(BaseModel):
    student_id: str
    answers: List[str]

class LoadBalanceSubmission(BaseModel):
    student_id: str
    payload: Dict[str, Any]

class DatabaseUpdate(BaseModel):
    roll_number: str
    mse: int
    ese: int

class DatabaseRead(BaseModel):
    roll_number: str

# ==================== GLOBAL STATE ====================

# Task 1-3: Exam Proctoring System
students_names = {
    58: "Hussain", 59: "Saish", 65: "Khushal", 75: "Hasnain", 68: "Amritesh"
}
violations = {}
terminated_students = set()
marksheet = dict.fromkeys(students_names, 100)
violation_counters = dict.fromkeys(students_names, 0)

# Task 4: Berkeley Clock Synchronization
system_times = {}
clock_sync_participants = set()

# Task 5: Mutual Exclusion
request_queue = []
current_holder = "Teacher"
mutex_lock = threading.Lock()

# Task 6: Exam Processing
exam_questions = [
    {"q": "Which feature is NOT typically associated with distributed systems?",
     "options": ["A) Transparency", "B) Scalability", "C) Centralized control", "D) Fault tolerance"], "ans": "C"},
    {"q": "In which model do processors form a common pool assigned to tasks as needed?",
     "options": ["A) Workstation model", "B) Minicomputer model", "C) Processor pool model", "D) Hybrid model"], "ans": "C"},
    {"q": "Middleware mainly provides which functionality in distributed systems?",
     "options": ["A) Communication and coordination", "B) File system management", "C) Operating system scheduling", "D) Hardware virtualization"], "ans": "A"},
    {"q": "Which of these is an API style often used in middleware systems?",
     "options": ["A) REST", "B) SMTP", "C) POP3", "D) Telnet"], "ans": "A"},
    {"q": "Which technology is widely used for Remote Procedure Calls (RPCs)?",
     "options": ["A) HTTP", "B) gRPC", "C) FTP", "D) SMTP"], "ans": "B"},
]

exam_status = {}  # student_id -> status
exam_submissions = {}  # student_id -> {"answers": [], "marks": int, "released": bool}

# Task 7: Load Balancing
local_queue = queue.Queue(maxsize=10)
local_inflight = 0
backup_queue = queue.Queue()
total_students = 15
received_count = 0
migrate_threshold = 8

# Task 8: Distributed Database
STUDENTS = [
    ("23102A0055", "SHRAVANI CHAVAN"),
    ("23102A0056", "SOHAN KUMAR"),
    ("23102A0057", "NIKHIL PATIL"),
    ("23102A0058", "HUSSAIN ANAJWALA"),
    ("23102A0059", "SAISH MORE"),
    ("23102A0060", "KETKI GAIKWAD"),
    ("23102A0061", "SAHIL GHOGARE"),
    ("23102A0062", "KHUSHBOO YADAV"),
    ("23102A0063", "VAISHNAVI SAWANT"),
    ("23102A0064", "SOHAM KHOLAPURE"),
    ("23102A0065", "KHUSHAL SOLANKI"),
    ("23102A0068", "DIKSHA PARULEKAR"),
    ("23102A0069", "DEVANSHI MAHAJAN"),
    ("23102A0070", "BHUMI NAIK"),
    ("23102A0071", "YASHRAJ PATIL"),
    ("23102A0072", "SHRUTI TAMBAD E"),
    ("23102A0073", "MOHAMMAD EQUAAN KACCHI"),
    ("23102A0074", "VAISHNAVI KHOPKAR"),
    ("23102A0075", "HASNAIN KHAN"),
    ("23102A0076", "PRASANA SHANGLOO"),
    ("24102A2001", "SIDDHI GAWADE"),
    ("24102A2002", "SANDEEP MAJUMDAR"),
    ("24102A2003", "CHIRAG CHAUDHARI"),
    ("24102A2004", "ANUSHKA UNDE"),
    ("24102A2005", "SAJIYA SHAIKH"),
    ("24102A2006", "TAMANNA SHAIKH"),
    ("24102A2007", "TANISHQ KULKARNI"),
    ("24102A2008", "ARAV MAHIND"),
]

# Generate initial database
database = {}
for rn, name in STUDENTS:
    database[rn] = {
        "rn": rn,
        "name": name,
        "isa": random.randint(0, 15),
        "mse": random.randint(0, 20),
        "ese": random.randint(0, 40),
        "total": 0
    }
    database[rn]["total"] = database[rn]["isa"] + database[rn]["mse"] + database[rn]["ese"]

# ==================== TASK 1-3: EXAM PROCTORING ====================

@app.post("/api/v1/violation/report")
async def report_violation(violation: ViolationReport):
    """Report a violation for a student (Task 1-3)"""
    roll = violation.roll
    if roll not in students_names:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if roll in terminated_students:
        return {"status": "ignored", "message": "Student already terminated"}
    
    violations[roll] = violations.get(roll, 0) + 1
    violation_counters[roll] += 1
    count = violations[roll]
    
    if count == 1:
        marksheet[roll] = 50
        status = "warning"
        message = f"First violation for {students_names[roll]} - marks reduced to 50%"
    elif count == 2:
        marksheet[roll] = 0
        terminated_students.add(roll)
        status = "terminated"
        message = f"Second violation for {students_names[roll]} - EXAM TERMINATED, marks = 0%"
    else:
        status = "ignored"
        message = f"Student {students_names[roll]} already terminated"
    
    logger.info(f"Violation {count} for {students_names[roll]} (Roll {roll}) on Q{violation.question_no}")
    
    return {
        "status": status,
        "message": message,
        "violation_count": count,
        "current_marks": marksheet[roll],
        "student_name": students_names[roll]
    }

@app.get("/api/v1/violation/status/{roll}")
async def get_violation_status(roll: int):
    """Get violation status for a student"""
    if roll not in students_names:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "roll": roll,
        "name": students_names[roll],
        "violation_count": violations.get(roll, 0),
        "current_marks": marksheet[roll],
        "terminated": roll in terminated_students
    }

@app.get("/api/v1/violation/marksheet")
async def get_marksheet():
    """Get final marksheet"""
    return {
        "marksheet": marksheet,
        "violations": violations,
        "terminated_students": list(terminated_students)
    }

# ==================== TASK 4: BERKELEY CLOCK SYNCHRONIZATION ====================

@app.post("/api/v1/clock/register")
async def register_clock_participant(clock_req: ClockSyncRequest):
    """Register a participant for clock synchronization"""
    clock_sync_participants.add(clock_req.role)
    system_times[clock_req.role] = clock_req.time
    return {"status": "registered", "participants": list(clock_sync_participants)}

@app.post("/api/v1/clock/sync")
async def start_clock_synchronization():
    """Start Berkeley clock synchronization"""
    if len(clock_sync_participants) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 participants")
    
    # Calculate average time
    times_in_seconds = []
    for role, time_str in system_times.items():
        h, m, s = map(int, time_str.split(":"))
        times_in_seconds.append(h * 3600 + m * 60 + s)
    
    avg_time = sum(times_in_seconds) // len(times_in_seconds)
    
    # Calculate adjustments
    adjustments = {}
    for role, time_str in system_times.items():
        h, m, s = map(int, time_str.split(":"))
        current_seconds = h * 3600 + m * 60 + s
        offset = avg_time - current_seconds
        adjustments[role] = offset
    
    # Update system times
    for role, offset in adjustments.items():
        h, m, s = map(int, system_times[role].split(":"))
        new_seconds = h * 3600 + m * 60 + s + offset
        new_h = new_seconds // 3600
        new_m = (new_seconds % 3600) // 60
        new_s = new_seconds % 60
        system_times[role] = f"{new_h:02d}:{new_m:02d}:{new_s:02d}"
    
    return {
        "status": "synchronized",
        "average_time": f"{avg_time // 3600:02d}:{(avg_time % 3600) // 60:02d}:{avg_time % 60:02d}",
        "adjustments": adjustments,
        "updated_times": system_times
    }

@app.get("/api/v1/clock/status")
async def get_clock_status():
    """Get current clock synchronization status"""
    return {
        "participants": list(clock_sync_participants),
        "system_times": system_times
    }

# ==================== TASK 5: MUTUAL EXCLUSION ====================

@app.post("/api/v1/mutex/request")
async def request_critical_section(mutex_req: MutualExclusionRequest):
    """Request access to critical section"""
    global current_holder
    with mutex_lock:
        heapq.heappush(request_queue, (mutex_req.timestamp, mutex_req.student_id))
        
        if current_holder == "Teacher":
            # Grant immediately if teacher is current holder
            ts, student = heapq.heappop(request_queue)
            current_holder = student
            return {
                "status": "granted",
                "holder": student,
                "timestamp": ts,
                "message": f"Critical section granted to {student}"
            }
        else:
            return {
                "status": "queued",
                "current_holder": current_holder,
                "queue_position": len(request_queue),
                "message": f"Request queued for {mutex_req.student_id}"
            }

@app.post("/api/v1/mutex/release")
async def release_critical_section(student_id: str):
    """Release critical section"""
    global current_holder
    with mutex_lock:
        if current_holder != student_id:
            raise HTTPException(status_code=400, detail="Only current holder can release")
        
        if request_queue:
            ts, next_student = heapq.heappop(request_queue)
            current_holder = next_student
            return {
                "status": "transferred",
                "new_holder": next_student,
                "timestamp": ts,
                "message": f"Critical section transferred to {next_student}"
            }
        else:
            current_holder = "Teacher"
            return {
                "status": "returned",
                "holder": "Teacher",
                "message": "Critical section returned to Teacher"
            }

@app.get("/api/v1/mutex/status")
async def get_mutex_status():
    """Get mutual exclusion status"""
    with mutex_lock:
        return {
            "current_holder": current_holder,
            "queue": [{"student": student, "timestamp": ts} for ts, student in request_queue],
            "queue_length": len(request_queue)
        }

# ==================== TASK 6: EXAM PROCESSING ====================

@app.get("/api/v1/exam/questions")
async def get_exam_questions():
    """Get exam questions"""
    return {"questions": exam_questions}

@app.post("/api/v1/exam/start/{student_id}")
async def start_exam(student_id: str):
    """Start exam for a student"""
    exam_status[student_id] = "Exam started"
    return {
        "status": "started",
        "student_id": student_id,
        "questions": exam_questions,
        "message": "Exam started successfully"
    }

@app.post("/api/v1/exam/submit")
async def submit_exam(submission: ExamSubmission):
    """Submit exam answers"""
    student_id = submission.student_id
    
    if student_id in exam_submissions:
        return {
            "status": "already_submitted",
            "message": "Exam already submitted"
        }
    
    # Calculate marks
    marks = sum(1 for i, q in enumerate(exam_questions)
                if i < len(submission.answers) and submission.answers[i].upper() == q["ans"])
    
    exam_submissions[student_id] = {
        "answers": submission.answers,
        "marks": marks,
        "released": False
    }
    exam_status[student_id] = "Exam submitted"
    
    return {
        "status": "submitted",
        "student_id": student_id,
        "marks": marks,
        "message": "Exam submitted successfully"
    }

@app.post("/api/v1/exam/release-marks/{student_id}")
async def release_marks(student_id: str):
    """Release marks for a student"""
    if student_id not in exam_submissions:
        raise HTTPException(status_code=404, detail="Student not found or exam not submitted")
    
    exam_submissions[student_id]["released"] = True
    exam_status[student_id] = "Marks released"
    
    return {
        "status": "released",
        "student_id": student_id,
        "marks": exam_submissions[student_id]["marks"],
        "message": "Marks released successfully"
    }

@app.get("/api/v1/exam/status/{student_id}")
async def get_exam_status(student_id: str):
    """Get exam status for a student"""
    status = exam_status.get(student_id, "No status")
    submission = exam_submissions.get(student_id)
    
    result = {"student_id": student_id, "status": status}
    if submission and submission["released"]:
        result["marks"] = submission["marks"]
    
    return result

# ==================== TASK 7: LOAD BALANCING ====================

async def process_submission_local(student_id: str, payload: Dict[str, Any]):
    """Process submission locally"""
    await asyncio.sleep(2)  # Simulate processing time
    logger.info(f"Local processing completed for {student_id}")

async def process_submission_backup(student_id: str, payload: Dict[str, Any]):
    """Process submission on backup server"""
    await asyncio.sleep(2)  # Simulate processing time
    logger.info(f"Backup processing completed for {student_id}")

@app.post("/api/v1/load-balance/submit")
async def submit_for_load_balancing(submission: LoadBalanceSubmission, background_tasks: BackgroundTasks):
    """Submit for load balancing processing"""
    global local_inflight, received_count
    
    student_id = submission.student_id
    payload = submission.payload
    
    received_count += 1
    
    if local_inflight >= migrate_threshold:
        # Migrate to backup
        background_tasks.add_task(process_submission_backup, student_id, payload)
        return {
            "status": "migrated",
            "student_id": student_id,
            "via": "backup",
            "message": "Submission migrated to backup server"
        }
    else:
        # Process locally
        local_inflight += 1
        background_tasks.add_task(process_submission_local, student_id, payload)
        return {
            "status": "accepted",
            "student_id": student_id,
            "via": "main",
            "message": "Submission accepted for local processing"
        }

@app.get("/api/v1/load-balance/status")
async def get_load_balance_status():
    """Get load balancing status"""
    return {
        "local_inflight": local_inflight,
        "received_count": received_count,
        "migrate_threshold": migrate_threshold,
        "local_queue_size": local_queue.qsize(),
        "backup_queue_size": backup_queue.qsize()
    }

# ==================== TASK 8: DISTRIBUTED DATABASE ====================

@app.get("/api/v1/database/read/{roll_number}")
async def read_student_record(roll_number: str):
    """Read student record from database"""
    if roll_number not in database:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    return {
        "status": "success",
        "record": database[roll_number]
    }

@app.post("/api/v1/database/update")
async def update_student_record(update: DatabaseUpdate):
    """Update student record using 2PC protocol"""
    roll_number = update.roll_number
    
    if roll_number not in database:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Simulate 2PC protocol
    # Phase 1: Prepare
    logger.info(f"Phase 1: Preparing update for {roll_number}")
    await asyncio.sleep(0.1)  # Simulate network delay
    
    # Phase 2: Commit
    logger.info(f"Phase 2: Committing update for {roll_number}")
    database[roll_number]["mse"] = update.mse
    database[roll_number]["ese"] = update.ese
    database[roll_number]["total"] = database[roll_number]["isa"] + update.mse + update.ese
    
    return {
        "status": "success",
        "message": f"Record updated for {roll_number}",
        "updated_record": database[roll_number]
    }

@app.get("/api/v1/database/all")
async def get_all_records():
    """Get all student records"""
    return {
        "status": "success",
        "records": list(database.values()),
        "total_records": len(database)
    }

@app.get("/api/v1/database/search")
async def search_records(name: Optional[str] = None, min_total: Optional[int] = None):
    """Search student records"""
    results = []
    
    for record in database.values():
        if name and name.lower() not in record["name"].lower():
            continue
        if min_total and record["total"] < min_total:
            continue
        results.append(record)
    
    return {
        "status": "success",
        "results": results,
        "count": len(results)
    }

# ==================== GENERAL ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified Exam Proctoring System API",
        "version": "1.0.0",
        "endpoints": {
            "violation": "/api/v1/violation/*",
            "clock": "/api/v1/clock/*",
            "mutex": "/api/v1/mutex/*",
            "exam": "/api/v1/exam/*",
            "load_balance": "/api/v1/load-balance/*",
            "database": "/api/v1/database/*"
        }
    }

@app.get("/api/v1/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "system_status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "exam_proctoring": "active",
            "clock_sync": "active",
            "mutual_exclusion": "active",
            "exam_processing": "active",
            "load_balancing": "active",
            "distributed_database": "active"
        },
        "statistics": {
            "total_students": len(students_names),
            "violations_reported": sum(violations.values()),
            "terminated_students": len(terminated_students),
            "exam_submissions": len(exam_submissions),
            "database_records": len(database)
        }
    }

@app.get("/api/v1/docs")
async def get_api_documentation():
    """Get API documentation"""
    return {
        "title": "Unified Exam Proctoring System API",
        "description": "Combined API for all 8 exam system tasks",
        "tasks": {
            "task_1_3": "Exam Proctoring with Violation Detection",
            "task_4": "Berkeley Clock Synchronization",
            "task_5": "Distributed Mutual Exclusion",
            "task_6": "Exam Processing with Auto Mark Release",
            "task_7": "Load Balancing with Backup Migration",
            "task_8": "Distributed Database with 2PC Protocol"
        },
        "usage": {
            "violation_detection": "POST /api/v1/violation/report",
            "clock_sync": "POST /api/v1/clock/sync",
            "mutual_exclusion": "POST /api/v1/mutex/request",
            "exam_processing": "POST /api/v1/exam/submit",
            "load_balancing": "POST /api/v1/load-balance/submit",
            "database_operations": "GET/POST /api/v1/database/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
