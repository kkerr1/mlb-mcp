"""
MCP server implementation for the baseball project with MLB Stats API integration.
"""

import inspect
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from mlb_stats_mcp.tools import (
    mlb_statsapi_tools,
    pybaseball_plotting_tools,
    pybaseball_supp_tools,
    statcast_tools,
)
from mlb_stats_mcp.utils.logging_config import setup_logging

# Initialize logging for the server
logger = setup_logging("mcp_server")

# Initialize FastMCP server
mcp = FastMCP("baseball")


def mcp_tool_wrapper(func):
    """Decorator to handle errors from tool functions."""
    sig = inspect.signature(func)

    # Create a wrapper function with the same signature as the original function
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e!s}")
            raise Exception(f"Error in {func.__name__}: {e!s}") from e

    # Copy the signature from the original function
    wrapper.__signature__ = sig

    # Register the tool with MCP
    return mcp.tool(name=func.__name__)(wrapper)


# Core Data Gathering Tools
@mcp_tool_wrapper
async def get_stats(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_stats(endpoint, params)


@mcp_tool_wrapper
async def get_schedule(
    date: Optional[str] = None,
    team_id: Optional[int] = None,
    sport_id: int = 1,
    game_type: Optional[str] = None,
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_schedule(date, team_id, sport_id, game_type)


@mcp_tool_wrapper
async def get_player_stats(
    player_id: int,
    group: str = "hitting",
    season: Optional[int] = None,
    stats: str = "season",
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_player_stats(player_id, group, season, stats)


@mcp_tool_wrapper
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
@mcp_tool_wrapper
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


@mcp_tool_wrapper
async def lookup_player(name: str) -> Dict[str, Any]:
    return await mlb_statsapi_tools.lookup_player(name)


@mcp_tool_wrapper
async def get_boxscore(game_id: int, timecode: Optional[str] = None) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_boxscore(game_id, timecode)


@mcp_tool_wrapper
async def get_team_roster(
    team_id: int,
    roster_type: str = "active",
    season: Optional[int] = None,
    date: Optional[str] = None,
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_team_roster(team_id, roster_type, season, date)


# Historical Context Tools
@mcp_tool_wrapper
async def get_game_pace(
    season: Optional[int] = None, team_id: Optional[int] = None
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_game_pace(season, team_id)


@mcp_tool_wrapper
async def get_meta(type_name: str, fields: Optional[str] = None) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_meta(type_name, fields)


@mcp_tool_wrapper
async def get_available_endpoints() -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_available_endpoints()


@mcp_tool_wrapper
async def get_notes(endpoint: str) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_notes(endpoint)


@mcp_tool_wrapper
async def get_game_scoring_play_data(game_id: int) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_game_scoring_play_data(game_id)


@mcp_tool_wrapper
async def get_last_game(team_id: int) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_last_game(team_id)


@mcp_tool_wrapper
async def get_league_leader_data(
    leader_categories: str,
    season: Optional[int] = None,
    limit: Optional[int] = None,
    stat_group: Optional[str] = None,
    league_id: Optional[int] = None,
) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_league_leader_data(
        leader_categories, season, limit, stat_group, league_id
    )


@mcp_tool_wrapper
async def get_linescore(game_id: int) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_linescore(game_id)


@mcp_tool_wrapper
async def get_next_game(team_id: int) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_next_game(team_id)


@mcp_tool_wrapper
async def get_game_highlight_data(game_id: int) -> Dict[str, Any]:
    return await mlb_statsapi_tools.get_game_highlight_data(game_id)


# Statcast Tools
@mcp_tool_wrapper
async def get_statcast_data(
    start_dt: Optional[str] = None,
    end_dt: Optional[str] = None,
    team: Optional[str] = None,
    verbose: bool = True,
    parallel: bool = True,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_data(
        start_dt, end_dt, team, verbose, parallel
    )


@mcp_tool_wrapper
async def get_statcast_batter_data(
    player_id: int,
    start_dt: Optional[str] = None,
    end_dt: Optional[str] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_batter_data(player_id, start_dt, end_dt)


@mcp_tool_wrapper
async def get_statcast_pitcher_data(
    player_id: int,
    start_dt: Optional[str] = None,
    end_dt: Optional[str] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_pitcher_data(player_id, start_dt, end_dt)


@mcp_tool_wrapper
async def get_statcast_batter_exitvelo_barrels(
    year: int,
    minBBE: Optional[int] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_batter_exitvelo_barrels(year, minBBE)


@mcp_tool_wrapper
async def get_statcast_pitcher_exitvelo_barrels(
    year: int,
    minBBE: Optional[int] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_pitcher_exitvelo_barrels(year, minBBE)


@mcp_tool_wrapper
async def get_statcast_batter_expected_stats(
    year: int,
    minPA: Optional[int] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_batter_expected_stats(year, minPA)


@mcp_tool_wrapper
async def get_statcast_pitcher_expected_stats(
    year: int,
    minPA: Optional[int] = None,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_pitcher_expected_stats(year, minPA)


@mcp_tool_wrapper
async def get_statcast_batter_percentile_ranks(year: int) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_batter_percentile_ranks(year)


@mcp_tool_wrapper
async def get_statcast_pitcher_percentile_ranks(year: int) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_pitcher_percentile_ranks(year)


@mcp_tool_wrapper
async def get_statcast_batter_pitch_arsenal(
    year: int,
    minPA: int = 25,
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_batter_pitch_arsenal(year, minPA)


@mcp_tool_wrapper
async def get_statcast_pitcher_pitch_arsenal(
    year: int,
    minP: Optional[int] = None,
    arsenal_type: str = "average_speed",
) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_pitcher_pitch_arsenal(
        year, minP, arsenal_type
    )


@mcp_tool_wrapper
async def get_statcast_single_game(game_pk: int) -> Dict[str, Any]:
    return await statcast_tools.get_statcast_single_game(game_pk)


@mcp_tool_wrapper
async def create_strike_zone_plot(
    data: Dict[str, Any],
    title: str = "",
    colorby: str = "pitch_type",
    legend_title: str = "",
    annotation: str = "pitch_type",
) -> Dict[str, Any]:
    return await pybaseball_plotting_tools.create_strike_zone_plot(
        data, title, colorby, legend_title, annotation
    )


@mcp_tool_wrapper
async def create_spraychart_plot(
    data: Dict[str, Any],
    team_stadium: str = "generic",
    title: str = "",
    colorby: str = "events",
    legend_title: str = "",
    size: int = 100,
    width: int = 500,
    height: int = 500,
) -> Dict[str, Any]:
    return await pybaseball_plotting_tools.create_spraychart_plot(
        data, team_stadium, title, colorby, legend_title, size, width, height
    )


@mcp_tool_wrapper
async def create_bb_profile_plot(
    data: Dict[str, Any],
    parameter: str = "launch_angle",
) -> Dict[str, Any]:
    return await pybaseball_plotting_tools.create_bb_profile_plot(data, parameter)


@mcp_tool_wrapper
async def create_teams_plot(
    data: Dict[str, Any],
    x_axis: str,
    y_axis: str,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    return await pybaseball_plotting_tools.create_teams_plot(
        data, x_axis, y_axis, title
    )


# Supplemental pybaseball tools
@mcp_tool_wrapper
async def get_pitching_stats_bref(season: Optional[int] = None) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_pitching_stats_bref(season)


@mcp_tool_wrapper
async def get_pitching_stats_range(
    start_dt: str,
    end_dt: Optional[str] = None,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_pitching_stats_range(start_dt, end_dt)


@mcp_tool_wrapper
async def get_pitching_stats(
    start_season: int,
    end_season: Optional[int] = None,
    league: str = "all",
    qual: Optional[int] = None,
    ind: int = 1,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_pitching_stats(
        start_season, end_season, league, qual, ind
    )


@mcp_tool_wrapper
async def get_playerid_lookup(
    last: str,
    first: Optional[str] = None,
    fuzzy: bool = False,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_playerid_lookup(last, first, fuzzy)


@mcp_tool_wrapper
async def reverse_lookup_player(
    player_ids: list[int],
    key_type: str = "mlbam",
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.reverse_lookup_player(player_ids, key_type)


@mcp_tool_wrapper
async def get_schedule_and_record(season: int, team: str) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_schedule_and_record(season, team)


@mcp_tool_wrapper
async def get_player_splits(
    playerid: str,
    year: Optional[int] = None,
    player_info: bool = False,
    pitching_splits: bool = False,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_player_splits(
        playerid, year, player_info, pitching_splits
    )


@mcp_tool_wrapper
async def get_pybaseball_standings(season: Optional[int] = None) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_standings(season)


@mcp_tool_wrapper
async def get_team_batting(
    start_season: int,
    end_season: Optional[int] = None,
    league: str = "all",
    ind: int = 1,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_team_batting(
        start_season, end_season, league, ind
    )


@mcp_tool_wrapper
async def get_team_fielding(
    start_season: int,
    end_season: Optional[int] = None,
    league: str = "all",
    ind: int = 1,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_team_fielding(
        start_season, end_season, league, ind
    )


@mcp_tool_wrapper
async def get_team_pitching(
    start_season: int,
    end_season: Optional[int] = None,
    league: str = "all",
    ind: int = 1,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_team_pitching(
        start_season, end_season, league, ind
    )


@mcp_tool_wrapper
async def get_top_prospects(
    team: Optional[str] = None,
    player_type: Optional[str] = None,
) -> Dict[str, Any]:
    return await pybaseball_supp_tools.get_top_prospects(team, player_type)


def main():
    """Initialize and run the MCP baseball server."""
    logger.info("Starting MLB Stats MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
