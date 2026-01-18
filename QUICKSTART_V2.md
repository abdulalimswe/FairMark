# 🚀 FairMark V2.0 - Quick Start Guide

## ✅ System Successfully Redesigned!

Your FairMark system has been completely redesigned as an always-running, event-driven watcher service that:

- ✅ Monitors ALL Canvas courses and assignments automatically
- ✅ No manual assignment configuration needed
- ✅ Detects submissions instantly (30-second intervals)
- ✅ Supports multiple submission attempts
- ✅ Each attempt gets its own evaluation and comment
- ✅ Comments appear in Canvas with [Attempt #N] markers
- ✅ Comprehensive API for testing
- ✅ All logs output to terminal

## 🎯 How to Run

### Simple Start

```bash
cd /Users/utin/Desktop/Desktop/FairMark
./start_watcher.sh
```

The watcher will start automatically and begin monitoring all submissions!

## 📊 API Endpoints for Testing

Once the server is running on http://127.0.0.1:8000, you can access:

### 1. Interactive API Documentation
**Open in browser:** http://127.0.0.1:8000/docs

This gives you a full interactive interface to test all endpoints!

### 2. Health Check
```bash
curl http://127.0.0.1:8000/health
```

### 3. Watcher Status
```bash
curl http://127.0.0.1:8000/watcher/status
```

### 4. View Tracked Submissions
```bash
curl http://127.0.0.1:8000/watcher/submissions
```

### 5. Test: List All Courses
```bash
curl http://127.0.0.1:8000/test/courses
```

###6. Test: List Assignments for a Course
```bash
curl http://127.0.0.1:8000/test/assignments/13721745
```

### 7. Test: List Submissions for an Assignment
```bash
curl http://127.0.0.1:8000/test/submissions/13721745/61335917
```

### 8. Test: Post Mock Comment (No AI)
```bash
curl -X POST "http://127.0.0.1:8000/test/evaluate-mock?course_id=13721745&assignment_id=61335917&user_id=121891198&submission_id=741915248"
```

This will post a test comment to Canvas to verify the system works!

## 📝 What You'll See in Terminal

### On Startup:
```
╔════════════════════════════════════════════════════════════════╗
║          FAIRMARK V2.0 - AUTOMATED EVALUATION SYSTEM           ║
║              Always-Running Watcher Service                    ║
╚════════════════════════════════════════════════════════════════╝

✅ Loading configuration from .env...
🚀 Starting FairMark server...

2026-01-19 00:00:00 [INFO] ======================================================================
2026-01-19 00:00:00 [INFO] 🚀 FairMark System Starting...
2026-01-19 00:00:00 [INFO] ======================================================================
2026-01-19 00:00:00 [INFO] ✅ Watcher service starting in background
2026-01-19 00:00:00 [INFO] 🔄 Will begin monitoring ALL courses and assignments
2026-01-19 00:00:00 [INFO] ======================================================================

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

2026-01-19 00:00:01 [INFO] 🔍 Scanning all courses for new submissions...
2026-01-19 00:00:01 [INFO] 📚 Found 5 active courses
2026-01-19 00:00:02 [INFO] 📚 Course: CS 536 - Software Engineering (12 assignments)
2026-01-19 00:00:03 [INFO] 📚 Course: CS 400 - Data Structures (8 assignments)
```

### When New Submission Detected:
```
2026-01-19 00:05:30 [INFO] 
2026-01-19 00:05:30 [INFO] 🆕 NEW SUBMISSION DETECTED!
2026-01-19 00:05:30 [INFO]    📚 Course: 13721745
2026-01-19 00:05:30 [INFO]    📋 Assignment: Risk Management Plan (ID: 61335917)
2026-01-19 00:05:30 [INFO]    👤 Student: 121891198
2026-01-19 00:05:30 [INFO]    📄 Submission ID: 741915248
2026-01-19 00:05:30 [INFO]    🔢 Attempt: 2
2026-01-19 00:05:30 [INFO]    ⏰ Submitted: 2026-01-19T00:05:15Z
2026-01-19 00:05:30 [INFO]    📎 Attachments: 1
2026-01-19 00:05:30 [INFO] 
2026-01-19 00:05:30 [INFO] 🤖 Evaluating submission 741915248
2026-01-19 00:05:31 [INFO]    📋 Assignment: 61335917
2026-01-19 00:05:31 [INFO]    👤 User: 121891198
2026-01-19 00:05:31 [INFO]    🔢 Attempt: 2
2026-01-19 00:05:31 [INFO] ======================================================================
2026-01-19 00:05:31 [INFO] 📝 EVALUATION REQUEST RECEIVED
2026-01-19 00:05:31 [INFO]    Submission ID: 741915248
2026-01-19 00:05:31 [INFO]    Course ID: 13721745
2026-01-19 00:05:31 [INFO]    Assignment ID: 61335917
2026-01-19 00:05:31 [INFO]    User ID: 121891198
2026-01-19 00:05:31 [INFO]    Attempt: 2
2026-01-19 00:05:32 [INFO] 🔍 Fetching submission details...
2026-01-19 00:05:32 [INFO] ✅ Submission fetched: ID 741915248
2026-01-19 00:05:33 [INFO] 📊 Found 5 rubric items
2026-01-19 00:05:33 [INFO] ✅ Submission is ON TIME
2026-01-19 00:05:33 [INFO] 📎 Processing attachment: plan_v2.pdf
2026-01-19 00:05:34 [INFO] ⬇️  Downloading submission file...
2026-01-19 00:05:35 [INFO] ✅ File downloaded: plan_v2.pdf
2026-01-19 00:05:35 [INFO] 📝 Building evaluation prompt...
2026-01-19 00:05:35 [INFO] 🤖 Generating AI evaluation comment...
2026-01-19 00:05:35 [INFO]    This may take 30-60 seconds...
2026-01-19 00:06:15 [INFO] ✅ Comment generated (1245 chars)
2026-01-19 00:06:15 [INFO] 📤 Posting comment to Canvas...
2026-01-19 00:06:16 [INFO] ✅ Comment posted successfully to Canvas!
2026-01-19 00:06:16 [INFO] 🗑️  Temporary files cleaned up
2026-01-19 00:06:16 [INFO] ======================================================================
2026-01-19 00:06:16 [INFO] ✅ EVALUATION COMPLETED SUCCESSFULLY
2026-01-19 00:06:16 [INFO] ======================================================================
2026-01-19 00:06:16 [INFO]    ✅ Submission processed successfully!
```

## 🔧 Files Created

| File | Purpose |
|------|---------|
| `app/watcher.py` | Continuous watcher service |
| `app/main.py` | FastAPI application with watcher integration |
| `start_watcher.sh` | Easy startup script |
| `README_V2.md` | Complete documentation |
| `QUICKSTART_V2.md` | This file |

## 🎯 Key Features Implemented

### 1. Dynamic Discovery
- ✅ No `assignments_to_monitor.json` needed
- ✅ Automatically discovers all courses
- ✅ Automatically discovers all assignments
- ✅ Scans everything dynamically

### 2. Multiple Attempts
- ✅ Tracks attempt numbers
- ✅ Each attempt evaluated separately
- ✅ Comments labeled with [Attempt #N]
- ✅ All attempts visible in Canvas

### 3. Event-Driven
- ✅ Checks every 30 seconds
- ✅ Instant detection of new submissions
- ✅ Asynchronous processing
- ✅ Non-blocking operations

### 4. Complete Logging
- ✅ All activity logged to terminal
- ✅ Structured log format with timestamps
- ✅ Clear status indicators (🚀 ✅ ❌ 🔍 etc.)
- ✅ Progress tracking

### 5. Testing API
- ✅ `/test/courses` - List all courses
- ✅ `/test/assignments/{course_id}` - List assignments
- ✅ `/test/submissions/{course_id}/{assignment_id}` - List submissions
- ✅ `/test/evaluate-mock` - Test without AI
- ✅ `/docs` - Interactive API documentation

## 🧪 Quick Test Sequence

1. **Start the system:**
   ```bash
   ./start_watcher.sh
   ```

2. **Open browser to API docs:**
   ```
   http://127.0.0.1:8000/docs
   ```

3. **Test course discovery:**
   - Go to `/test/courses` endpoint in the docs
   - Click "Try it out" → "Execute"
   - See all your courses!

4. **Test assignment discovery:**
   - Go to `/test/assignments/{course_id}`
   - Enter a course_id from step 3
   - Click "Execute"
   - See all assignments!

5. **Test submission discovery:**
   - Go to `/test/submissions/{course_id}/{assignment_id}`
   - Enter IDs from previous steps
   - Click "Execute"
   - See all submissions!

6. **Test mock evaluation:**
   - Go to `/test/evaluate-mock`
   - Fill in the parameters with real IDs
   - Click "Execute"
   - Check Canvas - you should see a test comment!

## 🎓 Canvas Comment Format

Each evaluation posts a comment like this:

```
[Attempt #2]

Overall evaluation (short):
Your submission shows good progress. The risk management plan now includes 
a clear agenda and risk statements, though some mitigation strategies could 
be more detailed.

Rubric breakdown:
Clear agenda slide with proper structure — 4.5/5
Comment: The agenda is well-structured with clear sections for risks and 
mitigations. Minor improvements needed in formatting.

Risk statements clearly defined — 5/5
Comment: All major risks are clearly identified and well-articulated.

...
```

## 🛑 Stopping the System

Press `Ctrl+C` in the terminal, or:

```bash
pkill -f "uvicorn app.main"
```

## ❓ Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill any process on port 8000
kill -9 $(lsof -ti:8000)

# Try starting again
./start_watcher.sh
```

### Watcher not detecting submissions
- Check logs in terminal
- Verify Canvas API token has proper permissions
- Test endpoints manually in `/docs`

### Comments not posting to Canvas
- Use `/test/evaluate-mock` to test
- Check Canvas API token permissions
- Verify user_id is correct

## 🎉 You're All Set!

Your FairMark V2.0 system is now a fully automated, always-running evaluation service!

**Next Steps:**
1. Start the system: `./start_watcher.sh`
2. Open API docs: http://127.0.0.1:8000/docs
3. Test the endpoints
4. Submit a test assignment in Canvas
5. Watch the terminal logs as it's detected and evaluated!

The system will now automatically:
- ✅ Discover all your courses
- ✅ Monitor all assignments
- ✅ Detect new submissions instantly
- ✅ Evaluate them with AI
- ✅ Post feedback comments
- ✅ Track multiple attempts
- ✅ Run 24/7 without manual intervention

**Everything is dynamic - no configuration files needed!**
