"""
MCP server implementation for the baseball project with MLB Stats API integration.
"""

import logging
import os
from typing import Any, Dict, Optional

import statsapi
from mcp.server.fastmcp import FastMCP


# Configure logging based on environment variables
def setup_logging():
    """Configure logging for the statsapi module based on environment variables."""
    # Get logging configuration from environment variables
    log_level = os.environ.get("MLB_STATS_LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("MLB_STATS_LOG_FILE", None)

    # Create logger for statsapi
    logger = logging.getLogger("statsapi")

    # Set the log level
    level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)8s - %(name)s - %(message)s"
    )

    # Configure root logger to ensure logs are properly displayed
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs
    logger.handlers = []

    # Add handlers based on configuration
    if log_file:
        # File handler if log file is specified
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Add a message indicating where logs are being sent
        logger.info(f"Logging configured at {log_level} level, writing to {log_file}")
    else:
        # Stream handler if no log file is specified
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Add a message indicating where logs are being sent
        logger.info(
            f"MLB Stats API logging configured at {log_level} level, writing to stdout"
        )

    return logger


# Initialize logging
logger = setup_logging()

# Initialize FastMCP server
mcp = FastMCP("baseball")


# Core Data Gathering Tools
@mcp.tool()
async def get_stats(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Access any endpoint in the MLB Stats API with custom parameters.

    Args:
        endpoint: The API endpoint to query (e.g., 'stats', 'schedule', 'standings')
        params: Dictionary of parameters to pass to the API

    Returns:
        JSON response from the MLB Stats API
    """
    try:
        logger.debug(
            f"Calling MLB Stats API endpoint: {endpoint} with params: {params}"
        )
        result = statsapi.get(endpoint, params)
        logger.debug(f"MLB Stats API response received for endpoint: {endpoint}")
        return result
    except Exception as e:
        error_msg = f"Error accessing MLB Stats API endpoint {endpoint}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "params": params}


@mcp.tool()
async def get_schedule(
    date: Optional[str] = None,
    team_id: Optional[int] = None,
    sport_id: int = 1,
    game_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get game schedule information.

    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
        team_id: MLB team ID to filter by
        sport_id: Sport ID (1 for MLB)
        game_type: Game type (R=Regular Season, F=Spring Training, etc.)

    Returns:
        Schedule data from the MLB Stats API
    """
    try:
        kwargs = {}
        if date is not None:
            kwargs["date"] = date
        if team_id is not None:
            kwargs["team"] = team_id
        if sport_id != 1:
            kwargs["sportId"] = sport_id
        if game_type is not None:
            kwargs["gameType"] = game_type

        logger.debug(f"Retrieving schedule with params: {kwargs}")
        result = statsapi.schedule(**kwargs)
        logger.debug(f"Retrieved schedule data: {len(result)} game(s)")
        return result
    except Exception as e:
        error_msg = f"Error retrieving schedule: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "params_sent": kwargs}


@mcp.tool()
async def get_player_stats(
    player_id: int,
    group: str = "hitting",
    season: Optional[int] = None,
    stats: str = "season",
) -> Dict[str, Any]:
    """
    Get comprehensive player statistics.

    Args:
        player_id: MLB player ID
        group: Stat group (hitting, pitching, fielding)
        season: Season year (defaults to current season)
        stats: Stat type (season, gameLog, etc.)

    Returns:
        Player statistics from the MLB Stats API
    """
    try:
        kwargs = {
            "personId": player_id,
            "group": group,
            "type": stats,
        }

        if season is not None:
            kwargs["season"] = season

        logger.debug(f"Stats for player ID: {player_id}, group: {group}, type: {stats}")
        result = statsapi.player_stat_data(**kwargs)
        logger.debug(f"Retrieved stats for player ID: {player_id}")
        return result
    except Exception as e:
        error_msg = f"Error retrieving player stats for player ID {player_id}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "params_sent": kwargs}


@mcp.tool()
async def get_standings(
    league_id: Optional[int] = None,
    division_id: Optional[int] = None,
    season: Optional[int] = None,
    standings_types: str = "regularSeason",
) -> Dict[str, Any]:
    """
    Get team standings information.

    Args:
        league_id: MLB league ID to filter by
        division_id: MLB division ID to filter by
        season: Season year (defaults to current season)
        standings_types: Type of standings (regularSeason, springTraining, etc.)

    Returns:
        Standings data from the MLB Stats API
    """
    try:
        kwargs = {"standingsTypes": standings_types}

        if league_id is not None:
            kwargs["leagueId"] = league_id
        if division_id is not None:
            kwargs["divisionId"] = division_id
        if season is not None:
            kwargs["season"] = season

        logger.debug(f"Retrieving standings with params: {kwargs}")
        result = statsapi.standings_data(**kwargs)
        logger.debug(f"Retrieved standings data for {standings_types}")
        return result
    except Exception as e:
        error_msg = f"Error retrieving standings: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "params_sent": kwargs}


# Team and Player Analysis Tools
@mcp.tool()
async def get_team_leaders(
    team_id: int,
    leader_category: str = "homeRuns",
    season: Optional[int] = None,
    leader_game_type: str = "R",
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get team statistical leaders.

    Args:
        team_id: MLB team ID
        leader_category: Statistic to sort by (homeRuns, battingAverage, etc.)
        season: Season year (defaults to current season)
        leader_game_type: Game type (R=Regular Season, etc.)
        limit: Number of leaders to return (defaults to all)

    Returns:
        Team leader data from the MLB Stats API
    """
    try:
        logger.debug(
            f"Retrieving team leaders for team: {team_id} | category: {leader_category}"
        )

        leaders_text = statsapi.team_leaders(
            team_id,
            leader_category,
            limit=10 if limit is None else limit,
            season=season,
        )

        logger.debug(f"Retrieved team leaders data for team ID: {team_id}")

        return {
            "teamId": team_id,
            "leaderCategory": leader_category,
            "season": season,
            "results": leaders_text,
            "teamLeaders": True,
        }
    except Exception as e:
        error_msg = f"Error retrieving team leaders for team ID {team_id}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "team_id": team_id, "leader_category": leader_category}


@mcp.tool()
async def lookup_player(name: str) -> Dict[str, Any]:
    """
    Look up a player by name to get their MLB ID.

    Args:
        name: Player name to search for

    Returns:
        Player lookup results from the MLB Stats API
    """
    try:
        logger.debug(f"Looking up player with name: {name}")
        result = statsapi.lookup_player(name)

        if result:
            logger.debug(f"Found {len(result)} player(s) matching: {name}")
        else:
            logger.info(f"No players found matching: {name}")

        return {"people": result}
    except Exception as e:
        error_msg = f"Error looking up player {name}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "name": name}


@mcp.tool()
async def get_boxscore(game_id: int, timecode: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed boxscore data for a game.

    Args:
        game_id: MLB game ID
        timecode: Optional timecode for in-game data

    Returns:
        Boxscore data from the MLB Stats API
    """
    try:
        logger.debug(f"Retrieving boxscore for game ID: {game_id}")

        # Add timecode if provided
        kwargs = {}
        if timecode:
            kwargs["timecode"] = timecode
            logger.debug(f"Using timecode: {timecode}")

        boxscore_text = statsapi.boxscore(game_id, **kwargs)
        logger.debug(f"Retrieved boxscore data for game ID: {game_id}")

        # Create a structured response
        return {"game_id": game_id, "boxscore": boxscore_text, "success": True}
    except Exception as e:
        error_msg = f"Error retrieving boxscore for game ID {game_id}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "game_id": game_id}


# Historical Context Tools
@mcp.tool()
async def get_game_pace(
    season: Optional[int] = None, team_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get game pace data to analyze how game length affects performance.

    Args:
        season: Season year (defaults to current season)
        team_id: MLB team ID to filter by

    Returns:
        Game pace data from the MLB Stats API
    """
    try:
        kwargs = {"sportId": 1}  # 1 is MLB

        if season is not None:
            kwargs["season"] = season
        if team_id is not None:
            kwargs["teamId"] = team_id

        logger.debug(f"Retrieving game pace data with params: {kwargs}")
        result = statsapi.game_pace_data(**kwargs)

        season_txt = f"season {season}" if season else "current season"
        team_txt = f"team ID {team_id}" if team_id else "all teams"
        logger.debug(f"Retrieved game pace data for {season_txt}, {team_txt}")

        return result
    except Exception as e:
        error_msg = f"Error retrieving game pace data: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "params_sent": kwargs}


@mcp.tool()
async def get_meta(type_name: str, fields: Optional[str] = None) -> Dict[str, Any]:
    """
    Get available values from StatsAPI for use in other queries,
        or look up descriptions.

    Args:
        type_name: Type of metadata to retrieve
            (e.g., 'leagueLeaderTypes', 'positions', 'statGroups')
        fields: Optional fields to return (limits response fields)

    Returns:
        Metadata information from the MLB Stats API

    Example types:
        awards, baseballStats, eventTypes, gameStatus, gameTypes, hitTrajectories,
        leagueLeaderTypes, metrics, pitchTypes, positions, statGroups, statTypes
    """
    try:
        logger.debug(f"Retrieving metadata for type: {type_name}")
        if fields:
            logger.debug(f"With field filtering: {fields}")
            result = statsapi.meta(type_name, fields=fields)
        else:
            result = statsapi.meta(type_name)

        logger.debug(f"Retrieved metadata for type: {type_name}")
        return result
    except Exception as e:
        error_msg = f"Error retrieving metadata for type {type_name}: {e!s}"
        logger.error(error_msg)
        return {"error": str(e), "type": type_name, "fields": fields}


@mcp.tool()
async def get_available_endpoints() -> Dict[str, Any]:
    """
    Get information about all available MLB Stats API endpoints that can be used with
    the get_stats tool.

    Returns:
        A dictionary containing details about all MLB Stats API endpoints, including:
        - endpoint name
        - URL pattern
        - required parameters
        - all available parameters
        - additional notes (if available)
    """
    try:
        logger.debug("Retrieving available MLB Stats API endpoints information")

        # Define all available endpoints with their details
        endpoints = {
            "attendance": {
                "url": "https://statsapi.mlb.com/api/{ver}/attendance",
                "required_params": ["teamId", "leagueId", "leagueListId"],
                "all_params": [
                    "ver",
                    "teamId",
                    "leagueId",
                    "season",
                    "date",
                    "leagueListId",
                    "gameType",
                    "fields",
                ],
                "notes": None,
            },
            "awards": {
                "url": "https://statsapi.mlb.com/api/{ver}/awards{awardId}{recipients}",
                "required_params": [],
                "all_params": [
                    "ver",
                    "awardId",
                    "recipients",
                    "sportId",
                    "leagueId",
                    "season",
                    "hydrate",
                    "fields",
                ],
                "notes": (
                    "Call awards endpoint with no parameters to return a list of "
                    "awardIds."
                ),
            },
            "conferences": {
                "url": "https://statsapi.mlb.com/api/{ver}/conferences",
                "required_params": [],
                "all_params": ["ver", "conferenceId", "season", "fields"],
                "notes": None,
            },
            "divisions": {
                "url": "https://statsapi.mlb.com/api/{ver}/divisions",
                "required_params": [],
                "all_params": ["ver", "divisionId", "leagueId", "sportId", "season"],
                "notes": (
                    "Call divisions endpoint with no parameters to return a list of "
                    "divisions."
                ),
            },
            "draft": {
                "url": "https://statsapi.mlb.com/api/{ver}/draft{prospects}{year}{latest}",
                "required_params": [],
                "all_params": [
                    "ver",
                    "prospects",
                    "year",
                    "latest",
                    "limit",
                    "fields",
                    "round",
                    "name",
                    "school",
                    "state",
                    "country",
                    "position",
                    "teamId",
                    "playerId",
                    "bisPlayerId",
                ],
                "notes": (
                    "No query parameters are honored when 'latest' endpoint is queried "
                    "(year is still required). Prospects and Latest cannot be used "
                    "together."
                ),
            },
            "game": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/feed/live",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "hydrate", "fields"],
                "notes": None,
            },
            "game_diff": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/feed/live/diffPatch",
                "required_params": ["gamePk", "startTimecode", "endTimecode"],
                "all_params": ["ver", "gamePk", "startTimecode", "endTimecode"],
                "notes": None,
            },
            "game_timestamps": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/feed/live/timestamps",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk"],
                "notes": None,
            },
            "game_changes": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/changes",
                "required_params": ["updatedSince"],
                "all_params": [
                    "ver",
                    "updatedSince",
                    "sportId",
                    "gameType",
                    "season",
                    "fields",
                ],
                "notes": None,
            },
            "game_contextMetrics": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/contextMetrics",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "fields"],
                "notes": None,
            },
            "game_winProbability": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/winProbability",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "fields"],
                "notes": (
                    "If you only want the current win probability for each team, try "
                    "the game_contextMetrics endpoint instead."
                ),
            },
            "game_boxscore": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/boxscore",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "fields"],
                "notes": None,
            },
            "game_content": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/content",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "highlightLimit"],
                "notes": None,
            },
            "game_linescore": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/linescore",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "fields"],
                "notes": None,
            },
            "game_playByPlay": {
                "url": "https://statsapi.mlb.com/api/{ver}/game/{gamePk}/playByPlay",
                "required_params": ["gamePk"],
                "all_params": ["ver", "gamePk", "timecode", "fields"],
                "notes": None,
            },
            "people": {
                "url": "https://statsapi.mlb.com/api/{ver}/people",
                "required_params": ["personIds"],
                "all_params": ["ver", "personIds", "hydrate", "fields"],
                "notes": None,
            },
            "person": {
                "url": "https://statsapi.mlb.com/api/{ver}/people/{personId}",
                "required_params": ["personId"],
                "all_params": ["ver", "personId", "hydrate", "fields"],
                "notes": None,
            },
            "person_stats": {
                "url": "https://statsapi.mlb.com/api/{ver}/people/{personId}/stats/game/{gamePk}",
                "required_params": ["personId", "gamePk"],
                "all_params": ["ver", "personId", "gamePk", "fields"],
                "notes": (
                    "Specify 'current' instead of a gamePk for a player's current "
                    "game stats."
                ),
            },
            "schedule": {
                "url": "https://statsapi.mlb.com/api/{ver}/schedule",
                "required_params": ["sportId or gamePk or gamePks"],
                "all_params": [
                    "ver",
                    "scheduleType",
                    "eventTypes",
                    "hydrate",
                    "teamId",
                    "leagueId",
                    "sportId",
                    "gamePk",
                    "gamePks",
                    "venueIds",
                    "gameTypes",
                    "date",
                    "startDate",
                    "endDate",
                    "opponentId",
                    "fields",
                    "season",
                ],
                "notes": None,
            },
            "standings": {
                "url": "https://statsapi.mlb.com/api/{ver}/standings",
                "required_params": ["leagueId"],
                "all_params": [
                    "ver",
                    "leagueId",
                    "season",
                    "standingsTypes",
                    "date",
                    "hydrate",
                    "fields",
                ],
                "notes": None,
            },
            "stats": {
                "url": "https://statsapi.mlb.com/api/{ver}/stats",
                "required_params": ["stats", "group"],
                "all_params": [
                    "ver",
                    "stats",
                    "playerPool",
                    "position",
                    "teamId",
                    "leagueId",
                    "limit",
                    "offset",
                    "group",
                    "gameType",
                    "season",
                    "sportIds",
                    "sortStat",
                    "order",
                    "hydrate",
                    "fields",
                    "personId",
                    "metrics",
                    "startDate",
                    "endDate",
                ],
                "notes": (
                    "If no limit is specified, the response will be limited to 50 "
                    "records."
                ),
            },
            "stats_leaders": {
                "url": "https://statsapi.mlb.com/api/{ver}/stats/leaders",
                "required_params": ["leaderCategories"],
                "all_params": [
                    "ver",
                    "leaderCategories",
                    "playerPool",
                    "leaderGameTypes",
                    "statGroup",
                    "season",
                    "leagueId",
                    "sportId",
                    "hydrate",
                    "limit",
                    "fields",
                    "statType",
                ],
                "notes": (
                    "If excluding season parameter to get all time leaders, include "
                    "statType=statsSingleSeason or you will likely not get any "
                    "results."
                ),
            },
            "teams": {
                "url": "https://statsapi.mlb.com/api/{ver}/teams",
                "required_params": [],
                "all_params": [
                    "ver",
                    "season",
                    "activeStatus",
                    "leagueIds",
                    "sportId",
                    "sportIds",
                    "gameType",
                    "hydrate",
                    "fields",
                ],
                "notes": None,
            },
            "team": {
                "url": "https://statsapi.mlb.com/api/{ver}/teams/{teamId}",
                "required_params": ["teamId"],
                "all_params": [
                    "ver",
                    "teamId",
                    "season",
                    "sportId",
                    "hydrate",
                    "fields",
                ],
                "notes": None,
            },
            "team_roster": {
                "url": "https://statsapi.mlb.com/api/{ver}/teams/{teamId}/roster",
                "required_params": ["teamId"],
                "all_params": [
                    "ver",
                    "teamId",
                    "rosterType",
                    "season",
                    "date",
                    "hydrate",
                    "fields",
                ],
                "notes": None,
            },
            "team_leaders": {
                "url": "https://statsapi.mlb.com/api/{ver}/teams/{teamId}/leaders",
                "required_params": ["teamId", "leaderCategories", "season"],
                "all_params": [
                    "ver",
                    "teamId",
                    "leaderCategories",
                    "season",
                    "leaderGameTypes",
                    "hydrate",
                    "limit",
                    "fields",
                ],
                "notes": None,
            },
            "venues": {
                "url": "https://statsapi.mlb.com/api/{ver}/venues",
                "required_params": ["venueIds"],
                "all_params": ["ver", "venueIds", "season", "hydrate", "fields"],
                "notes": None,
            },
        }

        logger.debug(
            f"Retrieved information for {len(endpoints)} MLB Stats API endpoints"
        )
        return {
            "endpoints": endpoints,
            "usage_note": (
                "Use these endpoints with the get_stats tool by specifying "
                "the endpoint name and required parameters"
            ),
            "example": {"endpoint": "teams", "params": {"sportId": 1}},
        }
    except Exception as e:
        error_msg = f"Error retrieving available endpoints information: {e!s}"
        logger.error(error_msg)
        return {"error": str(e)}


def main():
    """Initialize and run the MCP baseball server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
