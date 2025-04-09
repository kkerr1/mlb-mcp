"""
Pytest configuration file for the baseball MCP tests.
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import the baseball package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
