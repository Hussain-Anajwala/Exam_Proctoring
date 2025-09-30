#!/usr/bin/env python3
"""
Comprehensive Testing Script for All 8 Backend Tasks
Tests each task individually to verify functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Base URL for the unified server
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_server_connection():
    """Test if the server is running"""
    print_header("Testing Server Connection")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success("Server is running!")
            print_info(f"Server URL: {BASE_URL}")
            return True
        else:
            print_error(f"Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure it's running!")
        print_info("Start server with: python python_server/start_simple.py")
        return False
    except Exception as e:
        print_error(f"Error connecting to server: {e}")
        return False

def test_task_1_3_violation_detection():
    """Test Task 1-3: Violation Detection"""
    print_header("Task 1-3: Violation Detection")
    
    try:
        # Test 1: Report first violation
        print_info("Test 1: Reporting first violation for Hussain (Roll 58)")
        violation_data = {
            "roll": 58,
            "name": "Hussain",
            "warning": "Please focus, exam in progress!",
            "question_no": 15,
            "violation_no": 1
        }
        response = requests.post(f"{API_BASE}/violation/report", json=violation_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"First violation reported: {data['message']}")
            print_info(f"Current marks: {data['current_marks']}%")
        else:
            print_error(f"Failed to report violation: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 2: Report second violation (termination)
        print_info("\nTest 2: Reporting second violation for Hussain (Roll 58)")
        violation_data["violation_no"] = 2
        violation_data["question_no"] = 25
        response = requests.post(f"{API_BASE}/violation/report", json=violation_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Second violation reported: {data['message']}")
            print_info(f"Current marks: {data['current_marks']}%")
            print_info(f"Status: {data['status']}")
        else:
            print_error(f"Failed to report violation: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 3: Get violation status
        print_info("\nTest 3: Getting violation status")
        response = requests.get(f"{API_BASE}/violation/status/58")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status retrieved for {data['name']}")
            print_info(f"Violations: {data['violation_count']}, Marks: {data['current_marks']}%, Terminated: {data['terminated']}")
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
        
        # Test 4: Get marksheet
        print_info("\nTest 4: Getting complete marksheet")
        response = requests.get(f"{API_BASE}/violation/marksheet")
        if response.status_code == 200:
            data = response.json()
            print_success("Marksheet retrieved successfully")
            print_info(f"Total students: {len(data['marksheet'])}")
            print_info(f"Terminated students: {len(data['terminated_students'])}")
        else:
            print_error(f"Failed to get marksheet: {response.status_code}")
            return False
        
        print_success("\n✓ Task 1-3: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def test_task_4_clock_sync():
    """Test Task 4: Berkeley Clock Synchronization"""
    print_header("Task 4: Berkeley Clock Synchronization")
    
    try:
        # Test 1: Register participants
        print_info("Test 1: Registering clock participants")
        participants = [
            {"role": "teacher", "time": "10:30:45"},
            {"role": "student1", "time": "10:30:50"},
            {"role": "student2", "time": "10:30:40"},
            {"role": "proctor", "time": "10:30:48"}
        ]
        
        for participant in participants:
            response = requests.post(f"{API_BASE}/clock/register", json=participant)
            if response.status_code == 200:
                print_success(f"Registered {participant['role']} with time {participant['time']}")
            else:
                print_error(f"Failed to register {participant['role']}")
                return False
        
        time.sleep(1)
        
        # Test 2: Start synchronization
        print_info("\nTest 2: Starting clock synchronization")
        response = requests.post(f"{API_BASE}/clock/sync")
        if response.status_code == 200:
            data = response.json()
            print_success("Clock synchronization completed!")
            print_info(f"Average time: {data['average_time']}")
            print_info("Adjustments:")
            for role, offset in data['adjustments'].items():
                print_info(f"  {role}: {offset:+d} seconds")
        else:
            print_error(f"Failed to synchronize: {response.status_code}")
            return False
        
        # Test 3: Get clock status
        print_info("\nTest 3: Getting clock status")
        response = requests.get(f"{API_BASE}/clock/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Clock status retrieved")
            print_info(f"Participants: {len(data['participants'])}")
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
        
        print_success("\n✓ Task 4: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def test_task_5_mutual_exclusion():
    """Test Task 5: Distributed Mutual Exclusion"""
    print_header("Task 5: Distributed Mutual Exclusion")
    
    try:
        # Test 1: Request critical section
        print_info("Test 1: Student1 requesting critical section")
        request_data = {"student_id": "Student1", "timestamp": 1000}
        response = requests.post(f"{API_BASE}/mutex/request", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request status: {data['status']}")
            print_info(f"Message: {data['message']}")
        else:
            print_error(f"Failed to request: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 2: Another student requests
        print_info("\nTest 2: Student2 requesting critical section")
        request_data = {"student_id": "Student2", "timestamp": 1001}
        response = requests.post(f"{API_BASE}/mutex/request", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request status: {data['status']}")
            print_info(f"Queue position: {data.get('queue_position', 'N/A')}")
        else:
            print_error(f"Failed to request: {response.status_code}")
            return False
        
        # Test 3: Get mutex status
        print_info("\nTest 3: Getting mutex status")
        response = requests.get(f"{API_BASE}/mutex/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Mutex status retrieved")
            print_info(f"Current holder: {data['current_holder']}")
            print_info(f"Queue length: {len(data['queue'])}")
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
        
        # Test 4: Release critical section
        print_info("\nTest 4: Student1 releasing critical section")
        release_data = {"student_id": "Student1"}
        response = requests.post(f"{API_BASE}/mutex/release", json=release_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Release status: {data['status']}")
            print_info(f"Next holder: {data.get('next_holder', 'None')}")
        else:
            print_error(f"Failed to release: {response.status_code}")
            return False
        
        print_success("\n✓ Task 5: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def test_task_6_exam_processing():
    """Test Task 6: Exam Processing with Auto Mark Release"""
    print_header("Task 6: Exam Processing")
    
    try:
        # Test 1: Get exam questions
        print_info("Test 1: Getting exam questions")
        response = requests.get(f"{API_BASE}/exam/questions")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data['questions'])} questions")
            print_info(f"Sample question: {data['questions'][0]['question'][:50]}...")
        else:
            print_error(f"Failed to get questions: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 2: Start exam
        print_info("\nTest 2: Starting exam for student1")
        response = requests.post(f"{API_BASE}/exam/start/student1")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Exam started: {data['message']}")
            print_info(f"Status: {data['status']}")
        else:
            print_error(f"Failed to start exam: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 3: Submit exam
        print_info("\nTest 3: Submitting exam answers")
        submission_data = {
            "student_id": "student1",
            "answers": ["C", "A", "B", "A", "B"]  # Sample answers
        }
        response = requests.post(f"{API_BASE}/exam/submit", json=submission_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Exam submitted: {data['message']}")
            print_info(f"Score: {data['score']}/{data['total']}")
        else:
            print_error(f"Failed to submit exam: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 4: Release marks
        print_info("\nTest 4: Releasing marks")
        response = requests.post(f"{API_BASE}/exam/release-marks/student1")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Marks released: {data['message']}")
            print_info(f"Final marks: {data['marks']}")
        else:
            print_error(f"Failed to release marks: {response.status_code}")
            return False
        
        # Test 5: Get exam status
        print_info("\nTest 5: Getting exam status")
        response = requests.get(f"{API_BASE}/exam/status/student1")
        if response.status_code == 200:
            data = response.json()
            print_success("Exam status retrieved")
            print_info(f"Status: {data['status']}")
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
        
        print_success("\n✓ Task 6: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def test_task_7_load_balancing():
    """Test Task 7: Load Balancing with Backup Migration"""
    print_header("Task 7: Load Balancing")
    
    try:
        # Test 1: Submit single request
        print_info("Test 1: Submitting single request")
        submission_data = {
            "student_id": "student1",
            "payload": {"exam_id": "EXAM001", "data": "test_data"}
        }
        response = requests.post(f"{API_BASE}/load-balance/submit", json=submission_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request submitted: {data['message']}")
            print_info(f"Processed by: {data['processed_by']}")
            print_info(f"Request ID: {data['request_id']}")
        else:
            print_error(f"Failed to submit: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 2: Submit multiple requests to test load balancing
        print_info("\nTest 2: Submitting multiple requests (testing load balancing)")
        for i in range(5):
            submission_data = {
                "student_id": f"student{i+1}",
                "payload": {"exam_id": f"EXAM{i:03d}", "data": f"test_data_{i}"}
            }
            response = requests.post(f"{API_BASE}/load-balance/submit", json=submission_data)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Request {i+1} processed by: {data['processed_by']}")
            else:
                print_error(f"Failed to submit request {i+1}")
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Test 3: Get load balance status
        print_info("\nTest 3: Getting load balance status")
        response = requests.get(f"{API_BASE}/load-balance/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Load balance status retrieved")
            print_info(f"Local inflight: {data['local_inflight']}")
            print_info(f"Backup inflight: {data['backup_inflight']}")
            print_info(f"Migration threshold: {data['migration_threshold']}")
        else:
            print_error(f"Failed to get status: {response.status_code}")
            return False
        
        print_success("\n✓ Task 7: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def test_task_8_database():
    """Test Task 8: Distributed Database with 2PC Protocol"""
    print_header("Task 8: Distributed Database with 2PC")
    
    try:
        # Test 1: Read all records
        print_info("Test 1: Reading all database records")
        response = requests.get(f"{API_BASE}/database/all")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data['records'])} records")
            print_info(f"Total records: {data['total']}")
        else:
            print_error(f"Failed to read records: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 2: Read specific record
        print_info("\nTest 2: Reading specific record (23102A0058)")
        response = requests.get(f"{API_BASE}/database/read/23102A0058")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Record found: {data['record']['name']}")
            print_info(f"MSE: {data['record']['mse']}, ESE: {data['record']['ese']}, Total: {data['record']['total']}")
        else:
            print_error(f"Failed to read record: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 3: Update record using 2PC
        print_info("\nTest 3: Updating record using 2PC protocol")
        update_data = {
            "roll_number": "23102A0058",
            "mse": 18,
            "ese": 35
        }
        response = requests.post(f"{API_BASE}/database/update", json=update_data)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Record updated: {data['message']}")
            print_info(f"Protocol: {data['protocol']}")
            print_info(f"New total: {data['new_total']}")
        else:
            print_error(f"Failed to update record: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Test 4: Search records
        print_info("\nTest 4: Searching records (name contains 'Hussain')")
        response = requests.get(f"{API_BASE}/database/search?name=Hussain")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Search completed: {len(data['records'])} results")
            if data['records']:
                print_info(f"First result: {data['records'][0]['name']}")
        else:
            print_error(f"Failed to search: {response.status_code}")
            return False
        
        print_success("\n✓ Task 8: All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Exception during testing: {e}")
        return False

def main():
    """Main testing function"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'Unified Exam Proctoring System - Backend Testing'.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Test server connection first
    if not test_server_connection():
        print_error("\n❌ Cannot proceed without server connection!")
        return
    
    time.sleep(1)
    
    # Track test results
    results = {}
    
    # Run all tests
    results["Task 1-3: Violation Detection"] = test_task_1_3_violation_detection()
    time.sleep(2)
    
    results["Task 4: Clock Synchronization"] = test_task_4_clock_sync()
    time.sleep(2)
    
    results["Task 5: Mutual Exclusion"] = test_task_5_mutual_exclusion()
    time.sleep(2)
    
    results["Task 6: Exam Processing"] = test_task_6_exam_processing()
    time.sleep(2)
    
    results["Task 7: Load Balancing"] = test_task_7_load_balancing()
    time.sleep(2)
    
    results["Task 8: Database with 2PC"] = test_task_8_database()
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for task, result in results.items():
        if result:
            print_success(f"{task}")
        else:
            print_error(f"{task}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED! ({passed}/{total}){RESET}".center(70))
    else:
        print(f"{YELLOW}⚠ SOME TESTS FAILED ({passed}/{total} passed){RESET}".center(70))
    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
