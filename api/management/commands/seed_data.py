from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from api.models import League, Season, Team, Game, Player, PlayerContract, Goal, LeagueStanding
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample data for leagues, seasons, teams, and games'

    def add_arguments(self, parser):
        parser.add_argument(
            '--league',
            type=str,
            help='League name to create',
            default="Premier League"
        )
        parser.add_argument(
            '--teams',
            type=int,
            help='Number of teams to create',
            default=20
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create league
        league = League.objects.create(
            name=options['league'],
            country='England',
            founded_date=timezone.now()
        )
        
        # Create season
        season = Season.objects.create(
            name=f"{timezone.now().year}/{timezone.now().year + 1}",
            league=league,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=300),
            is_active=True
        )

        # Create teams
        teams = []
        for i in range(options['teams']):
            team = Team.objects.create(
                name=f"Team {i+1}",
                country='England',
                founded_date=timezone.now(),
                league=league
            )
            teams.append(team)

        # Create players for each team
        for team in teams:
            for i in range(20):  # 20 players per team
                player = Player.objects.create(
                    name=f"Player {i+1} - {team.name}",
                    nationality='England',
                    birth_date=timezone.now() - timedelta(days=365*random.randint(20, 35))
                )
                PlayerContract.objects.create(
                    player=player,
                    team=team,
                    start_date=season.start_date,
                    jersey_number=i+1
                )

        # Generate fixtures
        all_teams = list(teams)
        num_teams = len(all_teams)
        games_per_round = num_teams // 2
        rounds = num_teams - 1

        game_date = season.start_date
        for round in range(rounds):
            # Generate matches for this round
            for i in range(games_per_round):
                home_team = all_teams[i]
                away_team = all_teams[-1-i]
                if home_team != away_team:
                    game = Game.objects.create(
                        season=season,
                        home_team=home_team,
                        away_team=away_team,
                        played_at=game_date,
                        home_score=random.randint(0, 5) if game_date < timezone.now() else None,
                        away_score=random.randint(0, 5) if game_date < timezone.now() else None
                    )
                    
                    # Add some goals for completed games
                    if game.home_score is not None:
                        home_players = PlayerContract.objects.filter(team=home_team)
                        away_players = PlayerContract.objects.filter(team=away_team)
                        
                        for _ in range(game.home_score):
                            Goal.objects.create(
                                game=game,
                                player=random.choice(home_players).player,
                                minute=random.randint(1, 90)
                            )
                        
                        for _ in range(game.away_score):
                            Goal.objects.create(
                                game=game,
                                player=random.choice(away_players).player,
                                minute=random.randint(1, 90)
                            )

            game_date += timedelta(days=7)  # Next week's games
            
            # Rotate teams for next round (keep first team fixed)
            all_teams.insert(1, all_teams.pop())

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))