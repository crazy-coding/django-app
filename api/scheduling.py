from datetime import datetime, timedelta
from itertools import combinations
import random
from django.utils import timezone
from .models import Game, Team, Season

def generate_fixtures(season, start_date=None, matchdays_interval=7):
    """
    Generate fixtures for a season using round-robin tournament scheduling.
    Each team plays against every other team twice (home and away).
    
    Args:
        season: Season object
        start_date: datetime object for the first match (defaults to season start date)
        matchdays_interval: days between each matchday (default 7 days)
    """
    if not start_date:
        start_date = season.start_date
    
    # Get all teams in the league
    teams = list(Team.objects.filter(league=season.league))
    if len(teams) % 2 != 0:
        raise ValueError("Need an even number of teams for scheduling")

    # First half of the season - each team plays against others once
    matches = []
    for home_team, away_team in combinations(teams, 2):
        matches.append((home_team, away_team))

    # Shuffle matches to make the schedule more random
    random.shuffle(matches)

    # Create fixtures with dates
    matchday = 0
    games_per_matchday = len(teams) // 2
    fixtures = []

    # First half of season
    for i in range(0, len(matches), games_per_matchday):
        matchday_games = matches[i:i + games_per_matchday]
        match_date = timezone.make_aware(datetime.combine(
            start_date + timedelta(days=matchday * matchdays_interval),
            datetime.min.time()
        ))
        
        for home, away in matchday_games:
            fixtures.append({
                'season': season,
                'home_team': home,
                'away_team': away,
                'played_at': match_date
            })
        matchday += 1

    # Second half of season (return fixtures)
    for fixture in fixtures.copy():
        return_date = timezone.make_aware(datetime.combine(
            start_date + timedelta(days=matchday * matchdays_interval),
            datetime.min.time()
        ))
        fixtures.append({
            'season': season,
            'home_team': fixture['away_team'],
            'away_team': fixture['home_team'],
            'played_at': return_date
        })
        if len(fixtures) % games_per_matchday == 0:
            matchday += 1

    # Bulk create all fixtures
    Game.objects.bulk_create([
        Game(**fixture) for fixture in fixtures
    ])