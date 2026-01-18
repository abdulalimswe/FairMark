from typing import Any, Dict, Optional
import requests
from fastapi import HTTPException
from .canvas_client import CanvasClient

def resolve_context_from_submission_id(
    canvas: CanvasClient,
    submission_id: int,
    course_id: Optional[int],
    assignment_id: Optional[int],
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    if not user_id:
        try:
            current_user = canvas.get_self()
            user_id = current_user['id']
            print(f"[INFO] Using current user ID: {user_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not get current user: {str(e)}")

    # Fast path: course_id + assignment_id + user_id provided
    if course_id and assignment_id and user_id:
        try:
            print(f"[INFO] Fetching submission for user {user_id} in course {course_id}, assignment {assignment_id}")
            submission = canvas.get_submission_for_user(course_id, assignment_id, str(user_id))

            # Verify this is the correct submission
            if int(submission.get("id", -1)) == int(submission_id):
                return {
                    "course_id": course_id,
                    "assignment_id": assignment_id,
                    "user_id": str(user_id),
                    "submission": submission
                }
            else:
                print(f"[WARNING] Submission ID mismatch: expected {submission_id}, got {submission.get('id')}")
                # Still return it if it's the user's submission for this assignment
                return {
                    "course_id": course_id,
                    "assignment_id": assignment_id,
                    "user_id": str(user_id),
                    "submission": submission
                }

        except requests.exceptions.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching submission: {str(e)}")

    # Need at least course_id and assignment_id
    raise HTTPException(
        status_code=400,
        detail="Please provide both course_id and assignment_id for lookup."
    )
