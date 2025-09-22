#!/usr/bin/env python3
"""
Test client for the Unified Exam Proctoring System API
Demonstrates all 8 task functionalities
"""

import requests
import json
import time
import random
import socket
from typing import Dict, Any

def find_server_port(start_port=8000, max_attempts=10):
    """Find the port where the server is running"""
    for port in range(start_port, start_port + max_attempts):
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=2)
            if response.status_code == 200:
                return port
        except requests.exceptions.RequestException:
            continue
    return None

# Try to find the server port automatically
SERVER_PORT = find_server_port()
if SERVER_PORT is None:
    print("Warning: Could not find server automatically. Using default port 8000")
    SERVER_PORT = 8000

BASE_URL = f"http://localhost:{SERVER_PORT}"

class ExamSystemClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_violation_detection(self):
        """Test Task 1-3: Exam Proctoring with Violation Detection"""
        print("\n=== Testing Violation Detection (Task 1-3) ===")
        
        # Report first violation for student 58
        violation = {
            "roll": 58,
            "name": "Hussain",
            "warning": "Please focus, exam in progress!",
            "question_no": 15,
            "violation_no": 1
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/violation/report", json=violation)
        print(f"First violation: {response.json()}")
        
        # Report second violation for same student
        violation["violation_no"] = 2
        violation["question_no"] = 25
        response = self.session.post(f"{self.base_url}/api/v1/violation/report", json=violation)
        print(f"Second violation: {response.json()}")
        
        # Get marksheet
        response = self.session.get(f"{self.base_url}/api/v1/violation/marksheet")
        print(f"Marksheet: {response.json()}")
    
    def test_clock_synchronization(self):
        """Test Task 4: Berkeley Clock Synchronization"""
        print("\n=== Testing Clock Synchronization (Task 4) ===")
        
        # Register participants
        participants = [
            {"role": "teacher", "time": "10:30:45"},
            {"role": "student1", "time": "10:30:50"},
            {"role": "student2", "time": "10:30:40"},
            {"role": "student3", "time": "10:30:55"}
        ]
        
        for participant in participants:
            response = self.session.post(f"{self.base_url}/api/v1/clock/register", json=participant)
            print(f"Registered {participant['role']}: {response.json()}")
        
        # Start synchronization
        response = self.session.post(f"{self.base_url}/api/v1/clock/sync")
        print(f"Synchronization result: {response.json()}")
    
    def test_mutual_exclusion(self):
        """Test Task 5: Distributed Mutual Exclusion"""
        print("\n=== Testing Mutual Exclusion (Task 5) ===")
        
        # Request critical section from multiple students
        students = ["s1", "s2", "s3"]
        timestamps = [1000, 1001, 1002]
        
        for student, timestamp in zip(students, timestamps):
            request = {
                "student_id": student,
                "timestamp": timestamp
            }
            response = self.session.post(f"{self.base_url}/api/v1/mutex/request", json=request)
            print(f"Request from {student}: {response.json()}")
        
        # Check status
        response = self.session.get(f"{self.base_url}/api/v1/mutex/status")
        print(f"Mutex status: {response.json()}")
        
        # Release critical section
        response = self.session.post(f"{self.base_url}/api/v1/mutex/release", params={"student_id": "s1"})
        print(f"Release from s1: {response.json()}")
    
    def test_exam_processing(self):
        """Test Task 6: Exam Processing with Auto Mark Release"""
        print("\n=== Testing Exam Processing (Task 6) ===")
        
        student_id = "student1"
        
        # Start exam
        response = self.session.post(f"{self.base_url}/api/v1/exam/start/{student_id}")
        print(f"Start exam: {response.json()}")
        
        # Get questions
        response = self.session.get(f"{self.base_url}/api/v1/exam/questions")
        questions = response.json()["questions"]
        print(f"Got {len(questions)} questions")
        
        # Submit exam with some answers
        answers = ["C", "A", "B", "A", "B"]  # Some correct, some wrong
        submission = {
            "student_id": student_id,
            "answers": answers
        }
        response = self.session.post(f"{self.base_url}/api/v1/exam/submit", json=submission)
        print(f"Exam submission: {response.json()}")
        
        # Release marks
        response = self.session.post(f"{self.base_url}/api/v1/exam/release-marks/{student_id}")
        print(f"Release marks: {response.json()}")
        
        # Check status
        response = self.session.get(f"{self.base_url}/api/v1/exam/status/{student_id}")
        print(f"Exam status: {response.json()}")
    
    def test_load_balancing(self):
        """Test Task 7: Load Balancing with Backup Migration"""
        print("\n=== Testing Load Balancing (Task 7) ===")
        
        # Submit multiple requests to test load balancing
        for i in range(12):  # More than threshold
            submission = {
                "student_id": f"student_{i}",
                "payload": {"data": f"test_data_{i}"}
            }
            response = self.session.post(f"{self.base_url}/api/v1/load-balance/submit", json=submission)
            print(f"Submission {i}: {response.json()}")
            time.sleep(0.1)  # Small delay
        
        # Check load balance status
        response = self.session.get(f"{self.base_url}/api/v1/load-balance/status")
        print(f"Load balance status: {response.json()}")
    
    def test_distributed_database(self):
        """Test Task 8: Distributed Database with 2PC Protocol"""
        print("\n=== Testing Distributed Database (Task 8) ===")
        
        # Read a student record
        roll_number = "23102A0058"
        response = self.session.get(f"{self.base_url}/api/v1/database/read/{roll_number}")
        print(f"Read record: {response.json()}")
        
        # Update a student record
        update = {
            "roll_number": roll_number,
            "mse": 18,
            "ese": 35
        }
        response = self.session.post(f"{self.base_url}/api/v1/database/update", json=update)
        print(f"Update record: {response.json()}")
        
        # Search records
        response = self.session.get(f"{self.base_url}/api/v1/database/search", params={"min_total": 60})
        print(f"Search results (min_total=60): {len(response.json()['results'])} records")
        
        # Get all records
        response = self.session.get(f"{self.base_url}/api/v1/database/all")
        print(f"Total records: {response.json()['total_records']}")
    
    def test_system_status(self):
        """Test system status and documentation"""
        print("\n=== Testing System Status ===")
        
        # Get system status
        response = self.session.get(f"{self.base_url}/api/v1/status")
        print(f"System status: {response.json()}")
        
        # Get API documentation
        response = self.session.get(f"{self.base_url}/api/v1/docs")
        print(f"API docs: {response.json()}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting Unified Exam Proctoring System API Tests")
        print("=" * 60)
        
        try:
            self.test_violation_detection()
            self.test_clock_synchronization()
            self.test_mutual_exclusion()
            self.test_exam_processing()
            self.test_load_balancing()
            self.test_distributed_database()
            self.test_system_status()
            
            print("\n" + "=" * 60)
            print("All tests completed successfully!")
            
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to server. Make sure the server is running on http://localhost:8000")
        except Exception as e:
            print(f"Error during testing: {e}")

if __name__ == "__main__":
    client = ExamSystemClient()
    client.run_all_tests()
