"""
Infrastructure tests for the MCP client with the baseball server.
"""

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pathlib import Path


def simplify_session_setup():
    """Helper to create server params for tests."""
    server_path = Path(__file__).parent.parent / "server.py"
    return StdioServerParameters(command="python", args=[str(server_path)], env=None)


@pytest.mark.asyncio
async def test_client_connection():
    """Test connecting to the MCP server and checking available tools."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            response = await session.list_tools()
            tools = response.tools
            tool_names = [tool.name for tool in tools]

            required_tools = ["get_schedule", "lookup_player", "get_standings"]
            for tool in required_tools:
                assert tool in tool_names, f"Missing required tool: {tool}"
