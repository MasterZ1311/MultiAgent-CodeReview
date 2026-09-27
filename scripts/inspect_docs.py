"""
Comprehensive empirical analyzer and validator for Docs 1-4:
- PHASE_1_DETAILED_IMPLEMENTATION.md
- AGENT_SPECIFICATIONS.md
- DATABASE_DESIGN.md
- API_SPECIFICATIONS.md
"""
import ast
import os
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(r"e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview")
DOCS = [
    "PHASE_1_DETAILED_IMPLEMENTATION.md",
    "AGENT_SPECIFICATIONS.md",
    "DATABASE_DESIGN.md",
    "API_SPECIFICATIONS.md"
]

def extract_code_blocks(text):
    """Extract code blocks with line numbers and lang."""
    lines = text.split("\n")
    blocks = []
    in_block = False
    current_lang = ""
    start_line = 0
    current_content = []

    for idx, line in enumerate(lines, 1):
        if line.startswith("```"):
            if not in_block:
                in_block = True
                current_lang = line[3:].strip().lower()
                start_line = idx + 1
                current_content = []
            else:
                in_block = False
                end_line = idx - 1
                blocks.append({
                    "lang": current_lang,
                    "start": start_line,
                    "end": end_line,
                    "content": "\n".join(current_content)
                })
        elif in_block:
            current_content.append(line)
    return blocks

def analyze_document_structure(doc_path):
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    
    # 1. Title
    title = lines[0] if lines else ""
    has_h1 = title.startswith("# ")
    
    # 2. Table of contents
    has_toc = any("Table of Contents" in line or "## Contents" in line for line in lines[:50])
    
    # 3. Next doc pointer
    tail_text = "\n".join(lines[-30:])
    has_next_pointer = bool(re.search(r"(Next|Proceed to|Next Document|Next Step)", tail_text, re.IGNORECASE))
    
    # 4. Code blocks
    blocks = extract_code_blocks(text)
    
    return {
        "title": title,
        "has_h1": has_h1,
        "has_toc": has_toc,
        "has_next_pointer": has_next_pointer,
        "blocks": blocks,
        "total_lines": len(lines)
    }

def main():
    print("=== DOCS 1-4 EMPIRICAL CODE & STRUCTURE VALIDATION ===")
    all_results = {}
    
    for doc_name in DOCS:
        doc_path = ROOT / doc_name
        if not doc_path.exists():
            print(f"ERROR: {doc_name} not found!")
            continue
        print(f"\nScanning: {doc_name}")
        info = analyze_document_structure(doc_path)
        all_results[doc_name] = info
        print(f"  Title: {info['title']}")
        print(f"  Lines: {info['total_lines']}")
        print(f"  Has H1 Title: {info['has_h1']}")
        print(f"  Has TOC: {info['has_toc']}")
        print(f"  Has Next Doc Pointer: {info['has_next_pointer']}")
        print(f"  Code blocks count: {len(info['blocks'])}")
        
        # Breakdown by language
        langs = {}
        for b in info['blocks']:
            langs[b['lang']] = langs.get(b['lang'], 0) + 1
        print(f"  Languages: {langs}")
        
        # Check file path header in code blocks
        blocks_without_file_header = []
        for i, b in enumerate(info['blocks']):
            first_lines = "\n".join(b['content'].splitlines()[:3])
            has_file_header = bool(re.search(r"(#|--|\/\/)\s*(File|file|Path|path):", first_lines))
            # Some blocks might be bash commands or output or json config
            if b['lang'] in ['python', 'yaml', 'sql'] and not has_file_header:
                blocks_without_file_header.append((i, b['lang'], b['start'], b['end'], first_lines.splitlines()[0] if first_lines else ""))
                
        print(f"  Code blocks (py/yaml/sql) without file header: {len(blocks_without_file_header)}")
        for b_idx, lang, start, end, first_line in blocks_without_file_header[:5]:
            print(f"    Block {b_idx} ({lang}, lines {start}-{end}): {first_line[:60]}")

if __name__ == "__main__":
    main()
