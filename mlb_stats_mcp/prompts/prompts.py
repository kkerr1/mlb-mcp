"""
MCP prompt functions for the baseball server.
These prompts provide structured templates to guide LLM interactions.
"""

from typing import Optional


def player_report(player_name: str, season: Optional[int] = None) -> str:
    """
    Generate a comprehensive player performance report with statistics and visualizations.

    Args:
        player_name: Full name or partial name of the player
        season: Season year (defaults to current season if not specified)

    Returns:
        Detailed prompt instructing the LLM how to create a comprehensive player report
    """
    season_text = f"the {season} season" if season else "the current/most recent season"

    return f"""Create a comprehensive performance report for {player_name} for {season_text}.

STEP 1: PLAYER IDENTIFICATION & BASIC INFO
1. Use lookup_player("{player_name}") to find the player and get their MLB ID
2. If multiple players are found, select the most relevant/current one
3. Use get_playerid_lookup() if needed for additional player identification

STEP 2: DETERMINE PLAYER TYPE & GET CORE STATS
1. Use get_player_stats(player_id, group="hitting") to get batting stats
2. Use get_player_stats(player_id, group="pitching") to get pitching stats
3. Based on which stats are more relevant, determine if this is primarily a:
   - BATTER: Focus on hitting stats, batting visualizations
   - PITCHER: Focus on pitching stats, pitcher visualizations
   - TWO-WAY PLAYER: Include both hitting and pitching analysis

STEP 3: GET ADVANCED METRICS (STATCAST DATA)
For BATTERS:
- get_statcast_batter_data(player_id{
        ', start_dt="' + str(season) + '-01-01", end_dt="' + str(season) + '-12-31"'
        if season
        else ""
    })
- get_statcast_batter_expected_stats({season if season else "current_year"})
- get_statcast_batter_percentile_ranks({season if season else "current_year"})
- **get_statcast_batter_exitvelo_barrels({
        season if season else "current_year"
    }) - IMPORTANT for exit velocity analysis**

For PITCHERS:
- get_statcast_pitcher_data(player_id{
        ', start_dt="' + str(season) + '-01-01", end_dt="' + str(season) + '-12-31"'
        if season
        else ""
    })
- get_statcast_pitcher_expected_stats({season if season else "current_year"})
- get_statcast_pitcher_percentile_ranks({season if season else "current_year"})
- **get_statcast_pitcher_exitvelo_barrels({
        season if season else "current_year"
    }) - IMPORTANT for exit velocity allowed analysis**

STEP 4: CREATE VISUALIZATIONS
For BATTERS - Create these plots using the statcast data:
1. create_strike_zone_plot(statcast_data, title="{
        player_name
    } Strike Zone Profile", colorby="events")
2. create_spraychart_plot(statcast_data, title="{player_name} Spray Chart", colorby="events")
3. create_bb_profile_plot(statcast_data, parameter="launch_angle")
4. **create_bb_profile_plot(statcast_data, parameter="exit_velocity") - 
    NEW: Exit velocity distribution**

For PITCHERS - Create these plots using the statcast data:
1. create_strike_zone_plot(statcast_data, title="{
        player_name
    } Pitch Locations", colorby="pitch_type")
2. create_bb_profile_plot(statcast_data, parameter="release_speed")
3. **create_bb_profile_plot(statcast_data, parameter="exit_velocity") - 
    NEW: Exit velocity allowed distribution**

STEP 5: GET CONTEXTUAL DATA
1. Use get_team_roster() to find what team the player is currently on
2. Use get_standings() to see how their team is performing
3. Use get_league_leader_data() to compare player against league leaders in relevant categories

STEP 6: CREATE HTML REPORT
Generate a comprehensive HTML report with the following structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{player_name} Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white; 
            padding: 20px; 
            border-radius: 10px; 
        }}
        .header {{ 
            text-align: center; 
            border-bottom: 3px solid #003366; 
            padding-bottom: 20px; 
            margin-bottom: 30px; 
        }}
        .section {{ margin-bottom: 30px; }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
            }}
        .stat-card {{ 
            background-color: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center; 
            }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #003366; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .exitvelo-highlight {{ 
            background-color: #fff3cd; 
            border: 2px solid #ffc107; 
            }}
        .barrel-highlight {{ 
            background-color: #d1ecf1; 
            border: 2px solid #17a2b8; 
            }}
        .plot-container {{ text-align: center; margin: 20px 0; }}
        .plot-container img {{ 
            max-width: 100%; 
            height: auto; 
            border: 1px solid #ddd;
            border-radius: 8px; 
            }}
        .highlights {{ background-color: #e7f3ff; padding: 15px; border-radius: 8px; }}
        .analysis {{ background-color: #fff3e0; padding: 15px; border-radius: 8px; }}
        .exitvelo-section {{ 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid #ffc107; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{player_name} Performance Report</h1>
            <h3>{season_text}</h3>
        </div>
        
        <div class="section">
            <h2>Player Overview</h2>
            <!-- Include basic player info, team, position, etc. -->
        </div>
        
        <div class="section">
            <h2>Key Statistics</h2>
            <div class="stats-grid">
                <!-- Create stat cards for key metrics based on player type -->
                <div class="stat-card">
                    <div class="stat-value">[VALUE]</div>
                    <div class="stat-label">[STAT NAME]</div>
                </div>
                <!-- REQUIRED: Include these exit velocity stats with special highlighting -->
                <div class="stat-card exitvelo-highlight">
                    <div class="stat-value">[AVG_EXIT_VELO]</div>
                    <div class="stat-label">Average Exit Velocity</div>
                </div>
                <div class="stat-card exitvelo-highlight">
                    <div class="stat-value">[MAX_EXIT_VELO]</div>
                    <div class="stat-label">Max Exit Velocity</div>
                </div>
                <div class="stat-card barrel-highlight">
                    <div class="stat-value">[BARREL_RATE]</div>
                    <div class="stat-label">Barrel Rate</div>
                </div>
                <div class="stat-card barrel-highlight">
                    <div class="stat-value">[HARD_HIT_RATE]</div>
                    <div class="stat-label">Hard Hit Rate (95+ mph)</div>
                </div>
                <!-- Repeat for other key stats -->
            </div>
        </div>
        
        <div class="section exitvelo-section">
            <h2>Exit Velocity & Batted Ball Analysis</h2>
            <div class="stats-grid">
                <!-- Include comprehensive exit velocity metrics -->
                <div class="stat-card">
                    <div class="stat-value">[EV_50TH_PERCENTILE]</div>
                    <div class="stat-label">50th Percentile EV</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">[EV_90TH_PERCENTILE]</div>
                    <div class="stat-label">90th Percentile EV</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">[SWEET_SPOT_RATE]</div>
                    <div class="stat-label">Sweet Spot Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">[SOLID_CONTACT_RATE]</div>
                    <div class="stat-label">Solid Contact Rate</div>
                </div>
            </div>
            <p><strong>Analysis:</strong> Compare these exit velocity metrics to league averages and 
            explain what they indicate about the player's contact quality and power potential.</p>
        </div>
        
        <div class="section">
            <h2>Performance Visualizations</h2>
            <!-- Include all generated plots as base64 images -->
            <div class="plot-container">
                <h3>[Plot Title]</h3>
                <img src="data:image/png;base64,[BASE64_IMAGE_DATA]" alt="[Plot Description]">
                <p>[Brief description of what the plot shows]</p>
            </div>
            <!-- REQUIRED: Include exit velocity distribution plot -->
            <div class="plot-container">
                <h3>{player_name} Exit Velocity Distribution</h3>
                <img 
                    src="data:image/png;base64,[EXIT_VELO_PLOT_BASE64]" 
                    alt="Exit Velocity Distribution"
                >
                <p>
                    This chart shows the distribution of exit velocities for all batted balls, 
                    highlighting the player's ability to make hard contact consistently.
                </p>
            </div>
            <!-- Repeat for each visualization -->
        </div>
        
        <div class="section highlights">
            <h2>Season Highlights</h2>
            <!-- Include notable achievements, career highs, exit velocity milestones, etc. -->
            <h3>Exit Velocity Milestones</h3>
            <ul>
                <li>Hardest hit ball: [MAX_EV] mph on [DATE]</li>
                <li>Number of 110+ mph batted balls: [COUNT]</li>
                <li>Ranking in league average exit velocity: [RANKING]</li>
            </ul>
        </div>
        
        <div class="section analysis">
            <h2>Performance Analysis</h2>
            <!-- Include detailed analysis focusing heavily on exit velocity insights -->
            <h3>Contact Quality Assessment</h3>
            <p><strong>Exit Velocity Analysis:</strong> Analyze the player's exit velocity data in 
            context of:</p>
            <ul>
                <li>League average comparisons (avg EV, hard hit rate, barrel rate)</li>
                <li>Consistency of hard contact (90th percentile vs average)</li>
                <li>Power potential based on max exit velocity</li>
                <li>Sweet spot contact percentage and its relationship to production</li>
                <li>Trends in exit velocity throughout the season</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>League Context</h2>
            <!-- Compare player to league averages and leaders, emphasizing exit velocity rankings 
                -->
            <h3>Exit Velocity League Rankings</h3>
            <p>Show where the player ranks among qualified hitters in:</p>
            <ul>
                <li>Average Exit Velocity</li>
                <li>90th Percentile Exit Velocity</li>
                <li>Barrel Rate</li>
                <li>Hard Hit Rate</li>
            </ul>
        </div>
    </div>
</body>
</html>
```

IMPORTANT NOTES FOR BASE64 IMAGES:
- All plot functions return a dictionary with a 'base64' key containing the image data
- Use this format in HTML: 
    <img src="data:image/png;base64,{{plot_result['base64']}}" alt="Plot Description">
- Include descriptive alt text for each image
- Add brief explanations under each plot about what insights it provides

**EXIT VELOCITY ANALYSIS GUIDELINES:**
- **ALWAYS** retrieve and analyze exit velocity data using get_statcast_batter_exitvelo_barrels() or 
    get_statcast_pitcher_exitvelo_barrels()
- Compare the player's exit velocity metrics to league averages:
  - Average Exit Velocity (league avg ~89 mph)
  - 90th Percentile Exit Velocity (elite is 105+ mph)
  - Hard Hit Rate (95+ mph) - league avg ~35%
  - Barrel Rate (optimal combination of exit velo + launch angle) - league avg ~6%
- **Key Exit Velocity Metrics to Highlight:**
  - avg_hit_speed: Overall exit velocity average
  - max_hit_speed: Hardest contact made
  - ev50: 50th percentile exit velocity
  - ev95: 95th percentile exit velocity  
  - barrel_batted_rate: Percentage of batted balls that are "barrels"
  - solidcontact_percent: Rate of solid contact
  - flareburner_percent: Rate of weak contact
  - sweetspot_percent: Launch angle between 8-32 degrees

ANALYSIS GUIDELINES:
- **Prioritize exit velocity analysis** 
    - this is now the primary focus for contact quality assessment
- Compare current season performance to career averages where possible
- Identify strengths and areas for improvement based on exit velocity data
- Note any significant trends or changes in exit velocity throughout the season
- Put performance in context of team success and league standards
- For batters: Focus on contact quality (exit velo), power (barrels), plate discipline
- For pitchers: Focus on limiting hard contact, command, stuff quality
- **Always include exit velocity in the "strengths" or "areas for improvement" sections**

Generate a complete HTML report that baseball analysts and fans would find 
comprehensive and insightful, with special emphasis on exit velocity analysis."""


def team_comparison(team1: str, team2: str, focus_area: str = "overall") -> str:
    """
    Generate a comprehensive comparison between two MLB teams.

    Args:
        team1: First team abbreviation (e.g., "NYY", "BOS")
        team2: Second team abbreviation
        focus_area: Area to focus on ("overall", "hitting", "pitching", "recent")

    Returns:
        Prompt for detailed team comparison analysis
    """
    return f"""Create a comprehensive comparison between {team1} and {team2}
        with focus on {focus_area}.

STEP 1: BASIC TEAM INFO
1. Use get_standings() to get current records and division standings for both teams
2. Use get_schedule() to find recent head-to-head matchups this season
3. Get team rosters with get_team_roster() for both teams

STEP 2: STATISTICAL COMPARISON
Based on focus area "{focus_area}":

If "hitting" or "overall":
- get_team_batting(current_season) for both teams
- get_team_leaders() for key offensive categories (homeRuns, rbi, battingAverage, onBasePercentage)

If "pitching" or "overall":  
- get_team_pitching(current_season) for both teams
- get_team_leaders() for key pitching categories (earnedRunAverage, wins, strikeouts, saves)

If "recent":
- get_schedule() for last 10-15 games for each team
- Focus on recent performance trends

STEP 3: ADVANCED METRICS
- Get league-wide data using get_statcast_batter_expected_stats() and 
get_statcast_pitcher_expected_stats()
- Compare team averages to league benchmarks

STEP 4: CREATE VISUALIZATIONS
Use create_teams_plot() to generate comparison charts:
1. Team offensive comparison (if hitting focus)
2. Team pitching comparison (if pitching focus)
3. Overall team performance scatter plot

STEP 5: HEAD-TO-HEAD ANALYSIS
- Historical matchup data
- Key player matchups
- Recent series results

STEP 6: GENERATE HTML REPORT
Create detailed comparison report with team logos, stats tables, and visual comparisons.

Focus on identifying competitive advantages, key matchups, and prediction factors."""


def game_recap(game_id: int) -> str:
    """
    Generate a comprehensive game recap with statistics and key moments.

    Args:
        game_id: MLB game ID

    Returns:
        Prompt for detailed game recap generation
    """
    return f"""Create a comprehensive recap for game {game_id}.

STEP 1: BASIC GAME INFORMATION
1. get_boxscore({game_id}) - Get final score, basic stats, and game summary
2. get_linescore({game_id}) - Get inning-by-inning scoring breakdown
3. get_game_scoring_play_data({game_id}) - Get detailed scoring plays and key moments

STEP 2: ADVANCED GAME DATA
1. get_statcast_single_game({game_id}) - Get pitch-level data for the entire game
2. get_game_highlight_data({game_id}) - Get video highlights and notable plays

STEP 3: KEY PLAYER PERFORMANCES
- Identify standout hitting and pitching performances from boxscore
- Use statcast data to analyze quality of contact, pitch effectiveness
- Highlight clutch moments and game-changing plays

STEP 4: VISUALIZATIONS
Using the statcast game data:
1. create_strike_zone_plot() for key pitchers' locations
2. create_spraychart_plot() for notable hits/home runs
3. create_bb_profile_plot() for batted ball analysis

STEP 5: GENERATE HTML GAME RECAP
Create detailed HTML report including:
- Game summary header with final score
- Inning-by-inning scoring summary
- Key player stat lines
- Turning point analysis
- Visual breakdowns of key moments
- Post-game implications (standings, playoff picture, etc.)

Structure the recap like a professional sports article with data-driven insights."""


def statistical_deep_dive(
    stat_category: str, season: Optional[int] = None, min_qualifier: Optional[int] = None
) -> str:
    """
    Generate an in-depth statistical analysis for a specific category.

    Args:
        stat_category: Statistical category to analyze (e.g., "home_runs", "era", "steals")
        season: Season to analyze (current if not specified)
        min_qualifier: Minimum qualifying threshold

    Returns:
        Prompt for comprehensive statistical analysis
    """
    season_text = f"{season}" if season else "current season"

    return f"""Create a comprehensive statistical deep dive analysis for {stat_category} 
in the {season_text}.

STEP 1: GATHER LEAGUE-WIDE DATA
1. get_league_leader_data("{stat_category}", season={season or "current"}, limit=50)
2. Get appropriate team-level data using get_team_batting() or get_team_pitching()
3. Use get_statcast_batter_expected_stats() or get_statcast_pitcher_expected_stats() for advanced 
context

STEP 2: IDENTIFY KEY INSIGHTS
- Current leaders and their performance levels
- Historical context (how does this season compare?)
- Team-by-team breakdowns
- Notable trends or surprises

STEP 3: ADVANCED ANALYSIS
- Correlation with other statistics
- Expected vs actual performance (using statcast expected stats)
- Impact on team success
- Predictive indicators

STEP 4: VISUALIZATIONS
Create relevant plots based on the statistic:
- Distribution charts
- Team comparison plots using create_teams_plot()
- Player-specific visualizations for top performers

STEP 5: GENERATE COMPREHENSIVE REPORT
HTML format with:
- Executive summary of key findings
- Top 10 leaderboard with context
- Team rankings and analysis
- Historical perspective
- Statistical correlations and insights
- Predictions and trends to watch

Make it suitable for both casual fans and serious analysts."""
