from typing import Any, Dict, List

import requests
from .config import CANVAS_BASE_URL, CANVAS_TOKEN, REQUEST_TIMEOUT

class CanvasClient:
    def __init__(self):
        if not CANVAS_BASE_URL or not CANVAS_TOKEN:
            raise RuntimeError("Set CANVAS_BASE_URL and CANVAS_TOKEN.")
        self.base = CANVAS_BASE_URL.rstrip("/")
        self.h = {
            "Authorization": f"Bearer {CANVAS_TOKEN}",
            "Accept": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base}{path}"

    def get_self(self) -> Dict[str, Any]:
        r = requests.get(self._url("/api/v1/users/self/profile"), headers=self.h, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def list_courses(self, per_page: int = 20) -> List[Dict[str, Any]]:
        r = requests.get(
            self._url("/api/v1/courses"),
            headers=self.h,
            params={"per_page": per_page},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def list_assignments(self, course_id: int, per_page: int = 50) -> List[Dict[str, Any]]:
        r = requests.get(
            self._url(f"/api/v1/courses/{course_id}/assignments"),
            headers=self.h,
            params={"per_page": per_page},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def get_assignment(self, course_id: int, assignment_id: int) -> Dict[str, Any]:
        params = {"include[]": ["rubric", "all_dates", "assignment_visibility"]}
        r = requests.get(
            self._url(f"/api/v1/courses/{course_id}/assignments/{assignment_id}"),
            headers=self.h,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def get_submission_for_user(self, course_id: int, assignment_id: int, user_id: str) -> Dict[str, Any]:
        params = {"include[]": ["submission_history", "rubric_assessment", "submission_comments"]}
        r = requests.get(
            self._url(f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"),
            headers=self.h,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def post_submission_comment(self, course_id: int, assignment_id: int, user_id: str, comment_text: str) -> None:
        url = self._url(f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}")
        data = {"comment": {"text_comment": comment_text}}

        print(f"[DEBUG] Posting comment to Canvas:")
        print(f"  URL: {url}")
        print(f"  User ID: {user_id}")
        print(f"  Comment length: {len(comment_text)} chars")

        try:
            r = requests.put(
                url,
                headers=self.h,
                json=data,
                timeout=REQUEST_TIMEOUT,
            )
            print(f"[DEBUG] Response status: {r.status_code}")

            if r.status_code >= 400:
                print(f"[ERROR] Canvas API error response: {r.text}")

            r.raise_for_status()
            print("[SUCCESS] Comment posted successfully to Canvas")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to post comment: {e}")
            if hasattr(e.response, 'text'):
                print(f"[ERROR] Response body: {e.response.text}")
            raise

    @property
    def headers(self) -> Dict[str, str]:
        return dict(self.h)
