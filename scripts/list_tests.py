"""
Extract and list all test cases from TESTING_STRATEGY.md
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview")
content = (ROOT / "TESTING_STRATEGY.md").read_text(encoding="utf-8")

matches = re.finditer(r"def\s+(test_[a-zA-Z0-9_]+)\s*\((.*?)\):(?:\s*\"\"\"(.*?)\"\"\")?", content, re.DOTALL)
tests = list(matches)
print(f"Total test functions found: {len(tests)}")
for idx, m in enumerate(tests, 1):
    name = m.group(1)
    args = m.group(2).strip()
    doc = (m.group(3) or "").strip().split("\n")[0]
    print(f"{idx:2d}. {name} | {doc[:70]}")
