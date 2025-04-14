"""
MCP server implementation for the baseball project with MLB Stats API integration.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from mlb_stats_mcp.tools import mlb_statsapi_tools
from mlb_stats_mcp.utils.logging_config import setup_logging

# Initialize logging for the server
logger = setup_logging("mcp_server")

# Initialize FastMCP server
mcp = FastMCP("baseball")


# Core Data Gathering Tools
@mcp.tool()
async def get_stats(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_stats(endpoint, params)


@mcp.tool()
async def get_schedule(
    date: Optional[str] = None,
    team_id: Optional[int] = None,
    sport_id: int = 1,
    game_type: Optional[str] = None,
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_schedule(date, team_id, sport_id, game_type)


@mcp.tool()
async def get_player_stats(
    player_id: int,
    group: str = "hitting",
    season: Optional[int] = None,
    stats: str = "season",
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_player_stats(player_id, group, season, stats)


@mcp.tool()
async def get_standings(
    league_id: Optional[int] = None,
    division_id: Optional[int] = None,
    season: Optional[int] = None,
    standings_types: str = "regularSeason",
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_standings(
        league_id, division_id, season, standings_types
    )


# Team and Player Analysis Tools
@mcp.tool()
async def get_team_leaders(
    team_id: int,
    leader_category: str = "homeRuns",
    season: Optional[int] = None,
    leader_game_type: str = "R",
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_team_leaders(
        team_id, leader_category, season, leader_game_type, limit
    )


@mcp.tool()
async def lookup_player(name: str) -> Dict[str, Any]:
    return await mlb_statsapi_tools.lookup_player(name)


@mcp.tool()
async def get_boxscore(game_id: int, timecode: Optional[str] = None) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_boxscore(game_id, timecode)


# Historical Context Tools
@mcp.tool()
async def get_game_pace(
    season: Optional[int] = None, team_id: Optional[int] = None
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_game_pace(season, team_id)


@mcp.tool()
async def get_meta(type_name: str, fields: Optional[str] = None) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_meta(type_name, fields)


@mcp.tool()
async def get_available_endpoints() -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_available_endpoints()


@mcp.tool()
async def get_notes(endpoint: str) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_notes(endpoint)


def main():
    """Initialize and run the MCP baseball server."""
    logger.info("Starting MLB Stats MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
