#!/usr/bin/env python3
"""
Unified Exam Proctoring System Server
Combines all 8 tasks into a single FastAPI server with REST API endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi import WebSocket, WebSocketDisconnect
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

# Real-time session (WS) state
session_active = False
session_duration_seconds = 0
session_end_epoch = 0
session_task = None
connected_clients = set()  # set[WebSocket]

# Task 4: Berkeley Clock Synchronization
system_times = {}
clock_sync_participants = set()

# Task 5: Mutual Exclusion
request_queue = []
current_holder = "Teacher"
mutex_lock = threading.Lock()
granted_students = set()  # Track which students have been granted CS

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
local_workers = 8
batch_processing = False
batch_id = 0
local_done = set()
backup_done = set()
batch_end_sent = False
worker_status = {f"worker_{i}": "idle" for i in range(local_workers)}

# Task 8: Distributed Database with Multi-Replica System
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

# Multi-replica system configuration
REPLICA_NAMES = ["R1", "R2", "R3"]
CHUNK_SIZE = 7
REPLICATION_FACTOR = 2

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

# Chunk-based distribution
def create_chunks(data, chunk_size):
    """Split data into chunks for distribution"""
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Create chunks from student records
student_records = list(database.values())
chunks = create_chunks(student_records, CHUNK_SIZE)

# Chunk-to-replica mapping with replication
chunk_map = {}
replica_data = {replica: {} for replica in REPLICA_NAMES}

# Distribute chunks across replicas with replication
for chunk_id, chunk in enumerate(chunks):
    # Round-robin assignment with replication
    primary_replica = REPLICA_NAMES[chunk_id % len(REPLICA_NAMES)]
    secondary_replica = REPLICA_NAMES[(chunk_id + 1) % len(REPLICA_NAMES)]
    
    chunk_map[chunk_id] = [primary_replica, secondary_replica]
    
    # Store data in both replicas
    for record in chunk:
        replica_data[primary_replica][record["rn"]] = record.copy()
        replica_data[secondary_replica][record["rn"]] = record.copy()

# Replica status tracking
replica_status = {replica: "online" for replica in REPLICA_NAMES}
replica_locks = {replica: threading.Lock() for replica in REPLICA_NAMES}
replica_queues = {replica: {"read": [], "write": []} for replica in REPLICA_NAMES}

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

    # Broadcast flag event to WS clients
    await broadcast_ws_event({
        "type": "violation",
        "roll": roll,
        "name": students_names[roll],
        "question_no": violation.question_no,
        "violation_count": count,
        "current_marks": marksheet[roll]
    })
    
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
    global current_holder, granted_students
    with mutex_lock:
        # Check if student is already in queue
        student_in_queue = any(student == mutex_req.student_id for _, student in request_queue)
        
        if not student_in_queue:
            heapq.heappush(request_queue, (mutex_req.timestamp, mutex_req.student_id))
        
        if current_holder == "Teacher" and request_queue:
            # Grant immediately if teacher is current holder and queue has requests
            ts, student = heapq.heappop(request_queue)
            current_holder = student
            granted_students.add(student)
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

class MutexReleaseRequest(BaseModel):
    student_id: str

@app.post("/api/v1/mutex/release")
async def release_critical_section(request: MutexReleaseRequest):
    """Release critical section"""
    global current_holder, granted_students
    student_id = request.student_id
    with mutex_lock:
        if current_holder != student_id:
            raise HTTPException(status_code=400, detail="Only current holder can release")
        
        # Remove from granted students
        granted_students.discard(student_id)
        
        if request_queue:
            ts, next_student = heapq.heappop(request_queue)
            current_holder = next_student
            granted_students.add(next_student)
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

@app.get("/api/v1/mutex/check/{student_id}")
async def check_grant_status(student_id: str):
    """Check if student has been granted critical section access"""
    with mutex_lock:
        if student_id in granted_students and current_holder == student_id:
            return {
                "status": "granted",
                "holder": student_id,
                "message": f"Critical section access granted to {student_id}"
            }
        else:
            return {
                "status": "not_granted",
                "current_holder": current_holder,
                "message": f"Critical section not granted to {student_id}"
            }

@app.get("/api/v1/mutex/status")
async def get_mutex_status():
    """Get mutual exclusion status"""
    with mutex_lock:
        return {
            "current_holder": current_holder,
            "queue": [{"student": student, "timestamp": ts} for ts, student in request_queue],
            "queue_length": len(request_queue),
            "granted_students": list(granted_students)
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
    correct_answers = sum(1 for i, q in enumerate(exam_questions)
                if i < len(submission.answers) and submission.answers[i].upper() == q["ans"])
    
    # Calculate percentage
    total_questions = len(exam_questions)
    marks_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    exam_submissions[student_id] = {
        "answers": submission.answers,
        "marks": marks_percentage,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "released": False
    }
    exam_status[student_id] = "Exam submitted"
    
    return {
        "status": "submitted",
        "student_id": student_id,
        "marks": marks_percentage,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
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
    submission = exam_submissions.get(student_id)
    
    # Determine status based on submission state
    if submission:
        if submission["released"]:
            status = "released"
            result = {
                "student_id": student_id,
                "status": status,
                "marks": submission["marks"]
            }
        else:
            status = "submitted"
            result = {
                "student_id": student_id,
                "status": status
            }
    else:
        # No submission found - check if exam was started
        status = exam_status.get(student_id, "not_started")
        result = {
            "student_id": student_id,
            "status": status
        }
    
    return result

@app.post("/api/v1/exam/reset/{student_id}")
async def reset_exam(student_id: str):
    """Reset exam for a student - clears submission and marks"""
    # Remove from exam submissions
    if student_id in exam_submissions:
        del exam_submissions[student_id]
    
    # Reset exam status
    if student_id in exam_status:
        del exam_status[student_id]
    
    logger.info(f"Exam reset for student: {student_id}")
    
    return {
        "status": "reset",
        "student_id": student_id,
        "message": f"Exam reset successfully for {student_id}. Student can now retake the exam."
    }

# ==================== TASK 7: LOAD BALANCING ====================

async def process_submission_local(student_id: str, payload: Dict[str, Any], worker_id: str = None):
    """Process submission locally with worker tracking"""
    global local_inflight, local_done, batch_processing
    if worker_id:
        worker_status[worker_id] = "processing"
    
    await asyncio.sleep(2)  # Simulate processing time
    logger.info(f"Local processing completed for {student_id}")
    
    # Update worker status and counters
    if worker_id:
        worker_status[worker_id] = "idle"
    local_inflight = max(0, local_inflight - 1)
    local_done.add(student_id)
    
    # Check if batch is complete
    if len(local_done) + len(backup_done) >= total_students:
        batch_processing = False
        logger.info("Batch processing completed")

async def process_submission_backup(student_id: str, payload: Dict[str, Any]):
    """Process submission on backup server"""
    global backup_done, batch_processing, batch_end_sent
    await asyncio.sleep(2)  # Simulate processing time
    logger.info(f"Backup processing completed for {student_id}")
    backup_done.add(student_id)
    
    # Check if batch is complete
    if len(local_done) + len(backup_done) >= total_students:
        batch_processing = False
        # Send batch OK response from backup to main server
        logger.info(f"✓ BACKUP SERVER → MAIN SERVER: Batch {batch_id} processed OK")
        logger.info(f"✓ MAIN SERVER: All submissions completed - Batch {batch_id} SUBMITTED")
        logger.info("Batch processing completed")

@app.post("/api/v1/load-balance/submit")
async def submit_for_load_balancing(submission: LoadBalanceSubmission, background_tasks: BackgroundTasks):
    """Submit for load balancing processing with batch management"""
    global local_inflight, received_count, batch_processing, batch_id, batch_end_sent
    
    student_id = submission.student_id
    payload = submission.payload
    
    received_count += 1
    
    # Start batch processing if this is the first submission
    if not batch_processing:
        batch_processing = True
        batch_id += 1
        batch_end_sent = False
        local_done.clear()
        backup_done.clear()
        logger.info(f"Starting batch {batch_id} processing")
    
    # Send BATCH_END notification when all students have submitted
    if received_count >= total_students and not batch_end_sent:
        batch_end_sent = True
        logger.info(f"BATCH_END sent for batch {batch_id}")
    
    # Find available worker
    available_worker = None
    for worker_id, status in worker_status.items():
        if status == "idle":
            available_worker = worker_id
            break
    
    if local_inflight >= migrate_threshold or not available_worker:
        # Migrate to backup
        background_tasks.add_task(process_submission_backup, student_id, payload)
        return {
            "status": "migrated",
            "student_id": student_id,
            "via": "backup",
            "batch_id": batch_id,
            "message": "Submission migrated to backup server"
        }
    else:
        # Process locally with assigned worker
        local_inflight += 1
        background_tasks.add_task(process_submission_local, student_id, payload, available_worker)
        return {
            "status": "accepted",
            "student_id": student_id,
            "via": "main",
            "worker_id": available_worker,
            "batch_id": batch_id,
            "message": "Submission accepted for local processing"
        }

@app.get("/api/v1/load-balance/status")
async def get_load_balance_status():
    """Get enhanced load balancing status with batch processing"""
    batch_complete = len(local_done) + len(backup_done) >= total_students and batch_processing == False
    backup_response_sent = batch_complete and len(backup_done) > 0
    
    return {
        "local_inflight": local_inflight,
        "received_count": received_count,
        "migrate_threshold": migrate_threshold,
        "local_queue_size": local_queue.qsize(),
        "backup_queue_size": backup_queue.qsize(),
        "batch_processing": batch_processing,
        "current_batch_id": batch_id,
        "local_done_count": len(local_done),
        "backup_done_count": len(backup_done),
        "total_processed": len(local_done) + len(backup_done),
        "worker_status": worker_status,
        "batch_end_sent": batch_end_sent,
        "batch_complete": batch_complete,
        "backup_response_sent": backup_response_sent,
        "message": "Batch SUBMITTED - All processed" if batch_complete else "Processing..."
    }

# ==================== TASK 8: DISTRIBUTED DATABASE ====================

def find_chunk_for_record(roll_number: str):
    """Find which chunk contains the record"""
    for chunk_id, chunk in enumerate(chunks):
        for record in chunk:
            if record["rn"] == roll_number:
                return chunk_id
    return None

def get_available_replicas(chunk_id: int):
    """Get available replicas for a chunk"""
    if chunk_id not in chunk_map:
        return []
    
    available_replicas = []
    for replica in chunk_map[chunk_id]:
        if replica_status[replica] == "online":
            available_replicas.append(replica)
    return available_replicas

@app.get("/api/v1/database/read/{roll_number}")
async def read_student_record(roll_number: str):
    """Read student record from database with replica coordination"""
    chunk_id = find_chunk_for_record(roll_number)
    if chunk_id is None:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    available_replicas = get_available_replicas(chunk_id)
    if not available_replicas:
        raise HTTPException(status_code=503, detail="No replicas available")
    
    # Try to read from first available replica
    for replica in available_replicas:
        with replica_locks[replica]:
            if roll_number in replica_data[replica]:
                record = replica_data[replica][roll_number].copy()
                return {
                    "status": "success",
                    "record": record,
                    "replica": replica,
                    "chunk_id": chunk_id
                }
    
    raise HTTPException(status_code=404, detail="Record not found on any replica")

@app.post("/api/v1/database/update")
async def update_student_record(update: DatabaseUpdate):
    """Update student record using 2PC protocol with multi-replica coordination"""
    roll_number = update.roll_number
    chunk_id = find_chunk_for_record(roll_number)
    
    if chunk_id is None:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    available_replicas = get_available_replicas(chunk_id)
    if not available_replicas:
        raise HTTPException(status_code=503, detail="No replicas available")
    
    # 2PC Protocol Implementation
    logger.info(f"Starting 2PC for {roll_number} on chunk {chunk_id}")
    
    # Phase 1: Prepare
    logger.info(f"Phase 1: Preparing update for {roll_number}")
    prepared_replicas = []
    
    for replica in available_replicas:
        with replica_locks[replica]:
            if roll_number in replica_data[replica]:
                # Simulate prepare phase
                await asyncio.sleep(0.1)  # Simulate network delay
                prepared_replicas.append(replica)
                logger.info(f"Replica {replica} prepared for {roll_number}")
            else:
                logger.warning(f"Record {roll_number} not found on replica {replica}")
    
    if not prepared_replicas:
        return {
            "status": "error",
            "message": "No replicas could prepare the update"
        }
    
    # Phase 2: Commit
    logger.info(f"Phase 2: Committing update for {roll_number}")
    updated_record = None
    
    for replica in prepared_replicas:
        with replica_locks[replica]:
            if roll_number in replica_data[replica]:
                # Update the record
                replica_data[replica][roll_number]["mse"] = update.mse
                replica_data[replica][roll_number]["ese"] = update.ese
                replica_data[replica][roll_number]["total"] = (
                    replica_data[replica][roll_number]["isa"] + update.mse + update.ese
                )
                updated_record = replica_data[replica][roll_number].copy()
                logger.info(f"Replica {replica} committed update for {roll_number}")
    
    # Update main database for consistency
    if roll_number in database:
        database[roll_number]["mse"] = update.mse
        database[roll_number]["ese"] = update.ese
        database[roll_number]["total"] = database[roll_number]["isa"] + update.mse + update.ese
    
    return {
        "status": "success",
        "message": f"Record updated for {roll_number} on {len(prepared_replicas)} replicas",
        "updated_record": updated_record,
        "replicas": prepared_replicas,
        "chunk_id": chunk_id
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
    """Search student records across all replicas"""
    results = []
    
    for record in database.values():
        if name and name.lower() not in record["name"].lower():
            continue
        if min_total and record["total"] < min_total:
            continue
        results.append(record)
    
    return {
        "status": "success",
        "records": results,
        "count": len(results)
    }

@app.get("/api/v1/database/replicas")
async def get_replica_status():
    """Get replica status and chunk distribution"""
    return {
        "status": "success",
        "replicas": {
            name: {
                "status": replica_status[name],
                "record_count": len(replica_data[name]),
                "chunks": [chunk_id for chunk_id, replicas in chunk_map.items() if name in replicas]
            }
            for name in REPLICA_NAMES
        },
        "chunk_map": chunk_map,
        "total_chunks": len(chunks),
        "chunk_size": CHUNK_SIZE
    }

@app.post("/api/v1/database/replica/{replica_name}/fail")
async def simulate_replica_failure(replica_name: str):
    """Simulate replica failure for testing"""
    if replica_name not in REPLICA_NAMES:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    replica_status[replica_name] = "offline"
    logger.info(f"Replica {replica_name} marked as offline")
    
    return {
        "status": "success",
        "message": f"Replica {replica_name} marked as offline",
        "replica_status": replica_status
    }

@app.post("/api/v1/database/replica/{replica_name}/recover")
async def simulate_replica_recovery(replica_name: str):
    """Simulate replica recovery for testing"""
    if replica_name not in REPLICA_NAMES:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    replica_status[replica_name] = "online"
    logger.info(f"Replica {replica_name} marked as online")
    
    return {
        "status": "success",
        "message": f"Replica {replica_name} marked as online",
        "replica_status": replica_status
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

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

# ==================== REAL-TIME SESSION (WEBSOCKET) ====================

async def broadcast_ws_event(payload: Dict[str, Any]):
    """Send an event to all connected WS clients"""
    if not connected_clients:
        return
    dead = []
    for ws in list(connected_clients):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        try:
            connected_clients.discard(ws)
            await ws.close()
        except Exception:
            pass

async def session_tick_loop():
    """Background ticker broadcasting remaining time once per second"""
    global session_task, session_active
    while session_active:
        remaining = max(0, session_end_epoch - int(time.time()))
        await broadcast_ws_event({
            "type": "timer",
            "active": session_active,
            "remaining_seconds": remaining
        })
        if remaining <= 0:
            session_active = False
            await broadcast_ws_event({"type": "session_end"})
            break
        await asyncio.sleep(1)
    session_task = None

@app.post("/api/v1/session/start")
async def start_session(duration_minutes: int = 60):
    """Start an exam session and broadcast timer via WS"""
    global session_active, session_duration_seconds, session_end_epoch, session_task
    session_duration_seconds = max(1, duration_minutes) * 60
    session_end_epoch = int(time.time()) + session_duration_seconds
    session_active = True
    if session_task is None:
        session_task = asyncio.create_task(session_tick_loop())
    await broadcast_ws_event({
        "type": "session_start",
        "duration_seconds": session_duration_seconds,
        "end_epoch": session_end_epoch
    })
    return {"status": "started", "duration_seconds": session_duration_seconds, "end_epoch": session_end_epoch}

@app.post("/api/v1/session/stop")
async def stop_session():
    """Stop an active session"""
    global session_active
    session_active = False
    await broadcast_ws_event({"type": "session_stop"})
    return {"status": "stopped"}

@app.post("/api/v1/session/reset")
async def reset_session_state():
    """Reset counters/state relevant for a fresh run (non-destructive demo reset)"""
    global violations, terminated_students, marksheet, violation_counters
    violations = {}
    terminated_students = set()
    marksheet = dict.fromkeys(students_names, 100)
    violation_counters = dict.fromkeys(students_names, 0)
    await broadcast_ws_event({"type": "reset"})
    return {"status": "reset"}

@app.get("/api/v1/session/status")
async def get_session_status():
    remaining = max(0, session_end_epoch - int(time.time())) if session_active else 0
    return {
        "active": session_active,
        "remaining_seconds": remaining,
        "end_epoch": session_end_epoch,
        "connected_clients": len(connected_clients)
    }

@app.websocket("/ws/session")
async def session_ws(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "hello",
            "active": session_active,
            "remaining_seconds": max(0, session_end_epoch - int(time.time())) if session_active else 0
        })
        while True:
            # Keep the connection alive; ignore incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        try:
            connected_clients.discard(websocket)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
