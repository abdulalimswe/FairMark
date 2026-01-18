#!/bin/bash
# =============================================================================
# FAIRMARK V2.0 - AUTOMATED WATCHER SERVICE
# =============================================================================
# Starts the always-running watcher that monitors ALL Canvas submissions 24/7
# =============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          FAIRMARK V2.0 - AUTOMATED EVALUATION SYSTEM           ║"
echo "║              Always-Running Watcher Service                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this from the FairMark directory"
    exit 1
fi

# Load environment variables
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please make sure .env exists with your API keys"
    exit 1
fi

echo "✅ Loading configuration from .env..."
set -a
source .env
set +a

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Stop any existing instances
echo "🔄 Stopping any existing FairMark processes..."
pkill -f "uvicorn app.main" 2>/dev/null

# Kill any process using port 8000
PORT_PIDS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PORT_PIDS" ]; then
    echo "🔧 Freeing port 8000..."
    kill -9 $PORT_PIDS 2>/dev/null
fi
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  STARTING FAIRMARK SYSTEM                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Features:"
echo "   ✅ Automatic watcher monitors ALL courses & assignments"
echo "   ✅ No manual assignment configuration needed"
echo "   ✅ Instant detection of new submissions (30-second checks)"
echo "   ✅ Multiple submission attempts supported"
echo "   ✅ AI-powered evaluation with structured feedback"
echo "   ✅ Comments automatically posted to Canvas"
echo ""
echo "📊 API Endpoints Available:"
echo "   • Health Check:        http://127.0.0.1:8000/health"
echo "   • Watcher Status:      http://127.0.0.1:8000/watcher/status"
echo "   • Tracked Submissions: http://127.0.0.1:8000/watcher/submissions"
echo "   • API Documentation:   http://127.0.0.1:8000/docs"
echo ""
echo "🧪 Testing Endpoints:"
echo "   • List Courses:        http://127.0.0.1:8000/test/courses"
echo "   • List Assignments:    http://127.0.0.1:8000/test/assignments/{course_id}"
echo "   • List Submissions:    http://127.0.0.1:8000/test/submissions/{course_id}/{assignment_id}"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Start the server (watcher starts automatically on startup)
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
