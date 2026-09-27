"""
Print headers of all code blocks across Docs 5-8
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview")
DOCS = [
    "DEPLOYMENT_GUIDE.md",
    "MONITORING_OPERATIONS.md",
    "TESTING_STRATEGY.md",
    "PRODUCTION_LAUNCH_MANUAL.md"
]

for doc_name in DOCS:
    content = (ROOT / doc_name).read_text(encoding="utf-8")
    blocks = re.findall(r"```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```", content)
    print(f"\n=== {doc_name} ({len(blocks)} blocks) ===")
    for idx, (lang, body) in enumerate(blocks, 1):
        first_line = body.strip().split("\n")[0] if body.strip() else "<empty>"
        print(f"  [{idx:2d}] ({lang:10s}) {first_line[:80]}")
