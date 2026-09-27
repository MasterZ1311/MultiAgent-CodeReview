"""
Universal CommonMark Block Analyzer for Docs 5-8
"""
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
    lines = content.splitlines()
    blocks = []
    in_block = False
    cur_lang = ""
    cur_start = 0
    cur_lines = []

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
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

    print(f"\n==================================================")
    print(f"{doc_name}: {len(blocks)} CommonMark code blocks")
    print(f"==================================================")
    missing_lang = 0
    missing_header = 0
    for idx, (lang, start, end, blines) in enumerate(blocks, 1):
        first_line = blines[0].strip() if blines else "<empty>"
        if not lang:
            missing_lang += 1
            print(f"  WARNING: Block {idx} missing language (lines {start}-{end})")
        if not any(k in first_line.lower() for k in ["file:", "path:"]):
            missing_header += 1
            print(f"  WARNING: Block {idx} missing file header (lines {start}-{end}): {first_line[:60]}")
    print(f"Summary for {doc_name}:")
    print(f"  Total Blocks: {len(blocks)}")
    print(f"  Missing Language Tag: {missing_lang}")
    print(f"  Missing File Header: {missing_header}")
