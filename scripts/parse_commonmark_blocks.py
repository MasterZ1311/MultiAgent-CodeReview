"""
Line-based code block extractor for TESTING_STRATEGY.md
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview")
content = (ROOT / "TESTING_STRATEGY.md").read_text(encoding="utf-8")

lines = content.splitlines()
blocks = []
in_block = False
cur_lang = ""
cur_start = 0
cur_lines = []

for idx, line in enumerate(lines, 1):
    stripped = line.strip()
    # In CommonMark, a code fence starts at line start with 3 backticks
    if stripped.startswith("```"):
        if not in_block:
            in_block = True
            cur_lang = stripped[3:].strip()
            cur_start = idx
            cur_lines = []
        else:
            in_block = False
            blocks.append((cur_lang, cur_start, idx, cur_lines))
    elif in_block:
        cur_lines.append(line)

print(f"Total CommonMark blocks: {len(blocks)}")
for idx, (lang, start, end, blines) in enumerate(blocks, 1):
    first_line = blines[0].strip() if blines else "<empty>"
    print(f"[{idx:2d}] ({lang:10s}) lines {start:4d}-{end:4d} | {first_line[:75]}")
