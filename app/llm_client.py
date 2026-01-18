from typing import List, Optional

from fastapi import HTTPException
from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL
from .file_parser import extract_text_from_file, get_file_info

def generate_comment(
    policy_path: Optional[str],
    slides_path: Optional[str],
    submission_path: str,
    prompt_text: str,
) -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set.")

    print(f"[INFO] Initializing OpenAI client with model: {OPENAI_MODEL}")
    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        # Read file contents using proper parsers
        files_content = []

        if policy_path:
            policy_text = extract_text_from_file(policy_path)
            files_content.append(f"## Grading Policy Document\n\n{policy_text[:6000]}")

        if slides_path:
            slides_text = extract_text_from_file(slides_path)
            files_content.append(f"## Lecture Slides\n\n{slides_text[:6000]}")

        # Read submission file with proper parsing
        submission_info = get_file_info(submission_path)
        submission_text = extract_text_from_file(submission_path)

        # Add file info and content
        file_info_text = f"File: {submission_info.get('name', 'unknown')} ({submission_info.get('size_kb', 0)} KB)"
        files_content.append(f"## Student Submission\n\n{file_info_text}\n\n{submission_text[:12000]}")

        # Combine all content
        full_content = prompt_text + "\n\n" + "\n\n---\n\n".join(files_content)

        print(f"[INFO] Sending request to OpenAI API...")
        print(f"[INFO] Total content length: {len(full_content)} chars")

        # Use chat completions API
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are FairMark, an AI teaching assistant that provides detailed, constructive feedback on student submissions. "
                               "Analyze the submission thoroughly and provide specific, actionable feedback aligned with the rubric criteria."
                },
                {"role": "user", "content": full_content}
            ],
            temperature=0.7,
            max_tokens=2500
        )

        if resp.choices and len(resp.choices) > 0:
            result = resp.choices[0].message.content.strip()
            print(f"[SUCCESS] OpenAI response received ({len(result)} chars)")
            return result

        raise HTTPException(status_code=500, detail="LLM response could not be parsed.")

    except Exception as e:
        print(f"[ERROR] OpenAI API error: {type(e).__name__}: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error generating comment: {str(e)}")
