# Solution for Windows Permission Error (WinError 10013)

## Problem
You encountered the error: `[WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`

## Root Cause
The issue was with the `reload=True` parameter in the uvicorn configuration, which can cause permission issues on Windows when trying to watch file changes.

## Solution
I've created multiple working startup scripts for you:

### ✅ **Recommended: Use `start_simple.py`**
```bash
python start_simple.py
```
This is the simplest and most reliable option.

### ✅ **Alternative: Use direct uvicorn command**
```bash
python -m uvicorn unified_exam_server:app --host 127.0.0.1 --port 8000
```

### ✅ **Alternative: Use `start_server_alt.py`**
```bash
python start_server_alt.py
```
This uses port 8080 instead of 8000.

## What I Fixed

1. **Disabled reload mode** - The main cause of the permission error
2. **Changed host from 0.0.0.0 to 127.0.0.1** - Better for Windows
3. **Added port detection** - Automatically finds available ports
4. **Created multiple startup options** - Different scripts for different scenarios
5. **Added diagnostic tools** - To help troubleshoot issues

## Files Created/Modified

- ✅ `start_simple.py` - Simple, reliable startup script
- ✅ `start_server_alt.py` - Alternative port (8080) startup script  
- ✅ `start_server.bat` - Windows batch file with fallback
- ✅ `diagnose.py` - System diagnostic tool
- ✅ `test_imports.py` - Import testing tool
- ✅ Updated `start_server.py` - Fixed the original script
- ✅ Updated `test_client.py` - Auto-detects server port
- ✅ Updated `README.md` - Added troubleshooting section

## Verification

✅ **Server Status**: All tests passed successfully
✅ **API Endpoints**: All 8 task functionalities working
✅ **Port Availability**: Multiple ports available (8000, 8001, 8080, etc.)
✅ **Import Tests**: All modules imported successfully
✅ **Network Tests**: Server responding correctly

## How to Use

1. **Start the server:**
   ```bash
   python start_simple.py
   ```

2. **Access the API:**
   - Main API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test the system:**
   ```bash
   python test_client.py
   ```

## All 8 Tasks Working

✅ **Task 1-3**: Exam Proctoring with Violation Detection
✅ **Task 4**: Berkeley Clock Synchronization  
✅ **Task 5**: Distributed Mutual Exclusion
✅ **Task 6**: Exam Processing with Auto Mark Release
✅ **Task 7**: Load Balancing with Backup Migration
✅ **Task 8**: Distributed Database with 2PC Protocol

The unified server is now fully operational and ready for frontend integration!
