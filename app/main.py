import os
import asyncio
import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .models import RunRequest, RunResponse
from .canvas_client import CanvasClient
from .resolver import resolve_context_from_submission_id
from .file_utils import download_file
from .policy import parse_canvas_datetime, compute_late
from .prompt_builder import build_prompt
from .llm_client import generate_comment
from .config import CANVAS_BASE_URL, CANVAS_TOKEN, POLICY_TEXT, POLICY_FILE_PATH
from .watcher import get_watcher, SubmissionWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global watcher thread
watcher_thread: Optional[threading.Thread] = None


def run_watcher_in_thread():
    """Run watcher in a separate thread with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    watcher = get_watcher()
    try:
        loop.run_until_complete(watcher.run())
    except Exception as e:
        logger.error(f"Watcher error: {e}")
    finally:
        loop.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - starts watcher on startup, stops on shutdown
    """
    global watcher_thread

    logger.info("=" * 70)
    logger.info("🚀 FairMark System Starting...")
    logger.info("=" * 70)

    # Start the watcher service in a separate thread
    try:
        watcher = get_watcher()
        watcher_thread = threading.Thread(target=run_watcher_in_thread, daemon=True)
        watcher_thread.start()

        logger.info("✅ Watcher service started in background thread")
        logger.info("🔄 Now monitoring ALL courses and assignments 24/7")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ Error starting watcher: {e}")
        import traceback
        traceback.print_exc()

    yield

    # Shutdown: stop the watcher
    logger.info("=" * 70)
    logger.info("🛑 FairMark System Shutting Down...")
    logger.info("=" * 70)

    if watcher_thread:
        try:
            watcher.stop()
            # Give thread time to finish
            watcher_thread.join(timeout=5)
        except Exception as e:
            logger.error(f"Error stopping watcher: {e}")

    logger.info("✅ Watcher service stopped")
    logger.info("=" * 70)


# Create FastAPI app with lifespan
app = FastAPI(
    title="FairMark - Automated Education Evaluation System",
    version="2.0.0",
    description="Always-running watcher service for Canvas LMS submissions",
    lifespan=lifespan
)


# ==================== Models ====================

class EvaluateRequest(BaseModel):
    """Request model for evaluation endpoint"""
    submission_id: int = Field(..., description="Canvas submission ID")
    course_id: int = Field(..., description="Canvas course ID")
    assignment_id: int = Field(..., description="Canvas assignment ID")
    user_id: int = Field(..., description="Student user ID")
    attempt: int = Field(default=1, description="Submission attempt number")
    submitted_at: str = Field(..., description="Submission timestamp")


class WatcherStatusResponse(BaseModel):
    """Watcher status response"""
    is_running: bool
    check_interval: int
    total_submissions_tracked: int
    active_courses: int
    active_assignments: int


class SubmissionTestResponse(BaseModel):
    """Test endpoint response"""
    success: bool
    message: str
    data: Optional[Dict] = None


# ==================== Health & Status Endpoints ====================

@app.get("/health")
def health():
    """Health check endpoint"""
    logger.info("🏥 Health check requested")
    return {
        "ok": True,
        "service": "FairMark Automated Evaluation System",
        "version": "2.0.0",
        "canvas_base_url_set": bool(CANVAS_BASE_URL),
        "canvas_token_set": bool(CANVAS_TOKEN),
        "policy_text_set": bool(POLICY_TEXT),
        "policy_file_set": bool(POLICY_FILE_PATH and os.path.exists(POLICY_FILE_PATH)),
        "watcher_running": watcher_thread is not None and watcher_thread.is_alive(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/watcher/status", response_model=WatcherStatusResponse)
def get_watcher_status():
    """Get current watcher service status"""
    logger.info("📊 Watcher status requested")

    watcher = get_watcher()

    return WatcherStatusResponse(
        is_running=watcher.is_running,
        check_interval=watcher.check_interval,
        total_submissions_tracked=sum(len(attempts) for attempts in watcher.processed_submissions.values()),
        active_courses=0,  # Will be calculated dynamically
        active_assignments=0  # Will be calculated dynamically
    )


@app.get("/watcher/submissions")
def get_tracked_submissions():
    """Get all tracked submissions"""
    logger.info("📋 Tracked submissions requested")

    watcher = get_watcher()

    submissions_list = []
    for key, attempts in watcher.processed_submissions.items():
        parts = key.split("_")
        if len(parts) == 3:
            submissions_list.append({
                "course_id": int(parts[0]),
                "assignment_id": int(parts[1]),
                "user_id": int(parts[2]),
                "attempts": sorted(list(attempts))
            })

    return {
        "total_tracked": len(submissions_list),
        "submissions": submissions_list
    }


# ==================== Core Evaluation Endpoint ====================

@app.post("/evaluate", response_model=RunResponse)
async def evaluate_submission(req: EvaluateRequest):
    """
    Main evaluation endpoint - called by watcher for each new submission
    """
    logger.info("=" * 70)
    logger.info(f"📝 EVALUATION REQUEST RECEIVED")
    logger.info(f"   Submission ID: {req.submission_id}")
    logger.info(f"   Course ID: {req.course_id}")
    logger.info(f"   Assignment ID: {req.assignment_id}")
    logger.info(f"   User ID: {req.user_id}")
    logger.info(f"   Attempt: {req.attempt}")
    logger.info(f"   Submitted At: {req.submitted_at}")
    logger.info("=" * 70)

    if not CANVAS_BASE_URL or not CANVAS_TOKEN:
        raise HTTPException(status_code=500, detail="Canvas credentials not configured")

    canvas = CanvasClient()

    try:
        # Get submission details
        logger.info(f"🔍 Fetching submission details...")
        submission = canvas.get_submission_for_user(
            req.course_id,
            req.assignment_id,
            str(req.user_id)
        )

        logger.info(f"✅ Submission fetched: ID {submission.get('id')}")

        # Get assignment details
        logger.info(f"🔍 Fetching assignment details...")
        assignment = canvas.get_assignment(req.course_id, req.assignment_id)
        logger.info(f"✅ Assignment fetched: {assignment.get('name')}")

        # Extract rubric
        rubric_items = []
        rubric = assignment.get("rubric")
        if isinstance(rubric, list):
            for r in rubric:
                rubric_items.append({
                    "name": r.get("description") or r.get("criterion") or "Criterion",
                    "points": r.get("points", None),
                })
            logger.info(f"📊 Found {len(rubric_items)} rubric items")

        # Calculate late submission
        due_at = parse_canvas_datetime(assignment.get("due_at"))
        submitted_at = parse_canvas_datetime(submission.get("submitted_at"))
        late = compute_late(due_at, submitted_at)

        if late.is_late:
            logger.info(f"⏰ Submission is LATE by {late.late_minutes} minutes")
        else:
            logger.info(f"✅ Submission is ON TIME")

        # Get attachments
        attachments = submission.get("attachments") or []
        if not attachments:
            logger.error("❌ No attachments found")
            raise HTTPException(status_code=400, detail="No submission attachment found")

        att = attachments[0]
        att_url = att.get("url")
        att_name = att.get("filename") or att.get("display_name") or "submission"
        logger.info(f"📎 Processing attachment: {att_name}")

        if not att_url:
            raise HTTPException(status_code=400, detail="Attachment URL missing")

        # Download submission file
        logger.info(f"⬇️  Downloading submission file...")
        submission_tmp, submission_filename = download_file(att_url, canvas.headers)
        logger.info(f"✅ File downloaded: {submission_filename}")

        # Prepare evaluation packet
        policy_text = (POLICY_TEXT or "").strip()
        policy_path = POLICY_FILE_PATH if POLICY_FILE_PATH and os.path.exists(POLICY_FILE_PATH) else None

        packet = {
            "submission_meta": {
                "submission_id": int(submission.get("id")),
                "attempt": req.attempt,
                "submitted_at": req.submitted_at,
                "due_at": assignment.get("due_at"),
                "late": late.is_late,
                "late_minutes": late.late_minutes,
                "grace_applied": late.grace_applied,
                "penalty_percent": late.penalty_percent,
            },
            "course": {"course_id": req.course_id},
            "assignment": {
                "assignment_id": req.assignment_id,
                "title": assignment.get("name"),
                "points_possible": assignment.get("points_possible"),
                "instructions_html": assignment.get("description"),
            },
            "rubric": rubric_items or None,
            "policy_text": policy_text or None,
            "week_slides_included": False,
            "submission_attachment": {"filename": att_name, "downloaded_as": submission_filename},
        }

        # Build prompt
        logger.info(f"📝 Building evaluation prompt...")
        prompt = build_prompt(packet)

        # Generate comment using LLM
        logger.info(f"🤖 Generating AI evaluation comment...")
        logger.info(f"   This may take 30-60 seconds...")

        comment = generate_comment(
            policy_path=policy_path,
            slides_path=None,
            submission_path=submission_tmp,
            prompt_text=prompt,
        )

        logger.info(f"✅ Comment generated ({len(comment)} chars)")

        # Get current UTC time for timestamp
        from datetime import datetime, timezone
        evaluation_time = datetime.now(timezone.utc)
        utc_timestamp = evaluation_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        # Post comment to Canvas with metadata
        # Canvas will automatically show this in user's local timezone
        comment_with_metadata = f"""[Attempt #{req.attempt}]
Evaluated at: {utc_timestamp}

{comment}

---
💡 Note: This evaluation was generated automatically by FairMark AI.
The timestamp shown is in UTC. Your browser will display it in your local timezone.
"""

        logger.info(f"📤 Posting comment to Canvas...")
        logger.info(f"   Timestamp: {utc_timestamp}")
        canvas.post_submission_comment(
            req.course_id,
            req.assignment_id,
            str(req.user_id),
            comment_with_metadata
        )
        logger.info(f"✅ Comment posted successfully to Canvas!")

        # Cleanup
        if submission_tmp and os.path.exists(submission_tmp):
            os.remove(submission_tmp)
            logger.info(f"🗑️  Temporary files cleaned up")

        logger.info("=" * 70)
        logger.info("✅ EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)

        return RunResponse(
            resolved={
                "course_id": req.course_id,
                "assignment_id": req.assignment_id,
                "user_id": req.user_id,
                "submission_id": req.submission_id,
                "attempt": req.attempt,
                "rubric_found": bool(rubric_items),
                "slides_included": False,
                "late": late.is_late,
                "penalty_percent": late.penalty_percent,
            },
            comment_preview=comment[:500],
            posted=True,
        )

    except Exception as e:
        logger.error(f"❌ EVALUATION FAILED: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Legacy /run endpoint for backward compatibility ====================

@app.post("/run", response_model=RunResponse)
def run(req: RunRequest):
    """Legacy run endpoint - for backward compatibility"""
    logger.info("📝 Legacy /run endpoint called")

    if not CANVAS_BASE_URL or not CANVAS_TOKEN:
        raise HTTPException(status_code=500, detail="Set CANVAS_BASE_URL and CANVAS_TOKEN.")

    canvas = CanvasClient()

    ctx = resolve_context_from_submission_id(
        canvas=canvas,
        submission_id=req.submission_id,
        course_id=req.course_id,
        assignment_id=req.assignment_id,
        user_id=req.user_id,
    )

    course_id = int(ctx["course_id"])
    assignment_id = int(ctx["assignment_id"])
    user_id = str(ctx["user_id"])
    submission = ctx["submission"]

    assignment = canvas.get_assignment(course_id, assignment_id)

    # rubric extraction (best effort)
    rubric_items = []
    rubric = assignment.get("rubric")
    if isinstance(rubric, list):
        for r in rubric:
            rubric_items.append({
                "name": r.get("description") or r.get("criterion") or "Criterion",
                "points": r.get("points", None),
            })

    due_at = parse_canvas_datetime(assignment.get("due_at"))
    submitted_at = parse_canvas_datetime(submission.get("submitted_at"))
    late = compute_late(due_at, submitted_at)

    attachments = submission.get("attachments") or []
    if not attachments:
        raise HTTPException(status_code=400, detail="No submission attachment found (expected file upload).")

    att = attachments[0]
    att_url = att.get("url")
    att_name = att.get("filename") or att.get("display_name") or "submission"

    if not att_url:
        raise HTTPException(status_code=400, detail="Attachment URL missing.")

    submission_tmp, submission_filename = download_file(att_url, canvas.headers)

    slides_tmp = None
    if req.week_slides_url:
        slides_tmp, _ = download_file(req.week_slides_url, canvas.headers)

    policy_text = (req.policy_text_override or POLICY_TEXT or "").strip()
    policy_path = POLICY_FILE_PATH if POLICY_FILE_PATH and os.path.exists(POLICY_FILE_PATH) else None

    packet = {
        "submission_meta": {
            "submission_id": int(submission.get("id")),
            "submitted_at": submission.get("submitted_at"),
            "due_at": assignment.get("due_at"),
            "late": late.is_late,
            "late_minutes": late.late_minutes,
            "grace_applied": late.grace_applied,
            "penalty_percent": late.penalty_percent,
        },
        "course": {"course_id": course_id},
        "assignment": {
            "assignment_id": assignment_id,
            "title": assignment.get("name"),
            "points_possible": assignment.get("points_possible"),
            "instructions_html": assignment.get("description"),
        },
        "rubric": rubric_items or None,
        "policy_text": policy_text or None,
        "week_slides_included": bool(slides_tmp),
        "submission_attachment": {"filename": att_name, "downloaded_as": submission_filename},
    }

    prompt = build_prompt(packet)

    try:
        logger.info(f"[INFO] Generating comment for submission {req.submission_id}")
        comment = generate_comment(
            policy_path=policy_path,
            slides_path=slides_tmp,
            submission_path=submission_tmp,
            prompt_text=prompt,
        )
        logger.info(f"[INFO] Comment generated successfully ({len(comment)} chars)")

        logger.info(f"[INFO] Posting comment to Canvas for user {user_id}")
        canvas.post_submission_comment(course_id, assignment_id, user_id, comment)
        logger.info(f"[SUCCESS] Comment posted successfully!")

        return RunResponse(
            resolved={
                "course_id": course_id,
                "assignment_id": assignment_id,
                "user_id": user_id,
                "submission_id": req.submission_id,
                "rubric_found": bool(rubric_items),
                "slides_included": bool(slides_tmp),
                "late": late.is_late,
                "penalty_percent": late.penalty_percent,
            },
            comment_preview=comment[:2000],
            posted=True,
        )
    except Exception as e:
        logger.error(f"[ERROR] Failed to process submission: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        for p in [submission_tmp, slides_tmp]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


# ==================== Testing & Debugging Endpoints ====================

@app.get("/test/courses")
def test_list_courses():
    """Test endpoint: List all active courses"""
    logger.info("🧪 TEST: Listing all courses")

    try:
        canvas = CanvasClient()
        courses = canvas.list_courses(per_page=100)

        logger.info(f"✅ Found {len(courses)} courses")

        return {
            "success": True,
            "count": len(courses),
            "courses": [
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "course_code": c.get("course_code")
                }
                for c in courses
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/test/assignments/{course_id}")
def test_list_assignments(course_id: int):
    """Test endpoint: List all assignments for a course"""
    logger.info(f"🧪 TEST: Listing assignments for course {course_id}")

    try:
        canvas = CanvasClient()
        assignments = canvas.list_assignments(course_id, per_page=100)

        logger.info(f"✅ Found {len(assignments)} assignments")

        return {
            "success": True,
            "course_id": course_id,
            "count": len(assignments),
            "assignments": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "due_at": a.get("due_at"),
                    "points_possible": a.get("points_possible")
                }
                for a in assignments
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/test/submissions/{course_id}/{assignment_id}")
def test_list_submissions(course_id: int, assignment_id: int):
    """Test endpoint: List all submissions for an assignment"""
    logger.info(f"🧪 TEST: Listing submissions for assignment {assignment_id}")

    try:
        import requests

        url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
        headers = {
            "Authorization": f"Bearer {CANVAS_TOKEN}",
            "Accept": "application/json"
        }

        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 100, "include[]": "submission_history"},
            timeout=30
        )
        response.raise_for_status()
        submissions = response.json()

        logger.info(f"✅ Found {len(submissions)} submissions")

        return {
            "success": True,
            "course_id": course_id,
            "assignment_id": assignment_id,
            "count": len(submissions),
            "submissions": [
                {
                    "id": s.get("id"),
                    "user_id": s.get("user_id"),
                    "workflow_state": s.get("workflow_state"),
                    "submitted_at": s.get("submitted_at"),
                    "attempt": s.get("attempt"),
                    "has_attachments": len(s.get("attachments", [])) > 0
                }
                for s in submissions
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/test/evaluate-mock")
def test_evaluate_mock(
    course_id: int,
    assignment_id: int,
    user_id: int,
    submission_id: int
):
    """Test endpoint: Trigger evaluation without AI (mock)"""
    logger.info(f"🧪 TEST: Mock evaluation")
    logger.info(f"   Course: {course_id}, Assignment: {assignment_id}")
    logger.info(f"   User: {user_id}, Submission: {submission_id}")

    try:
        canvas = CanvasClient()

        # Fetch submission
        submission = canvas.get_submission_for_user(course_id, assignment_id, str(user_id))

        # Post a mock comment
        mock_comment = f"""[TEST EVALUATION - Mock Mode]

Submission ID: {submission_id}
User ID: {user_id}
Attempt: {submission.get('attempt', 1)}
Submitted At: {submission.get('submitted_at')}

This is a TEST comment to verify the system is working.
No actual AI evaluation was performed.

Generated at: {datetime.now().isoformat()}
"""

        canvas.post_submission_comment(course_id, assignment_id, str(user_id), mock_comment)

        logger.info("✅ Mock comment posted successfully")

        return {
            "success": True,
            "message": "Mock evaluation completed",
            "data": {
                "submission_id": submission_id,
                "user_id": user_id,
                "comment_posted": True
            }
        }
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


@app.get("/")
def root():
    """Root endpoint with system information"""
    return {
        "service": "FairMark - Automated Education Evaluation System",
        "version": "2.0.0",
        "status": "running",
        "watcher_active": watcher_thread is not None and watcher_thread.is_alive(),
        "endpoints": {
            "health": "/health",
            "watcher_status": "/watcher/status",
            "tracked_submissions": "/watcher/submissions",
            "evaluate": "/evaluate (POST)",
            "test_courses": "/test/courses",
            "test_assignments": "/test/assignments/{course_id}",
            "test_submissions": "/test/submissions/{course_id}/{assignment_id}",
            "test_mock_eval": "/test/evaluate-mock (POST)",
            "docs": "/docs"
        },
        "description": "Always-running watcher monitoring ALL Canvas submissions 24/7"
    }
