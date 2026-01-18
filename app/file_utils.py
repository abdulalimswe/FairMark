import os
import re
import time
import tempfile
from typing import Dict, Tuple
from urllib.parse import urlparse

import requests
from .config import REQUEST_TIMEOUT

def safe_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")
    return name or f"file_{int(time.time())}"

def download_file(url: str, headers: Dict[str, str]) -> Tuple[str, str]:
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True)
    resp.raise_for_status()

    filename = None
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r'filename="?([^"]+)"?', cd)
    if m:
        filename = m.group(1)

    if not filename:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or f"download_{int(time.time())}"

    filename = safe_filename(filename)
    fd, tmp_path = tempfile.mkstemp(prefix="fairmark_", suffix="_" + filename)
    os.close(fd)

    with open(tmp_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)

    return tmp_path, filename
