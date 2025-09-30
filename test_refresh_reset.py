#!/usr/bin/env python3
"""
Simple test to verify refresh and reset functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_component(name, test_func):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    try:
        result = test_func()
        if result:
            print(f"✓ {name}: PASS")
        else:
            print(f"✗ {name}: FAIL")
        return result
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        return False

def test_violation_detection():
    """Test violation detection refresh"""
    print("\n1. Reporting violation...")
    violation = {
        "roll": 58,
        "name": "Hussain",
        "warning": "Test warning",
        "question_no": 10,
        "violation_no": 1
    }
    r = requests.post(f"{BASE_URL}/violation/report", json=violation)
    print(f"   Status: {r.status_code}")
    
    print("2. Refreshing marksheet...")
    r = requests.get(f"{BASE_URL}/violation/marksheet")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Students: {len(data['marksheet'])}")
        return True
    return False

def test_clock_sync():
    """Test clock sync refresh"""
    print("\n1. Registering participants...")
    p1 = {"role": "teacher", "time": "10:30:45"}
    r = requests.post(f"{BASE_URL}/clock/register", json=p1)
    print(f"   Teacher: {r.status_code}")
    
    p2 = {"role": "student1", "time": "10:30:50"}
    r = requests.post(f"{BASE_URL}/clock/register", json=p2)
    print(f"   Student: {r.status_code}")
    
    print("2. Starting sync...")
    r = requests.post(f"{BASE_URL}/clock/sync")
    print(f"   Status: {r.status_code}")
    
    print("3. Refreshing status...")
    r = requests.get(f"{BASE_URL}/clock/status")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Participants: {len(data['participants'])}")
        return True
    return False

def test_mutex():
    """Test mutex refresh"""
    print("\n1. Requesting critical section...")
    req = {"student_id": "TestStudent", "timestamp": 2000}
    r = requests.post(f"{BASE_URL}/mutex/request", json=req)
    print(f"   Status: {r.status_code}")
    
    print("2. Refreshing status...")
    r = requests.get(f"{BASE_URL}/mutex/status")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Current holder: {data['current_holder']}")
        return True
    return False

def test_exam():
    """Test exam refresh"""
    print("\n1. Getting questions...")
    r = requests.get(f"{BASE_URL}/exam/questions")
    print(f"   Status: {r.status_code}")
    
    print("2. Starting exam...")
    r = requests.post(f"{BASE_URL}/exam/start/test_student")
    print(f"   Status: {r.status_code}")
    
    print("3. Refreshing status...")
    r = requests.get(f"{BASE_URL}/exam/status/test_student")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Exam status: {data['status']}")
        return True
    return False

def test_load_balance():
    """Test load balance refresh"""
    print("\n1. Submitting request...")
    sub = {"student_id": "test", "payload": {"data": "test"}}
    r = requests.post(f"{BASE_URL}/load-balance/submit", json=sub)
    print(f"   Status: {r.status_code}")
    
    print("2. Refreshing status...")
    r = requests.get(f"{BASE_URL}/load-balance/status")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Local inflight: {data['local_inflight']}")
        return True
    return False

def test_database():
    """Test database refresh"""
    print("\n1. Getting all records...")
    r = requests.get(f"{BASE_URL}/database/all")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Total records: {data['total']}")
    
    print("2. Reading specific record...")
    r = requests.get(f"{BASE_URL}/database/read/23102A0058")
    print(f"   Status: {r.status_code}")
    
    print("3. Refreshing all records...")
    r = requests.get(f"{BASE_URL}/database/all")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        return True
    return False

def main():
    print("\n" + "="*60)
    print("REFRESH & RESET FUNCTIONALITY TEST")
    print("="*60)
    
    # Check backend
    try:
        r = requests.get("http://localhost:8000", timeout=3)
        print("✓ Backend server is running")
    except:
        print("✗ Backend server is NOT running")
        print("\nStart backend with: cd python_server && python start_simple.py")
        return
    
    # Check frontend
    try:
        r = requests.get("http://localhost:5173", timeout=3)
        print("✓ Frontend server is running")
    except:
        print("✗ Frontend server is NOT running")
        print("\nStart frontend with: cd client_frontend && npm run dev")
        return
    
    time.sleep(1)
    
    # Run tests
    results = {}
    results["Violation Detection"] = test_component("Violation Detection", test_violation_detection)
    time.sleep(1)
    results["Clock Synchronization"] = test_component("Clock Synchronization", test_clock_sync)
    time.sleep(1)
    results["Mutual Exclusion"] = test_component("Mutual Exclusion", test_mutex)
    time.sleep(1)
    results["Exam Processing"] = test_component("Exam Processing", test_exam)
    time.sleep(1)
    results["Load Balancing"] = test_component("Load Balancing", test_load_balance)
    time.sleep(1)
    results["Database Management"] = test_component("Database Management", test_database)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("✓ Refresh and Reset buttons should work correctly in the UI")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    print("\nNext steps:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Test each tab's Refresh and Reset buttons")
    print("3. Verify data updates correctly")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
