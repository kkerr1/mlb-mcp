"""
MCP server implementation for the baseball project with MLB Stats API integration.
"""

import os
import logging
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
        print(
            f"MLB Stats API logging configured at {log_level} level, writing to {log_file}"
        )
    else:
        # Stream handler if no log file is specified
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Add a message indicating where logs are being sent
        print(
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
        error_msg = f"Error accessing MLB Stats API endpoint {endpoint}: {str(e)}"
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
        # Pass parameters directly as keyword arguments
        kwargs = {}
        if date is not None:
            kwargs["date"] = date
        if team_id is not None:
            kwargs["team"] = team_id  # API expects 'team', not 'teamId'
        if sport_id != 1:
            kwargs["sportId"] = sport_id
        if game_type is not None:
            kwargs["gameType"] = game_type

        logger.debug(f"Retrieving schedule with params: {kwargs}")
        result = statsapi.schedule(**kwargs)
        logger.debug(f"Retrieved schedule data: {len(result)} game(s)")
        return result
    except Exception as e:
        error_msg = f"Error retrieving schedule: {str(e)}"
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
        # Call player_stat_data directly with keyword arguments
        kwargs = {
            "personId": player_id,
            "group": group,
            "type": stats,  # API expects 'type', not 'stats'
        }

        if season is not None:
            kwargs["season"] = season

        logger.debug(
            f"Retrieving player stats for player ID: {player_id}, group: {group}, type: {stats}"
        )
        result = statsapi.player_stat_data(**kwargs)
        logger.debug(f"Retrieved stats for player ID: {player_id}")
        return result
    except Exception as e:
        error_msg = f"Error retrieving player stats for player ID {player_id}: {str(e)}"
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
        # Call standings_data directly with keyword arguments
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
        error_msg = f"Error retrieving standings: {str(e)}"
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
        # Prepare parameters for logging
        params = {
            "team_id": team_id,
            "leader_category": leader_category,
            "season": season,
            "limit": 10 if limit is None else limit,
        }

        logger.debug(
            f"Retrieving team leaders for team ID: {team_id}, category: {leader_category}"
        )

        # Call the formatted leaders function that returns more detailed data
        leaders_text = statsapi.team_leaders(
            team_id,
            leader_category,
            limit=10 if limit is None else limit,
            season=season,
        )

        logger.debug(f"Retrieved team leaders data for team ID: {team_id}")

        # Convert the text response to a more structured format
        return {
            "teamId": team_id,
            "leaderCategory": leader_category,
            "season": season,
            "results": leaders_text,
            "teamLeaders": True,  # Flag to indicate this contains team leaders
        }
    except Exception as e:
        error_msg = f"Error retrieving team leaders for team ID {team_id}: {str(e)}"
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
        # lookup_player takes name as a direct argument
        result = statsapi.lookup_player(name)

        if result:
            logger.debug(f"Found {len(result)} player(s) matching: {name}")
        else:
            logger.info(f"No players found matching: {name}")

        # Return with a "people" key for consistency
        return {"people": result}
    except Exception as e:
        error_msg = f"Error looking up player {name}: {str(e)}"
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
        error_msg = f"Error retrieving boxscore for game ID {game_id}: {str(e)}"
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
        # Pass parameters directly as keyword arguments
        kwargs = {"sportId": 1}  # Set default sportId

        if season is not None:
            kwargs["season"] = season
        if team_id is not None:
            kwargs["teamId"] = team_id

        logger.debug(f"Retrieving game pace data with params: {kwargs}")
        result = statsapi.game_pace_data(**kwargs)

        # Log more detailed information about what was retrieved
        season_txt = f"season {season}" if season else "current season"
        team_txt = f"team ID {team_id}" if team_id else "all teams"
        logger.debug(f"Retrieved game pace data for {season_txt}, {team_txt}")

        return result
    except Exception as e:
        error_msg = f"Error retrieving game pace data: {str(e)}"
        logger.error(error_msg)
        return {"error": str(e), "params_sent": kwargs}


def main():
    """Initialize and run the MCP baseball server."""
    # Log startup information
    log_level = os.environ.get("MLB_STATS_LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("MLB_STATS_LOG_FILE", "stdout")
    logger.info(
        f"Starting MLB Stats MCP server with logging level: {log_level}, output: {log_file}"
    )

    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
