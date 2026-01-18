#!/usr/bin/env python3
"""
FairMark Continuous Watcher Service
Always-running service that monitors ALL Canvas submissions in real-time
"""
import asyncio
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Tuple
import requests
from .canvas_client import CanvasClient
from .config import CANVAS_BASE_URL, CANVAS_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SubmissionWatcher:
    """
    Continuous watcher that monitors all Canvas submissions across all courses
    """

    def __init__(self, check_interval: int = 30):
        """
        Initialize watcher

        Args:
            check_interval: Seconds between checks (default 30s for near-instant detection)
        """
        self.check_interval = check_interval
        self.canvas = CanvasClient()
        # Track file hashes: {assignment_key: {(attempt, file_hash)}}
        self.processed_submissions: Dict[str, Set[Tuple[int, str]]] = {}
        self.api_base = "http://127.0.0.1:8000"
        self.is_running = False

        logger.info("=" * 70)
        logger.info("FairMark Continuous Watcher Service Initialized")
        logger.info("=" * 70)
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info(f"API endpoint: {self.api_base}")
        logger.info(f"File change detection: ENABLED")
        logger.info("=" * 70)

    def get_all_active_courses(self) -> List[Dict]:
        """Fetch all active courses for the current user"""
        try:
            url = f"{CANVAS_BASE_URL}/api/v1/courses"
            headers = {
                "Authorization": f"Bearer {CANVAS_TOKEN}",
                "Accept": "application/json"
            }

            response = requests.get(
                url,
                headers=headers,
                params={
                    "enrollment_state": "active",
                    "per_page": 100
                },
                timeout=30
            )
            response.raise_for_status()
            courses = response.json()

            logger.info(f"📚 Found {len(courses)} active courses")
            return courses

        except Exception as e:
            logger.error(f"❌ Error fetching courses: {e}")
            return []

    def get_all_assignments_for_course(self, course_id: int) -> List[Dict]:
        """Fetch all assignments for a course"""
        try:
            url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments"
            headers = {
                "Authorization": f"Bearer {CANVAS_TOKEN}",
                "Accept": "application/json"
            }

            response = requests.get(
                url,
                headers=headers,
                params={"per_page": 100},
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Error fetching assignments for course {course_id}: {e}")
            return []

    def get_all_submissions_for_assignment(
        self,
        course_id: int,
        assignment_id: int
    ) -> List[Dict]:
        """Fetch all submissions for an assignment"""
        try:
            url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
            headers = {
                "Authorization": f"Bearer {CANVAS_TOKEN}",
                "Accept": "application/json"
            }

            response = requests.get(
                url,
                headers=headers,
                params={
                    "include[]": ["submission_history"],
                    "per_page": 100
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Error fetching submissions for assignment {assignment_id}: {e}")
            return []

    def get_submission_key(self, course_id: int, assignment_id: int, user_id: int) -> str:
        """Generate unique key for tracking submissions"""
        return f"{course_id}_{assignment_id}_{user_id}"

    def get_file_hash(self, file_url: str) -> Optional[str]:
        """
        Compute MD5 hash of file content to detect changes

        Args:
            file_url: URL of the file to download and hash

        Returns:
            MD5 hash string or None if error
        """
        try:
            headers = {
                "Authorization": f"Bearer {CANVAS_TOKEN}",
            }
            response = requests.get(file_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Compute MD5 hash of file content
            file_hash = hashlib.md5(response.content).hexdigest()
            return file_hash

        except Exception as e:
            logger.error(f"❌ Error computing file hash: {e}")
            return None

    def is_submission_new(
        self,
        course_id: int,
        assignment_id: int,
        user_id: int,
        attempt: int,
        file_hash: str
    ) -> bool:
        """
        Check if this submission has been processed

        Returns True if:
        - Never seen this submission before, OR
        - Same attempt but file content changed (re-upload)
        """
        key = self.get_submission_key(course_id, assignment_id, user_id)

        if key not in self.processed_submissions:
            self.processed_submissions[key] = set()

        # Check if we've seen this exact combination of attempt + file hash
        submission_signature = (attempt, file_hash)
        return submission_signature not in self.processed_submissions[key]

    def mark_submission_processed(
        self,
        course_id: int,
        assignment_id: int,
        user_id: int,
        attempt: int,
        file_hash: str
    ):
        """Mark a submission as processed with its file hash"""
        key = self.get_submission_key(course_id, assignment_id, user_id)

        if key not in self.processed_submissions:
            self.processed_submissions[key] = set()

        submission_signature = (attempt, file_hash)
        self.processed_submissions[key].add(submission_signature)

    async def evaluate_submission(
        self,
        submission_id: int,
        course_id: int,
        assignment_id: int,
        user_id: int,
        attempt: int,
        submitted_at: str
    ):
        """Send submission to evaluation API"""
        try:
            logger.info(f"🤖 Evaluating submission {submission_id}")
            logger.info(f"   📋 Assignment: {assignment_id}")
            logger.info(f"   👤 User: {user_id}")
            logger.info(f"   🔢 Attempt: {attempt}")
            logger.info(f"   📅 Submitted: {submitted_at}")

            response = requests.post(
                f"{self.api_base}/evaluate",
                json={
                    "submission_id": submission_id,
                    "course_id": course_id,
                    "assignment_id": assignment_id,
                    "user_id": user_id,
                    "attempt": attempt,
                    "submitted_at": submitted_at
                },
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"   ✅ Evaluation complete!")
                logger.info(f"   💬 Comment posted: {result.get('posted', False)}")
                logger.info(f"   📝 Preview: {result.get('comment_preview', '')[:80]}...")
                return result
            else:
                logger.error(f"   ❌ Evaluation failed: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error evaluating submission: {e}")
            return None

    async def process_submission(
        self,
        submission: Dict,
        course_id: int,
        assignment_id: int,
        assignment_name: str
    ):
        """Process a single submission"""
        user_id = submission.get("user_id")
        submission_id = submission.get("id")
        workflow_state = submission.get("workflow_state")
        attempt = submission.get("attempt", 1)
        submitted_at = submission.get("submitted_at")

        # Only process submitted submissions with attachments
        if workflow_state != "submitted":
            return

        attachments = submission.get("attachments")
        if not attachments:
            return

        if not submitted_at:
            return

        # Get file hash to detect if file content changed
        first_attachment = attachments[0]
        file_url = first_attachment.get("url")

        if not file_url:
            logger.warning(f"   ⚠️  No file URL found for submission {submission_id}")
            return

        logger.info(f"   🔍 Computing file hash for change detection...")
        file_hash = self.get_file_hash(file_url)

        if not file_hash:
            logger.warning(f"   ⚠️  Could not compute file hash, skipping")
            return

        # Check if this submission (attempt + file hash) is new
        if not self.is_submission_new(course_id, assignment_id, user_id, attempt, file_hash):
            return

        logger.info("")
        logger.info("🆕 NEW/UPDATED SUBMISSION DETECTED!")
        logger.info(f"   📚 Course: {course_id}")
        logger.info(f"   📋 Assignment: {assignment_name} (ID: {assignment_id})")
        logger.info(f"   👤 Student: {user_id}")
        logger.info(f"   📄 Submission ID: {submission_id}")
        logger.info(f"   🔢 Attempt: {attempt}")
        logger.info(f"   🔐 File Hash: {file_hash[:8]}...")
        logger.info(f"   ⏰ Submitted: {submitted_at}")
        logger.info(f"   📎 Attachments: {len(attachments)}")

        # Evaluate the submission
        result = await self.evaluate_submission(
            submission_id,
            course_id,
            assignment_id,
            user_id,
            attempt,
            submitted_at
        )

        if result:
            # Mark as processed with file hash
            self.mark_submission_processed(course_id, assignment_id, user_id, attempt, file_hash)
            logger.info(f"   ✅ Submission processed successfully!")
        else:
            logger.error(f"   ❌ Failed to process submission")

        logger.info("")

    async def scan_all_submissions(self):
        """Scan all courses, assignments, and submissions"""
        try:
            logger.info("🔍 Scanning all courses for new submissions...")

            # Get all active courses
            courses = self.get_all_active_courses()

            total_assignments = 0
            total_new_submissions = 0

            for course in courses:
                course_id = course.get("id")
                course_name = course.get("name", "Unknown")

                # Get all assignments for this course
                assignments = self.get_all_assignments_for_course(course_id)
                total_assignments += len(assignments)

                if assignments:
                    logger.info(f"📚 Course: {course_name} ({len(assignments)} assignments)")

                for assignment in assignments:
                    assignment_id = assignment.get("id")
                    assignment_name = assignment.get("name", "Unknown")

                    # Get all submissions for this assignment
                    submissions = self.get_all_submissions_for_assignment(course_id, assignment_id)

                    # Process each submission
                    for submission in submissions:
                        await self.process_submission(
                            submission,
                            course_id,
                            assignment_id,
                            assignment_name
                        )

            logger.info(f"✅ Scan complete. Checked {total_assignments} assignments across {len(courses)} courses")
        except Exception as e:
            logger.error(f"❌ Error during scan: {e}")
            import traceback
            traceback.print_exc()

    async def run(self):
        """Main watcher loop - runs continuously"""
        self.is_running = True

        logger.info("")
        logger.info("🚀 Starting continuous watcher service...")
        logger.info("🔄 Monitoring ALL courses and assignments dynamically")
        logger.info(f"⏱️  Checking every {self.check_interval} seconds")
        logger.info("🛑 Press Ctrl+C to stop")
        logger.info("")

        try:
            while self.is_running:
                scan_start = datetime.now()

                await self.scan_all_submissions()

                scan_duration = (datetime.now() - scan_start).total_seconds()
                logger.info(f"⏱️  Scan completed in {scan_duration:.2f} seconds")
                logger.info(f"⏳ Next scan in {self.check_interval} seconds...")
                logger.info("")

                await asyncio.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Watcher service stopped by user")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ Watcher service error: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False

    def stop(self):
        """Stop the watcher service"""
        logger.info("🛑 Stopping watcher service...")
        self.is_running = False


# Global watcher instance
_watcher_instance: Optional[SubmissionWatcher] = None


def get_watcher() -> SubmissionWatcher:
    """Get or create the global watcher instance"""
    global _watcher_instance
    if _watcher_instance is None:
        _watcher_instance = SubmissionWatcher(check_interval=30)
    return _watcher_instance
