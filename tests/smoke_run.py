#!/usr/bin/env python3
print('SMOKE TEST START')
import os
import sys
import pathlib
import tempfile
import json

# Ensure project root is on sys.path so `app` package can be imported when running this script directly
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# load env from project .env BEFORE importing app so module-level config reads it
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)

from app import main
from app.models import RunRequest

# Monkeypatch resolver to return a fake context
def fake_resolver(canvas, submission_id, course_id=None, assignment_id=None):
    return {
        'course_id': str(course_id or 1),
        'assignment_id': str(assignment_id or 1),
        'user_id': str(42),
        'submission': {
            'id': int(submission_id),
            'submitted_at': None,
            'attachments': [
                {
                    'url': 'file://local-fake',
                    'filename': 'submission.txt',
                }
            ]
        }
    }

# Monkeypatch download_file to create a temp file and return its path
def fake_download_file(url, headers):
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(b"This is a fake submission file.\n")
    tf.flush()
    tf.close()
    return tf.name, os.path.basename(tf.name)

# Dummy CanvasClient to avoid network calls
class DummyCanvas:
    def __init__(self):
        self.headers = {}
    def get_assignment(self, course_id, assignment_id):
        return {
            'due_at': None,
            'rubric': [],
            'name': 'Test Assignment',
            'points_possible': 100,
            'description': 'Test description',
        }
    def post_submission_comment(self, course_id, assignment_id, user_id, comment_text):
        print('post_submission_comment called with:', course_id, assignment_id, user_id)

# Monkeypatch generate_comment to return a simple string
def fake_generate_comment(policy_path, slides_path, submission_path, prompt_text):
    return 'SMOKE TEST COMMENT' + ('\n' + prompt_text[:200] if prompt_text else '')

# Apply monkeypatchs into the main module
main.resolve_context_from_submission_id = fake_resolver
main.download_file = fake_download_file
main.CanvasClient = DummyCanvas
import app.llm_client as llm_module
llm_module.generate_comment = fake_generate_comment
main.generate_comment = fake_generate_comment

# Run
req = RunRequest(submission_id=1, course_id=1, assignment_id=1)
resp = main.run(req)
print('\nRun response:')
print(json.dumps(resp.model_dump(), indent=2, default=str))
