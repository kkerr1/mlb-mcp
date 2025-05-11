"""
Tests for pybaseball tools in the baseball project.
"""

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pathlib import Path


def simplify_session_setup():
    """Helper to create server params for tests."""
    server_path = Path(__file__).parent.parent / "server.py"
    return StdioServerParameters(command="python", args=[str(server_path)], env=None)


# Add pybaseball tool tests here
