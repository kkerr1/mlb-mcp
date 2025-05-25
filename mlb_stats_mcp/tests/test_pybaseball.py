"""
Tests for pybaseball tools in the baseball project.
"""

import json
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def simplify_session_setup():
    """Helper to create server params for tests."""
    server_path = Path(__file__).parent.parent / "server.py"
    return StdioServerParameters(command="python", args=[str(server_path)], env=None)


@pytest.mark.asyncio
async def test_get_statcast_data():
    """Test the get_statcast_data tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters - using a small date range to minimize test time
            result = await session.call_tool(
                "get_statcast_data", {"start_dt": "2023-04-01", "end_dt": "2023-04-01"}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"

            # Test with team parameter
            result = await session.call_tool(
                "get_statcast_data",
                {"start_dt": "2023-04-01", "end_dt": "2023-04-01", "team": "NYY"},
            )
            assert not result.isError, "Expected successful response"


@pytest.mark.asyncio
async def test_get_statcast_batter_data():
    """Test the get_statcast_batter_data tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters - using Aaron Judge's ID
            result = await session.call_tool(
                "get_statcast_batter_data",
                {"player_id": 592450, "start_dt": "2023-04-01", "end_dt": "2023-04-01"},
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"

            # Test with invalid player ID
            result = await session.call_tool(
                "get_statcast_batter_data",
                {
                    "player_id": 99999999,
                    "start_dt": "2023-04-01",
                    "end_dt": "2023-04-01",
                },
            )
            assert result.isError, "Expected error response for invalid player ID"


@pytest.mark.asyncio
async def test_get_statcast_pitcher_data():
    """Test the get_statcast_pitcher_data tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters - using Gerrit Cole's ID
            result = await session.call_tool(
                "get_statcast_pitcher_data",
                {"player_id": 543037, "start_dt": "2023-04-01", "end_dt": "2024-04-01"},
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"

            # Test with invalid player ID
            result = await session.call_tool(
                "get_statcast_pitcher_data",
                {
                    "player_id": 99999999,
                    "start_dt": "2023-04-01",
                    "end_dt": "2024-04-01",
                },
            )
            assert result.isError, "Expected error response for invalid player ID"


@pytest.mark.asyncio
async def test_get_statcast_batter_exitvelo_barrels():
    """Test the get_statcast_batter_exitvelo_barrels tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_batter_exitvelo_barrels", {"year": 2023, "minBBE": 50}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_pitcher_exitvelo_barrels():
    """Test the get_statcast_pitcher_exitvelo_barrels tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_pitcher_exitvelo_barrels", {"year": 2023, "minBBE": 50}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_batter_expected_stats():
    """Test the get_statcast_batter_expected_stats tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_batter_expected_stats", {"year": 2023, "minPA": 50}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_pitcher_expected_stats():
    """Test the get_statcast_pitcher_expected_stats tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_pitcher_expected_stats", {"year": 2023, "minPA": 50}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_batter_percentile_ranks():
    """Test the get_statcast_batter_percentile_ranks tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_batter_percentile_ranks", {"year": 2023}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_pitcher_percentile_ranks():
    """Test the get_statcast_pitcher_percentile_ranks tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_pitcher_percentile_ranks", {"year": 2023}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_batter_pitch_arsenal():
    """Test the get_statcast_batter_pitch_arsenal tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_batter_pitch_arsenal", {"year": 2023, "minPA": 50}
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"


@pytest.mark.asyncio
async def test_get_statcast_pitcher_pitch_arsenal():
    """Test the get_statcast_pitcher_pitch_arsenal tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_statcast_pitcher_pitch_arsenal",
                {"year": 2023, "minP": 50, "arsenal_type": "avg_speed"},
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"

            # Test with different arsenal type
            result = await session.call_tool(
                "get_statcast_pitcher_pitch_arsenal",
                {"year": 2023, "minP": 50, "arsenal_type": "avg_spin"},
            )
            assert not result.isError, "Expected successful response"

            # Test with invalid arsenal type
            result = await session.call_tool(
                "get_statcast_pitcher_pitch_arsenal",
                {"year": 2023, "minP": 50, "arsenal_type": "invalid_type"},
            )
            assert result.isError, "Expected error for invalid arsenal type"


@pytest.mark.asyncio
async def test_get_statcast_single_game():
    """Test the get_statcast_single_game tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters - using a known game ID
            result = await session.call_tool(
                "get_statcast_single_game",
                {"game_pk": 717953},  # Example game from 2023
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"
            assert "count" in data, "Response should contain 'count' key"
            assert "columns" in data, "Response should contain 'columns' key"

            # Test with invalid game ID
            result = await session.call_tool(
                "get_statcast_single_game", {"game_pk": 999999999}
            )
            assert result.isError, "Expected error response for invalid game ID"
