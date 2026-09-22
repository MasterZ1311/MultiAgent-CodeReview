"""
Compatibility layer mapping 'codevault' namespace directly to 'cerberus'.
Allows `python -m codevault.cli` and `import codevault` to work interchangeably.
"""

import sys
import cerberus

# Mirror all modules and CLI from cerberus
sys.modules["codevault"] = cerberus

__version__ = cerberus.__version__
