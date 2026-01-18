from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class RunRequest(BaseModel):
    submission_id: int = Field(..., description="Canvas submission_id")
    course_id: Optional[int] = Field(None, description="Optional but recommended for faster lookup")
    assignment_id: Optional[int] = Field(None, description="Optional but recommended for faster lookup")
    user_id: Optional[int] = Field(None, description="Optional: student's user_id (if not provided, uses current user)")
    week_slides_url: Optional[str] = Field(None, description="Optional: direct download URL for week slides PDF")
    policy_text_override: Optional[str] = Field(None, description="Optional: policy text to use for this run")

class RunResponse(BaseModel):
    resolved: Dict[str, Any]
    comment_preview: str
    posted: bool
