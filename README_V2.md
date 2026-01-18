# FairMark V2.0 - Automated Watcher Service

## 🚀 Complete Redesign - Always-Running System

FairMark V2.0 is a fully automated, event-driven evaluation system that monitors ALL Canvas submissions 24/7 without any manual configuration.

## ✨ Key Features

### 1. **Always-Running Watcher**
- ✅ Automatically starts when the system boots up
- ✅ Monitors ALL courses and assignments dynamically
- ✅ No manual assignment ID configuration needed
- ✅ Checks Canvas every 30 seconds for instant detection
- ✅ Runs continuously 24/7

### 2. **Dynamic Discovery**
- ✅ Automatically discovers all active courses
- ✅ Automatically discovers all assignments
- ✅ No `assignments_to_monitor.json` file needed
- ✅ Scales to handle any number of courses/assignments

### 3. **Multiple Submission Support**
- ✅ Each submission attempt gets its own evaluation
- ✅ Each attempt gets its own feedback comment
- ✅ Attempt numbers tracked and displayed
- ✅ Most recent comments appear at top in Canvas

### 4. **Complete Logging**
- ✅ All activity logged to terminal in real-time
- ✅ Detailed logs for every submission detected
- ✅ Evaluation progress tracked
- ✅ Error messages clearly displayed

### 5. **Testing API**
- ✅ Built-in testing endpoints
- ✅ Easy to verify system is working
- ✅ Mock evaluation mode for testing
- ✅ Interactive API documentation

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     FairMark V2.0 System                    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   FastAPI Server Starts   │
              │   (Port 8000)             │
              └──────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   Watcher Auto-Starts     │
              │   (Lifespan Event)        │
              └──────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   Every 30 Seconds:       │
              │   1. Scan all courses     │
              │   2. Scan all assignments │
              │   3. Check submissions    │
              └──────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   New Submission Found?   │
              └──────────────────────────┘
                     │              │
                    Yes            No
                     │              │
                     ▼              ▼
        ┌────────────────────┐   Continue
        │  POST /evaluate     │   Watching
        │  - Download file    │
        │  - AI evaluation    │
        │  - Post comment     │
        └────────────────────┘
                     │
                     ▼
        ┌────────────────────┐
        │  Mark as Processed  │
        │  (Track attempt #)  │
        └────────────────────┘
```

## 🚀 Quick Start

### Start the System

```bash
cd /Users/utin/Desktop/Desktop/FairMark
./start_watcher.sh
```

**That's it!** The watcher starts automatically and monitors ALL submissions.

### What You'll See

```
╔════════════════════════════════════════════════════════════════╗
║          FAIRMARK V2.0 - AUTOMATED EVALUATION SYSTEM           ║
║              Always-Running Watcher Service                    ║
╚════════════════════════════════════════════════════════════════╝

✅ Loading configuration from .env...
🔄 Stopping any existing FairMark processes...

╔════════════════════════════════════════════════════════════════╗
║                  STARTING FAIRMARK SYSTEM                      ║
╚════════════════════════════════════════════════════════════════╝

🚀 FairMark System Starting...
✅ Watcher service started automatically
🔄 Now monitoring ALL courses and assignments 24/7

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000

🔍 Scanning all courses for new submissions...
📚 Found 5 active courses
📚 Course: CS 536 - Software Engineering (10 assignments)
✅ Scan complete. Checked 45 assignments across 5 courses
⏱️  Scan completed in 3.25 seconds
⏳ Next scan in 30 seconds...
```

### When a New Submission is Detected

```
🆕 NEW SUBMISSION DETECTED!
   📚 Course: 13721745
   📋 Assignment: Risk Management Plan (ID: 61335917)
   👤 Student: 121891198
   📄 Submission ID: 741915248
   🔢 Attempt: 2
   ⏰ Submitted: 2026-01-18T14:30:45Z
   📎 Attachments: 1

🤖 Evaluating submission 741915248
   📋 Assignment: 61335917
   👤 User: 121891198
   🔢 Attempt: 2
   📅 Submitted: 2026-01-18T14:30:45Z

🔍 Fetching submission details...
✅ Submission fetched: ID 741915248
🔍 Fetching assignment details...
✅ Assignment fetched: Risk Management Plan
📊 Found 5 rubric items
✅ Submission is ON TIME
📎 Processing attachment: risk_plan_v2.pdf
⬇️  Downloading submission file...
✅ File downloaded: risk_plan_v2.pdf
📝 Building evaluation prompt...
🤖 Generating AI evaluation comment...
   This may take 30-60 seconds...
✅ Comment generated (1245 chars)
📤 Posting comment to Canvas...
✅ Comment posted successfully to Canvas!
🗑️  Temporary files cleaned up

✅ Submission processed successfully!
```

## 📊 API Endpoints

### Health & Status

#### **GET** `/health`
Check system health and configuration.

```bash
curl http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "ok": true,
  "service": "FairMark Automated Evaluation System",
  "version": "2.0.0",
  "canvas_base_url_set": true,
  "canvas_token_set": true,
  "watcher_running": true,
  "timestamp": "2026-01-18T14:30:00"
}
```

#### **GET** `/watcher/status`
Get current watcher service status.

```bash
curl http://127.0.0.1:8000/watcher/status
```

**Response:**
```json
{
  "is_running": true,
  "check_interval": 30,
  "total_submissions_tracked": 47,
  "active_courses": 5,
  "active_assignments": 45
}
```

#### **GET** `/watcher/submissions`
See all tracked submissions and attempts.

```bash
curl http://127.0.0.1:8000/watcher/submissions
```

**Response:**
```json
{
  "total_tracked": 25,
  "submissions": [
    {
      "course_id": 13721745,
      "assignment_id": 61335917,
      "user_id": 121891198,
      "attempts": [1, 2, 3]
    }
  ]
}
```

### Testing Endpoints

#### **GET** `/test/courses`
List all active courses.

```bash
curl http://127.0.0.1:8000/test/courses
```

#### **GET** `/test/assignments/{course_id}`
List all assignments for a course.

```bash
curl http://127.0.0.1:8000/test/assignments/13721745
```

#### **GET** `/test/submissions/{course_id}/{assignment_id}`
List all submissions for an assignment.

```bash
curl http://127.0.0.1:8000/test/submissions/13721745/61335917
```

**Response Example:**
```json
{
  "success": true,
  "course_id": 13721745,
  "assignment_id": 61335917,
  "count": 3,
  "submissions": [
    {
      "id": 741915248,
      "user_id": 121891198,
      "workflow_state": "submitted",
      "submitted_at": "2026-01-18T14:30:45Z",
      "attempt": 2,
      "has_attachments": true
    }
  ]
}
```

#### **POST** `/test/evaluate-mock`
Test evaluation without AI (posts mock comment).

```bash
curl -X POST "http://127.0.0.1:8000/test/evaluate-mock?course_id=13721745&assignment_id=61335917&user_id=121891198&submission_id=741915248"
```

### Core Evaluation Endpoint

#### **POST** `/evaluate`
Main evaluation endpoint (called automatically by watcher).

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": 741915248,
    "course_id": 13721745,
    "assignment_id": 61335917,
    "user_id": 121891198,
    "attempt": 2,
    "submitted_at": "2026-01-18T14:30:45Z"
  }'
```

## 🧪 Testing Your System

### Step 1: Start the System
```bash
./start_watcher.sh
```

### Step 2: Check Health
Open browser to: http://127.0.0.1:8000/health

### Step 3: View API Documentation
Open browser to: http://127.0.0.1:8000/docs

### Step 4: Test Course Discovery
```bash
curl http://127.0.0.1:8000/test/courses
```

### Step 5: Test Assignment Discovery
```bash
# Replace 13721745 with your course ID from step 4
curl http://127.0.0.1:8000/test/assignments/13721745
```

### Step 6: Test Submission Detection
```bash
# Replace with your course and assignment IDs
curl http://127.0.0.1:8000/test/submissions/13721745/61335917
```

### Step 7: Test Mock Evaluation
```bash
# Replace with your actual IDs
curl -X POST "http://127.0.0.1:8000/test/evaluate-mock?course_id=13721745&assignment_id=61335917&user_id=121891198&submission_id=741915248"
```

Check Canvas to see if the mock comment was posted!

## 📋 Key Differences from V1

| Feature | V1 (Old) | V2 (New) |
|---------|----------|----------|
| Assignment Config | Manual JSON file | Fully automatic |
| Discovery | Static list | Dynamic scanning |
| Startup | Separate scripts | Single command |
| Watcher | External Python script | Built-in to FastAPI |
| Check Interval | 5 minutes | 30 seconds |
| Multiple Attempts | Basic support | Full tracking |
| Testing | Manual scripts | Built-in API |
| Logging | Mixed | Structured & clear |

## 🎓 Canvas Comment Priority

Canvas displays comments in **reverse chronological order** (newest first).

Each submission attempt gets its own comment with:
```
[Attempt #2]

Overall evaluation (short):
...
```

This ensures:
- ✅ Latest submission comment appears at top
- ✅ Older attempts remain visible below
- ✅ Students can compare feedback across attempts

## 🛑 Stopping the System

Press `Ctrl+C` in the terminal, or:

```bash
pkill -f "uvicorn app.main"
```

The watcher will gracefully shutdown.

## 📝 Environment Variables

Required in `.env`:
```bash
CANVAS_BASE_URL=https://canvas.instructure.com
CANVAS_TOKEN=your_canvas_api_token_here
OPENAI_API_KEY=your_openai_key_here
POLICY_TEXT=Your evaluation policy text here
```

## 🔧 Configuration

- **Check Interval**: Edit `app/watcher.py`, line with `SubmissionWatcher(check_interval=30)`
- **Port**: Edit `start_watcher.sh`, change `--port 8000`

## 📊 System Requirements

- Python 3.9+
- FastAPI
- OpenAI API access
- Canvas API token with appropriate permissions

## 🚨 Important Notes

1. **No Manual Configuration**: System discovers everything automatically
2. **Instant Detection**: 30-second checks ensure fast response
3. **Multiple Attempts**: Each resubmission is evaluated independently
4. **Instructor Authority**: All evaluations are comments, not grades
5. **Scalable**: Handles unlimited courses and assignments

## 🎉 You're Ready!

Your FairMark V2.0 system is now a fully automated, always-running evaluation service that monitors all Canvas submissions 24/7!

Visit http://127.0.0.1:8000/docs for interactive API testing.
