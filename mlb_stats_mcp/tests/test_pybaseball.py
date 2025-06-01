"""
Tests for pybaseball tools.
"""

import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from mlb_stats_mcp.utils.images import display_base64_image
from mlb_stats_mcp.utils.logging_config import setup_logging

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

logger = setup_logging("test_suite")

logger.debug(f"SHOW_IMAGE SET TO {os.environ.get('SHOW_IMAGE')}")


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


@pytest.mark.asyncio
async def test_image_create_spraychart_altuve():
    """Test the create_spraychart_plot tool following the Altuve example."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            try:
                # Get statcast batter data for Jose Altuve
                batter_result = await session.call_tool(
                    "get_statcast_batter_data",
                    {
                        "player_id": 514888,
                        "start_dt": "2019-05-01",
                        "end_dt": "2019-07-01",
                    },
                )

                assert not batter_result.isError
                batter_data = json.loads(batter_result.content[0].text)

                assert "data" in batter_data
                assert len(batter_data["data"]) > 0
            except Exception as e:
                raise Exception(f"Exception occured in pre-req batter data: {e}") from e

            # Create spraychart
            try:
                spraychart_result = await session.call_tool(
                    "create_spraychart_plot",
                    {
                        "data": batter_data,
                        "team_stadium": "astros",
                        "title": "Jose Altuve: May-June 2019",
                        "colorby": "events",
                        "size": 120,
                        "width": 1024,
                        "height": 1024,
                    },
                )
            except Exception as e:
                raise Exception(f"Exception occured in spraychart tool: {e}") from e

            assert not spraychart_result.isError
            result_json = json.loads(spraychart_result.content[0].text)

            # Verify response structure
            assert result_json["plot_type"] == "spraychart"
            assert "image_base64" in result_json
            assert len(result_json["image_base64"]) > 100
            assert result_json["hit_count"] > 0
            assert result_json["stadium"] == "astros"
            assert result_json["title"] == "Jose Altuve: May-June 2019"
            assert "metadata" in result_json
            assert result_json["metadata"]["colorby"] == "events"
            assert isinstance(result_json["metadata"]["events"], dict)

            # Display the image if SHOW_IMAGE environment variable is set to true
            if os.environ.get("SHOW_IMAGE", "false").lower() == "true":
                display_base64_image(result_json["image_base64"])


@pytest.mark.asyncio
async def test_image_create_spraychart_plot_votto_aquino():
    """Test spraychart with Joey Votto vs. Aristedes Aquino data."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            try:
                # Get statcast batter data for Joey Votto (458015)
                votto_result = await session.call_tool(
                    "get_statcast_batter_data",
                    {
                        "player_id": 458015,
                        "start_dt": "2019-08-01",
                        "end_dt": "2019-10-01",
                    },
                )

                assert not votto_result.isError
                votto_data = json.loads(votto_result.content[0].text)

                # Get statcast batter data for Aristedes Aquino (606157)
                aquino_result = await session.call_tool(
                    "get_statcast_batter_data",
                    {
                        "player_id": 606157,
                        "start_dt": "2019-08-01",
                        "end_dt": "2019-10-01",
                    },
                )

                assert not aquino_result.isError
                aquino_data = json.loads(aquino_result.content[0].text)

                # Combine the data (concatenate the data arrays)
                combined_data = {"data": votto_data["data"] + aquino_data["data"]}

                assert len(combined_data["data"]) > 0
            except Exception as e:
                raise Exception(
                    f"Exception occurred in pre-req batter data: {e}"
                ) from e

            # Create spraychart
            try:
                spraychart_result = await session.call_tool(
                    "create_spraychart_plot",
                    {
                        "data": combined_data,
                        "team_stadium": "reds",
                        "title": "Joey Votto vs. Aristedes Aquino",
                        "colorby": "player_name",  # Color by player
                        "size": 120,
                        "width": 1024,
                        "height": 1024,
                    },
                )
            except Exception as e:
                raise Exception(f"Exception occurred in spraychart tool: {e}") from e

            assert not spraychart_result.isError
            result_json = json.loads(spraychart_result.content[0].text)

            # Verify response structure
            assert result_json["plot_type"] == "spraychart"
            assert "image_base64" in result_json
            assert len(result_json["image_base64"]) > 100
            assert result_json["hit_count"] > 0
            assert result_json["stadium"] == "reds"
            assert result_json["title"] == "Joey Votto vs. Aristedes Aquino"
            assert "metadata" in result_json
            assert result_json["metadata"]["colorby"] == "player_name"
            assert isinstance(result_json["metadata"]["events"], dict)

            # Display the image if SHOW_IMAGE environment variable is set to true
            if os.environ.get("SHOW_IMAGE", "false").lower() == "true":
                display_base64_image(result_json["image_base64"])


@pytest.mark.asyncio
async def test_image_create_bb_profile_plot():
    """Test bb_profile plot recreating the example logic."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            try:
                # Get statcast data for specific date range
                statcast_result = await session.call_tool(
                    "get_statcast_data",
                    {
                        "start_dt": "2018-05-01",
                        "end_dt": "2018-05-04",
                        "verbose": True,
                        "parallel": True,
                    },
                )

                assert not statcast_result.isError
                statcast_data = json.loads(statcast_result.content[0].text)

                assert "data" in statcast_data
                assert len(statcast_data["data"]) > 0
            except Exception as e:
                raise Exception(
                    f"Exception occurred in pre-req statcast data: {e}"
                ) from e

            # Create bb_profile plot
            try:
                bb_profile_result = await session.call_tool(
                    "create_bb_profile_plot",
                    {
                        "data": statcast_data,
                        "parameter": "launch_angle",
                    },
                )
            except Exception as e:
                raise Exception(f"Exception occurred in bb_profile tool: {e}") from e

            assert not bb_profile_result.isError
            result_json = json.loads(bb_profile_result.content[0].text)

            # Verify response structure
            assert result_json["plot_type"] == "bb_profile"
            assert "image_base64" in result_json
            assert len(result_json["image_base64"]) > 100
            assert result_json["bb_count"] > 0
            assert result_json["parameter"] == "launch_angle"
            assert "metadata" in result_json
            assert isinstance(result_json["metadata"]["bb_types"], dict)

            # Display the image if SHOW_IMAGE environment variable is set to true
            if os.environ.get("SHOW_IMAGE", "false").lower() == "true":
                display_base64_image(result_json["image_base64"])


@pytest.mark.asyncio
async def test_image_plot_teams():
    """Test plotting teams based on team batting data."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Get team batting data for 2023
            result = await session.call_tool(
                "get_team_batting",
                {"start_season": 2023, "league": "all"},
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

            # Create plot_teams visualization
            plot_result = await session.call_tool(
                "create_teams_plot",
                {
                    "data": data,
                    "x_axis": "HR",
                    "y_axis": "BB",
                    "title": "Team HR vs BB (2023)",
                },
            )

            # Verify successful plot response
            assert not plot_result.isError, "Expected successful plot response"
            assert plot_result.content, "No content returned from plot tool"
            assert plot_result.content[0].type == "text", "Expected text response"

            # Verify plot response structure
            plot_data = json.loads(plot_result.content[0].text)
            assert "plot_type" in plot_data, "Response should contain 'plot_type' key"
            assert plot_data["plot_type"] == "teams"
            assert (
                "image_base64" in plot_data
            ), "Response should contain 'image_base64' key"
            assert (
                len(plot_data["image_base64"]) > 100
            ), "Image data should be substantial"
            assert "team_count" in plot_data, "Response should contain 'team_count' key"
            assert plot_data["team_count"] > 0, "Should have team data"
            assert "x_axis" in plot_data, "Response should contain 'x_axis' key"
            assert plot_data["x_axis"] == "HR"
            assert "y_axis" in plot_data, "Response should contain 'y_axis' key"
            assert plot_data["y_axis"] == "BB"

            # Display the image if SHOW_IMAGE environment variable is set to true
            if os.environ.get("SHOW_IMAGE", "false").lower() == "true":
                display_base64_image(plot_data["image_base64"])


@pytest.mark.asyncio
async def test_get_pitching_stats_bref():
    """Test the get_pitching_stats_bref tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_pitching_stats_bref", {"season": 2023}
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
            assert data["count"] > 0, "Should have pitching data"


@pytest.mark.asyncio
async def test_get_pitching_stats_range():
    """Test the get_pitching_stats_range tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_pitching_stats_range",
                {"start_dt": "2023-04-01", "end_dt": "2023-04-07"},
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
async def test_get_pitching_stats():
    """Test the get_pitching_stats tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_pitching_stats",
                {"start_season": 2023, "qual": 50},
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
async def test_get_schedule_and_record():
    """Test the get_schedule_and_record tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_schedule_and_record",
                {"season": 2023, "team": "LAD"},
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
async def test_get_player_splits():
    """Test the get_player_splits tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters - Mike Trout's Baseball Reference ID
            result = await session.call_tool(
                "get_player_splits",
                {"playerid": "troutmi01", "year": 2023},
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
async def test_get_pybaseball_standings():
    """Test the get_pybaseball_standings tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_pybaseball_standings",
                {"season": 2023},
            )

            # Verify successful response
            assert not result.isError, "Expected successful response"
            assert result.content, "No content returned from tool"
            assert result.content[0].type == "text", "Expected text response"

            # Verify response structure
            data = json.loads(result.content[0].text)
            assert "data" in data, "Response should contain 'data' key"


@pytest.mark.asyncio
async def test_get_team_batting():
    """Test the get_team_batting tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_team_batting",
                {"start_season": 2023, "league": "all"},
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
async def test_get_team_fielding():
    """Test the get_team_fielding tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_team_fielding",
                {"start_season": 2023, "league": "all"},
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
async def test_get_team_pitching():
    """Test the get_team_pitching tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_team_pitching",
                {"start_season": 2023, "league": "all"},
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
async def test_get_top_prospects():
    """Test the get_top_prospects tool."""
    params = simplify_session_setup()

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test with valid parameters
            result = await session.call_tool(
                "get_top_prospects",
                {"team": "angels", "player_type": "batters"},
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
