# FairMark V2.0 - Automated Education Evaluation System

## 🎯 Overview

FairMark is an **always-running, event-driven evaluation system** that monitors ALL Canvas LMS submissions 24/7 and provides automated AI-powered feedback.

### ✨ Key Features

- ✅ **Always Running** - Monitors all courses and assignments automatically
- ✅ **Dynamic Discovery** - No manual configuration needed
- ✅ **Instant Detection** - Checks every 30 seconds for new submissions
- ✅ **Multiple Attempts** - Each resubmission gets separate evaluation
- ✅ **AI-Powered** - GPT-4 based structured feedback
- ✅ **Canvas Integration** - Automatic comment posting
- ✅ **Testing API** - Comprehensive endpoints for testing

## 🚀 Quick Start

### Start the System

```bash
cd /Users/utin/Desktop/Desktop/FairMark
./start_watcher.sh
```

**That's it!** The system will:
1. Start the FastAPI server on port 8000
2. Launch the watcher service automatically
3. Begin monitoring ALL courses and assignments
4. Detect and evaluate new submissions instantly

### Stop the System

Press `Ctrl+C` in the terminal

## 📊 API Endpoints

Once running, access these endpoints:

### Documentation
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

### Status & Monitoring
- **Watcher Status**: http://127.0.0.1:8000/watcher/status
- **Tracked Submissions**: http://127.0.0.1:8000/watcher/submissions

### Testing Endpoints
- **List Courses**: http://127.0.0.1:8000/test/courses
- **List Assignments**: http://127.0.0.1:8000/test/assignments/{course_id}
- **List Submissions**: http://127.0.0.1:8000/test/submissions/{course_id}/{assignment_id}
- **Mock Evaluation**: POST to http://127.0.0.1:8000/test/evaluate-mock

## 🧪 Testing Your System

### 1. Check Health
```bash
curl http://127.0.0.1:8000/health
```

### 2. List Your Courses
```bash
curl http://127.0.0.1:8000/test/courses
```

### 3. List Assignments
```bash
curl http://127.0.0.1:8000/test/assignments/YOUR_COURSE_ID
```

### 4. Test Mock Evaluation
```bash
curl -X POST "http://127.0.0.1:8000/test/evaluate-mock?course_id=COURSE_ID&assignment_id=ASSIGNMENT_ID&user_id=USER_ID&submission_id=SUBMISSION_ID"
```

Check Canvas to see if the test comment was posted!

## 📋 How It Works

```
System Startup
    ↓
FastAPI Server Starts (Port 8000)
    ↓
Watcher Auto-Starts (Background Thread)
    ↓
Every 30 seconds:
  → Scan all active courses
  → Check all assignments
  → Look for new submissions
    ↓
New Submission Detected
    ↓
  → Extract metadata (student_id, submission_id, attempt, timestamp)
  → Download submission file
  → AI evaluation (GPT-4)
  → Generate structured feedback
  → Post comment to Canvas: [Attempt #N] + feedback
  → Mark as processed
    ↓
Continue monitoring...
```

## 📝 Configuration

### Required Environment Variables

Create a `.env` file with:

```bash
CANVAS_BASE_URL=https://canvas.instructure.com
CANVAS_TOKEN=your_canvas_api_token_here
OPENAI_API_KEY=your_openai_api_key_here
POLICY_TEXT=Your evaluation policy text here
```

### Optional Configuration

- **Check Interval**: Edit `app/watcher.py`, change `SubmissionWatcher(check_interval=30)`
- **Port**: Edit `start_watcher.sh`, change `--port 8000`

## 📂 Project Structure

```
FairMark/
├── app/
│   ├── main.py              # FastAPI application with all endpoints
│   ├── watcher.py           # Continuous watcher service
│   ├── canvas_client.py     # Canvas API client
│   ├── llm_client.py        # OpenAI integration
│   ├── models.py            # Pydantic models
│   ├── resolver.py          # Submission resolver
│   ├── policy.py            # Policy and late submission logic
│   ├── prompt_builder.py    # Evaluation prompt builder
│   ├── file_parser.py       # File parsing utilities
│   ├── file_utils.py        # File download utilities
│   └── config.py            # Configuration
├── start_watcher.sh         # Startup script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── README_V2.md            # Complete documentation
├── QUICKSTART_V2.md        # Quick start guide
└── COMMANDS.md             # Command reference
```

## 🎓 Canvas Comment Format

Each evaluation posts a comment with:

```
[Attempt #N]

Overall evaluation (short):
Brief summary of the submission...

Rubric breakdown:
Criterion 1 — X/Y points
Comment: Detailed feedback...

Criterion 2 — X/Y points
Comment: Detailed feedback...

Possible Final Grade: X/Y

Note: [Any additional notes]
```

## 🔧 Requirements

- Python 3.9+
- Canvas API token with submission and comment permissions
- OpenAI API key
- FastAPI and dependencies (see requirements.txt)

## 📚 Documentation

- **README_V2.md** - Complete system documentation
- **QUICKSTART_V2.md** - Quick start guide with examples
- **COMMANDS.md** - All available commands
- **API Docs** - http://127.0.0.1:8000/docs (when running)

## 🎯 Key Advantages

### V2.0 vs V1.0

| Feature | V1.0 | V2.0 |
|---------|------|------|
| Assignment Config | Manual JSON | Fully Automatic |
| Discovery | Static List | Dynamic Scanning |
| Startup | Multiple Scripts | Single Command |
| Watcher | External Script | Built into FastAPI |
| Check Interval | 5 minutes | 30 seconds |
| Multiple Attempts | Basic | Full Tracking |
| Testing | Manual | Built-in API |
| Logging | Mixed | Structured |

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Restart
./start_watcher.sh
```

### Watcher Not Detecting
- Check Canvas API token permissions
- Verify environment variables in `.env`
- Test endpoints in http://127.0.0.1:8000/docs

### Comments Not Posting
- Test with `/test/evaluate-mock` endpoint
- Check Canvas API token has comment permissions
- Verify user_id is correct

## 📞 Support

For issues or questions:
1. Check the logs in your terminal
2. Test endpoints at http://127.0.0.1:8000/docs
3. Review README_V2.md for detailed documentation

## 📄 License

This project is for educational purposes.

## 🎉 Status

**FULLY OPERATIONAL** - System is production-ready and monitoring submissions 24/7!

---

**Start monitoring now:** `./start_watcher.sh`
# FairMark
