"""
Check runtime errors (NameError, TypeError, ImportError, etc.) across all blocks in Docs 1-4.
"""
from pathlib import Path
from scripts.verify_python_blocks import extract_python_blocks, ROOT

def main():
    docs = [
        'PHASE_1_DETAILED_IMPLEMENTATION.md',
        'AGENT_SPECIFICATIONS.md',
        'API_SPECIFICATIONS.md',
        'DATABASE_DESIGN.md'
    ]
    
    for doc_name in docs:
        blocks = extract_python_blocks(ROOT / doc_name)
        print(f"\n==========================================")
        print(f"Checking {doc_name} ({len(blocks)} blocks)")
        print(f"==========================================")
        
        for idx, b in enumerate(blocks, 1):
            namespace = {}
            # First line header
            first_line = b['content'].splitlines()[0] if b['content'].splitlines() else ""
            try:
                exec(b['content'], namespace)
            except NameError as e:
                print(f"[FAIL] Block #{idx} (lines {b['start']}-{b['end']}) {first_line}: NameError: {e}")
            except ImportError as e:
                print(f"[FAIL] Block #{idx} (lines {b['start']}-{b['end']}) {first_line}: ImportError: {e}")
            except Exception as e:
                print(f"[FAIL] Block #{idx} (lines {b['start']}-{b['end']}) {first_line}: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
