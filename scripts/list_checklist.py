"""
Audit checklist items in PRODUCTION_LAUNCH_MANUAL.md
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview")
content = (ROOT / "PRODUCTION_LAUNCH_MANUAL.md").read_text(encoding="utf-8")

pillars = re.findall(r"###\s*(2\.\d+)\s*([^|\n]+)\n+([\s\S]*?)(?=###\s*2\.\d+|\n##\s*3\.)", content)
print(f"Pillars found: {len(pillars)}")
total_items = 0
for pnum, pname, pbody in pillars:
    rows = re.findall(r"\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|\n]+)\|", pbody)
    print(f"  {pnum}: {pname.strip()} -> {len(rows)} items")
    total_items += len(rows)
    for r in rows[:2]:
        print(f"    Item {r[0]}: {r[1].strip()[:50]} [{r[5].strip()}]")
print(f"Total checklist items across all pillars: {total_items}")
