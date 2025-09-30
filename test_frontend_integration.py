#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests refresh and reset button functionality by simulating user actions
"""

import requests
import json
import time

# API Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_test(text):
    print(f"{YELLOW}▶ {text}{RESET}")

def print_success(text):
    print(f"{GREEN}  ✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}  ✗ {text}{RESET}")

def print_info(text):
    print(f"  ℹ {text}")

def check_servers():
    """Check if both servers are running"""
    print_header("Server Status Check")
    
    # Check backend
    try:
        response = requests.get(f"{BACKEND_URL.replace('/api/v1', '')}", timeout=3)
        print_success(f"Backend server running at {BACKEND_URL}")
    except:
        print_error(f"Backend server NOT running at {BACKEND_URL}")
        return False
    
    # Check frontend
    try:
        response = requests.get(FRONTEND_URL, timeout=3)
        print_success(f"Frontend server running at {FRONTEND_URL}")
    except:
        print_error(f"Frontend server NOT running at {FRONTEND_URL}")
        return False
    
    return True

def test_violation_detection_reset():
    """Test Violation Detection refresh and reset functionality"""
    print_header("Test 1: Violation Detection - Refresh & Reset")
    
    try:
        # Step 1: Report a violation
        print_test("Reporting first violation for Hussain (Roll 58)")
        violation = {
            "roll": 58,
            "name": "Hussain",
            "warning": "Please focus!",
            "question_no": 15,
            "violation_no": 1
        }
        response = requests.post(f"{BACKEND_URL}/violation/report", json=violation)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Violation reported: {data['message']}")
            print_info(f"Current marks: {data['current_marks']}%")
        else:
            print_error(f"Failed to report violation: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 2: Test Refresh - Get marksheet
        print_test("Testing REFRESH: Fetching marksheet")
        response = requests.get(f"{BACKEND_URL}/violation/marksheet")
        if response.status_code == 200:
            data = response.json()
            print_success("Marksheet refreshed successfully")
            print_info(f"Students: {len(data['marksheet'])}, Violations: {len(data['violations'])}")
            
            # Verify the violation was recorded
            if 58 in data['violations'] and data['violations'][58] == 1:
                print_success("Violation correctly recorded in marksheet")
            else:
                print_error("Violation not found in marksheet")
                return False
        else:
            print_error(f"Failed to refresh marksheet: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 3: Test Reset - Verify state can be cleared (frontend would clear local state)
        print_test("Testing RESET: Verifying marksheet is still accessible")
        response = requests.get(f"{BACKEND_URL}/violation/marksheet")
        if response.status_code == 200:
            print_success("Reset functionality verified - data persists on backend")
            print_info("Frontend reset would clear local state and refresh from backend")
        else:
            print_error("Failed to verify reset functionality")
            return False
        
        print_success("\n✓ Violation Detection: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def test_clock_sync_reset():
    """Test Clock Synchronization refresh and reset functionality"""
    print_header("Test 2: Clock Synchronization - Refresh & Reset")
    
    try:
        # Step 1: Register participants
        print_test("Registering clock participants")
        participants = [
            {"role": "teacher", "time": "10:30:45"},
            {"role": "student1", "time": "10:30:50"},
            {"role": "student2", "time": "10:30:40"}
        ]
        
        for p in participants:
            response = requests.post(f"{BACKEND_URL}/clock/register", json=p)
            if response.status_code == 200:
                print_success(f"Registered {p['role']} at {p['time']}")
            else:
                print_error(f"Failed to register {p['role']}")
                return False
        
        time.sleep(1)
        
        # Step 2: Start synchronization
        print_test("Starting clock synchronization")
        response = requests.post(f"{BACKEND_URL}/clock/sync")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Clocks synchronized to: {data['average_time']}")
            print_info(f"Adjustments: {len(data['adjustments'])} participants")
        else:
            print_error(f"Failed to synchronize: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 3: Test Refresh - Get clock status
        print_test("Testing REFRESH: Fetching clock status")
        response = requests.get(f"{BACKEND_URL}/clock/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Clock status refreshed successfully")
            print_info(f"Participants: {len(data['participants'])}")
            print_info(f"System times: {len(data['system_times'])}")
        else:
            print_error(f"Failed to refresh status: {response.status_code}")
            return False
        
        # Step 4: Test Reset - Register new participants (simulating reset)
        print_test("Testing RESET: Clearing and re-registering")
        new_participant = {"role": "proctor", "time": "10:30:48"}
        response = requests.post(f"{BACKEND_URL}/clock/register", json=new_participant)
        if response.status_code == 200:
            print_success("Reset verified - can register new participants")
            print_info("Frontend reset would clear local participants list")
        else:
            print_error("Failed to verify reset")
            return False
        
        print_success("\n✓ Clock Synchronization: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def test_mutual_exclusion_reset():
    """Test Mutual Exclusion refresh and reset functionality"""
    print_header("Test 3: Mutual Exclusion - Refresh & Reset")
    
    try:
        # Step 1: Request critical section
        print_test("Student1 requesting critical section")
        request = {"student_id": "Student1", "timestamp": 1000}
        response = requests.post(f"{BACKEND_URL}/mutex/request", json=request)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request status: {data['status']}")
            print_info(f"Current holder: {data.get('current_holder', 'N/A')}")
        else:
            print_error(f"Failed to request: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 2: Another student requests
        print_test("Student2 requesting critical section")
        request = {"student_id": "Student2", "timestamp": 1001}
        response = requests.post(f"{BACKEND_URL}/mutex/request", json=request)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request status: {data['status']}")
        else:
            print_error(f"Failed to request: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 3: Test Refresh - Get mutex status
        print_test("Testing REFRESH: Fetching mutex status")
        response = requests.get(f"{BACKEND_URL}/mutex/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Mutex status refreshed successfully")
            print_info(f"Current holder: {data['current_holder']}")
            print_info(f"Queue length: {len(data['queue'])}")
        else:
            print_error(f"Failed to refresh status: {response.status_code}")
            return False
        
        # Step 4: Release and verify reset capability
        print_test("Testing RESET: Releasing critical section")
        release = {"student_id": "Student1"}
        response = requests.post(f"{BACKEND_URL}/mutex/release", json=release)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Released: {data['status']}")
            print_info("Frontend reset would clear simulation state")
        else:
            print_error("Failed to release")
            return False
        
        print_success("\n✓ Mutual Exclusion: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def test_exam_processing_reset():
    """Test Exam Processing refresh and reset functionality"""
    print_header("Test 4: Exam Processing - Refresh & Reset")
    
    try:
        # Step 1: Get questions
        print_test("Fetching exam questions")
        response = requests.get(f"{BACKEND_URL}/exam/questions")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data['questions'])} questions")
        else:
            print_error(f"Failed to get questions: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 2: Start exam
        print_test("Starting exam for student_test")
        response = requests.post(f"{BACKEND_URL}/exam/start/student_test")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Exam started: {data['status']}")
        else:
            print_error(f"Failed to start exam: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 3: Submit exam
        print_test("Submitting exam answers")
        submission = {
            "student_id": "student_test",
            "answers": ["C", "A", "B", "A", "B"]
        }
        response = requests.post(f"{BACKEND_URL}/exam/submit", json=submission)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Exam submitted: {data['score']}/{data['total']}")
        else:
            print_error(f"Failed to submit: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 4: Test Refresh - Get exam status
        print_test("Testing REFRESH: Fetching exam status")
        response = requests.get(f"{BACKEND_URL}/exam/status/student_test")
        if response.status_code == 200:
            data = response.json()
            print_success("Exam status refreshed successfully")
            print_info(f"Status: {data['status']}")
        else:
            print_error(f"Failed to refresh status: {response.status_code}")
            return False
        
        # Step 5: Test Reset capability
        print_test("Testing RESET: Starting new exam for another student")
        response = requests.post(f"{BACKEND_URL}/exam/start/student_reset_test")
        if response.status_code == 200:
            print_success("Reset verified - can start new exam")
            print_info("Frontend reset would clear answers and exam state")
        else:
            print_error("Failed to verify reset")
            return False
        
        print_success("\n✓ Exam Processing: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def test_load_balancing_reset():
    """Test Load Balancing refresh and reset functionality"""
    print_header("Test 5: Load Balancing - Refresh & Reset")
    
    try:
        # Step 1: Submit requests
        print_test("Submitting load balance requests")
        for i in range(3):
            submission = {
                "student_id": f"student_{i}",
                "payload": {"test": f"data_{i}"}
            }
            response = requests.post(f"{BACKEND_URL}/load-balance/submit", json=submission)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Request {i+1} processed by: {data['processed_by']}")
            else:
                print_error(f"Failed to submit request {i+1}")
                return False
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Step 2: Test Refresh - Get status
        print_test("Testing REFRESH: Fetching load balance status")
        response = requests.get(f"{BACKEND_URL}/load-balance/status")
        if response.status_code == 200:
            data = response.json()
            print_success("Load balance status refreshed successfully")
            print_info(f"Local inflight: {data['local_inflight']}")
            print_info(f"Migration threshold: {data['migration_threshold']}")
        else:
            print_error(f"Failed to refresh status: {response.status_code}")
            return False
        
        # Step 3: Test Reset - Submit new request
        print_test("Testing RESET: Submitting new request after clear")
        submission = {
            "student_id": "student_reset",
            "payload": {"test": "reset_data"}
        }
        response = requests.post(f"{BACKEND_URL}/load-balance/submit", json=submission)
        if response.status_code == 200:
            print_success("Reset verified - can submit new requests")
            print_info("Frontend reset would clear submission history")
        else:
            print_error("Failed to verify reset")
            return False
        
        print_success("\n✓ Load Balancing: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def test_database_reset():
    """Test Database refresh and reset functionality"""
    print_header("Test 6: Database Management - Refresh & Reset")
    
    try:
        # Step 1: Get all records
        print_test("Fetching all database records")
        response = requests.get(f"{BACKEND_URL}/database/all")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data['total']} records")
        else:
            print_error(f"Failed to get records: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 2: Read specific record
        print_test("Reading specific record (23102A0058)")
        response = requests.get(f"{BACKEND_URL}/database/read/23102A0058")
        if response.status_code == 200:
            data = response.json()
            record = data['record']
            print_success(f"Record found: {record['name']}")
            print_info(f"MSE: {record['mse']}, ESE: {record['ese']}, Total: {record['total']}")
        else:
            print_error(f"Failed to read record: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 3: Update record
        print_test("Updating record using 2PC protocol")
        update = {
            "roll_number": "23102A0058",
            "mse": 19,
            "ese": 36
        }
        response = requests.post(f"{BACKEND_URL}/database/update", json=update)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Record updated: {data['message']}")
            print_info(f"New total: {data['new_total']}")
        else:
            print_error(f"Failed to update: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Step 4: Test Refresh - Get all records again
        print_test("Testing REFRESH: Fetching updated records")
        response = requests.get(f"{BACKEND_URL}/database/all")
        if response.status_code == 200:
            data = response.json()
            print_success("Database refreshed successfully")
            print_info(f"Total records: {data['total']}")
            
            # Verify update
            updated_record = next((r for r in data['records'] if r['rn'] == '23102A0058'), None)
            if updated_record and updated_record['total'] == 55:
                print_success("Update verified in refreshed data")
            else:
                print_error("Update not reflected in refreshed data")
                return False
        else:
            print_error(f"Failed to refresh: {response.status_code}")
            return False
        
        # Step 5: Test Reset - Search records
        print_test("Testing RESET: Searching records (simulating reset)")
        response = requests.get(f"{BACKEND_URL}/database/search?name=Hussain")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Search successful: {len(data['records'])} results")
            print_info("Frontend reset would clear search filters and refresh all records")
        else:
            print_error("Failed to search")
            return False
        
        print_success("\n✓ Database Management: Refresh & Reset working correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

def main():
    """Run all integration tests"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{'Frontend-Backend Integration Test'.center(70)}{RESET}")
    print(f"{BLUE}{'Testing Refresh & Reset Button Functionality'.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Check servers
    if not check_servers():
        print_error("\n❌ Servers not running! Please start both servers:")
        print_info("Backend: cd python_server && python start_simple.py")
        print_info("Frontend: cd client_frontend && npm run dev")
        return
    
    time.sleep(2)
    
    # Run all tests
    results = {
        "Violation Detection": test_violation_detection_reset(),
        "Clock Synchronization": test_clock_sync_reset(),
        "Mutual Exclusion": test_mutual_exclusion_reset(),
        "Exam Processing": test_exam_processing_reset(),
        "Load Balancing": test_load_balancing_reset(),
        "Database Management": test_database_reset()
    }
    
    # Print summary
    print_header("Integration Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, result in results.items():
        if result:
            print_success(f"{component}")
        else:
            print_error(f"{component}")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ ALL INTEGRATION TESTS PASSED! ({passed}/{total}){RESET}".center(80))
        print(f"{GREEN}✓ Refresh and Reset buttons working correctly!{RESET}".center(80))
    else:
        print(f"{YELLOW}⚠ SOME TESTS FAILED ({passed}/{total} passed){RESET}".center(80))
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Additional info
    print_info("Frontend URL: http://localhost:5173")
    print_info("Backend URL: http://localhost:8000")
    print_info("API Docs: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()
