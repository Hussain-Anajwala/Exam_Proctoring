# Unified Exam Proctoring System

A comprehensive Python server that combines all 8 exam system tasks into a single FastAPI application with REST API endpoints.

## Features

This unified server implements all functionalities from the original 8 tasks:

### Task 1-3: Exam Proctoring with Violation Detection
- Real-time violation reporting and tracking
- Automatic mark deduction based on violations
- Student termination after 2 violations
- Final marksheet generation

### Task 4: Berkeley Clock Synchronization
- Multi-participant clock synchronization
- Average time calculation and adjustment
- Real-time clock updates

### Task 5: Distributed Mutual Exclusion
- Token-based mutual exclusion algorithm
- Request queue management
- Critical section access control

### Task 6: Exam Processing with Auto Mark Release
- Exam question management
- Automatic answer evaluation
- Mark release system
- Student status tracking

### Task 7: Load Balancing with Backup Migration
- Dynamic load balancing
- Automatic migration to backup servers
- Queue management and processing

### Task 8: Distributed Database with 2PC Protocol
- Student record management
- Two-Phase Commit protocol implementation
- Database search and update operations

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python start_server.py
```

The server will automatically find an available port starting from 8000.

## Troubleshooting

### Windows Permission Error (WinError 10013)

If you encounter `[WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`, try these solutions:

#### Solution 1: Use Alternative Port
```bash
python start_server_alt.py
```
This uses port 8080 instead of 8000.

#### Solution 2: Run as Administrator
1. Right-click on PowerShell/Command Prompt
2. Select "Run as Administrator"
3. Navigate to the project directory
4. Run `python start_server.py`

#### Solution 3: Use Batch File
```bash
start_server.bat
```
This will try port 8000 first, then automatically fall back to port 8080.

#### Solution 4: Check Windows Firewall
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Add Python or your terminal application to the allowed list

#### Solution 5: Check for Port Conflicts
```bash
netstat -ano | findstr :8000
```
If another process is using port 8000, either:
- Close that application
- Use a different port (modify the script)
- Kill the process using the PID shown

### Other Common Issues

**Port Already in Use**: The improved startup script automatically finds available ports.

**Module Not Found**: Make sure you're in the correct directory and have activated your virtual environment:
```bash
# Activate virtual environment
venv\Scripts\activate

# Verify you're in the right directory
cd python_server
```

## API Endpoints

### Violation Detection (Task 1-3)
- `POST /api/v1/violation/report` - Report a violation
- `GET /api/v1/violation/status/{roll}` - Get violation status
- `GET /api/v1/violation/marksheet` - Get final marksheet

### Clock Synchronization (Task 4)
- `POST /api/v1/clock/register` - Register clock participant
- `POST /api/v1/clock/sync` - Start synchronization
- `GET /api/v1/clock/status` - Get clock status

### Mutual Exclusion (Task 5)
- `POST /api/v1/mutex/request` - Request critical section
- `POST /api/v1/mutex/release` - Release critical section
- `GET /api/v1/mutex/status` - Get mutex status

### Exam Processing (Task 6)
- `GET /api/v1/exam/questions` - Get exam questions
- `POST /api/v1/exam/start/{student_id}` - Start exam
- `POST /api/v1/exam/submit` - Submit exam
- `POST /api/v1/exam/release-marks/{student_id}` - Release marks
- `GET /api/v1/exam/status/{student_id}` - Get exam status

### Load Balancing (Task 7)
- `POST /api/v1/load-balance/submit` - Submit for processing
- `GET /api/v1/load-balance/status` - Get load balance status

### Distributed Database (Task 8)
- `GET /api/v1/database/read/{roll_number}` - Read student record
- `POST /api/v1/database/update` - Update student record
- `GET /api/v1/database/all` - Get all records
- `GET /api/v1/database/search` - Search records

### General
- `GET /` - Root endpoint with API information
- `GET /api/v1/status` - System status
- `GET /api/v1/docs` - API documentation

## Testing

Run the test client to verify all functionalities:

```bash
python test_client.py
```

This will test all 8 task functionalities and demonstrate the API usage.

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Example Usage

### Report a Violation
```python
import requests

violation = {
    "roll": 58,
    "name": "Hussain",
    "warning": "Please focus, exam in progress!",
    "question_no": 15,
    "violation_no": 1
}

response = requests.post("http://localhost:8000/api/v1/violation/report", json=violation)
print(response.json())
```

### Start Clock Synchronization
```python
# Register participants
participants = [
    {"role": "teacher", "time": "10:30:45"},
    {"role": "student1", "time": "10:30:50"}
]

for participant in participants:
    requests.post("http://localhost:8000/api/v1/clock/register", json=participant)

# Start synchronization
response = requests.post("http://localhost:8000/api/v1/clock/sync")
print(response.json())
```

### Submit Exam
```python
submission = {
    "student_id": "student1",
    "answers": ["C", "A", "B", "A", "B"]
}

response = requests.post("http://localhost:8000/api/v1/exam/submit", json=submission)
print(response.json())
```

## Architecture

The unified server uses:
- **FastAPI** for the web framework and API
- **Pydantic** for data validation
- **Asyncio** for asynchronous processing
- **Threading** for concurrent operations
- **Background tasks** for load balancing

## Configuration

The server can be configured by modifying the constants at the top of `unified_exam_server.py`:
- Student names and roll numbers
- Exam questions
- Load balancing thresholds
- Database records

## Error Handling

The API includes comprehensive error handling:
- HTTP status codes for different error types
- Detailed error messages
- Input validation
- Graceful degradation

## Performance

The server is designed for high performance:
- Asynchronous request handling
- Background task processing
- Efficient data structures
- Minimal blocking operations
