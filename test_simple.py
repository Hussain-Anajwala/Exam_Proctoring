#!/usr/bin/env python3
"""
Simple test to verify server is running and test basic endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_connection():
    print("\n=== Testing Server Connection ===")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✓ Server is running! Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ Server connection failed: {e}")
        return False

def test_violation_detection():
    print("\n=== Task 1-3: Violation Detection ===")
    try:
        # Report first violation
        data = {
            "roll": 58,
            "name": "Hussain",
            "warning": "Please focus!",
            "question_no": 15,
            "violation_no": 1
        }
        response = requests.post(f"{API_BASE}/violation/report", json=data)
        result = response.json()
        print(f"✓ First violation: {result['message']}")
        print(f"  Current marks: {result['current_marks']}%")
        
        # Get marksheet
        response = requests.get(f"{API_BASE}/violation/marksheet")
        result = response.json()
        print(f"✓ Marksheet retrieved: {len(result['marksheet'])} students")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_clock_sync():
    print("\n=== Task 4: Clock Synchronization ===")
    try:
        # Register participants
        participants = [
            {"role": "teacher", "time": "10:30:45"},
            {"role": "student1", "time": "10:30:50"}
        ]
        for p in participants:
            requests.post(f"{API_BASE}/clock/register", json=p)
        print(f"✓ Registered {len(participants)} participants")
        
        # Synchronize
        response = requests.post(f"{API_BASE}/clock/sync")
        result = response.json()
        print(f"✓ Synchronized to: {result['average_time']}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_mutual_exclusion():
    print("\n=== Task 5: Mutual Exclusion ===")
    try:
        # Request critical section
        data = {"student_id": "Student1", "timestamp": 1000}
        response = requests.post(f"{API_BASE}/mutex/request", json=data)
        result = response.json()
        print(f"✓ Request status: {result['status']}")
        
        # Get status
        response = requests.get(f"{API_BASE}/mutex/status")
        result = response.json()
        print(f"✓ Current holder: {result['current_holder']}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_exam_processing():
    print("\n=== Task 6: Exam Processing ===")
    try:
        # Get questions
        response = requests.get(f"{API_BASE}/exam/questions")
        result = response.json()
        print(f"✓ Retrieved {len(result['questions'])} questions")
        
        # Start exam
        response = requests.post(f"{API_BASE}/exam/start/student2")
        result = response.json()
        print(f"✓ Exam started: {result['status']}")
        
        # Submit exam
        data = {"student_id": "student2", "answers": ["C", "A", "B", "A", "B"]}
        response = requests.post(f"{API_BASE}/exam/submit", json=data)
        result = response.json()
        print(f"✓ Exam submitted: {result['score']}/{result['total']}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_load_balancing():
    print("\n=== Task 7: Load Balancing ===")
    try:
        # Submit request
        data = {"student_id": "student1", "payload": {"test": "data"}}
        response = requests.post(f"{API_BASE}/load-balance/submit", json=data)
        result = response.json()
        print(f"✓ Request processed by: {result['processed_by']}")
        
        # Get status
        response = requests.get(f"{API_BASE}/load-balance/status")
        result = response.json()
        print(f"✓ Local inflight: {result['local_inflight']}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_database():
    print("\n=== Task 8: Database with 2PC ===")
    try:
        # Get all records
        response = requests.get(f"{API_BASE}/database/all")
        result = response.json()
        print(f"✓ Retrieved {result['total']} records")
        
        # Read specific record
        response = requests.get(f"{API_BASE}/database/read/23102A0058")
        result = response.json()
        print(f"✓ Record: {result['record']['name']}")
        
        # Update record
        data = {"roll_number": "23102A0058", "mse": 18, "ese": 35}
        response = requests.post(f"{API_BASE}/database/update", json=data)
        result = response.json()
        print(f"✓ Updated: {result['message']}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  BACKEND TESTING - All 8 Tasks")
    print("="*60)
    
    if not test_connection():
        print("\n✗ Cannot connect to server. Please start it first:")
        print("  cd python_server && python start_simple.py")
        return
    
    results = {
        "Task 1-3: Violation Detection": test_violation_detection(),
        "Task 4: Clock Synchronization": test_clock_sync(),
        "Task 5: Mutual Exclusion": test_mutual_exclusion(),
        "Task 6: Exam Processing": test_exam_processing(),
        "Task 7: Load Balancing": test_load_balancing(),
        "Task 8: Database with 2PC": test_database()
    }
    
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for task, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {task}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
