from django.db import models
from django.db.models import Q, Sum, Count, F
from django.core.validators import MinValueValidator
from django.utils import timezone


class League(models.Model):
    name = models.CharField(max_length=200, unique=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.country})"


class Season(models.Model):
    league = models.ForeignKey(League, related_name='seasons', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)  # e.g., "2025-2026"
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['league', 'name']

    def __str__(self):
        return f"{self.league.name} - {self.name}"
    
    def get_top_scorers(self, limit=10):
        """Get the top scorers for this season."""
        return Player.objects.filter(goals__game__season=self).annotate(
            goals_scored=Count('goals')
        ).order_by('-goals_scored')[:limit]
    
    def get_top_assisters(self, limit=10):
        """Get the top assisters for this season."""
        return Player.objects.filter(assists__game__season=self).annotate(
            total_assists=Count('assists')
        ).order_by('-total_assists')[:limit]


class Team(models.Model):
    name = models.CharField(max_length=200)
    league = models.ForeignKey(League, related_name='teams', on_delete=models.CASCADE)
    short_name = models.CharField(max_length=3, help_text="Three letter code", null=True)
    founded_year = models.IntegerField(null=True, blank=True)
    players = models.ManyToManyField('Player', through='PlayerContract', related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['league', 'name']

    def __str__(self):
        return f"{self.name} ({self.league.name})"
    
    def get_current_squad(self):
        """Get current squad sorted by position."""
        return self.players.filter(
            contracts__start_date__lte=timezone.now(),
            contracts__end_date__gte=timezone.now()
        ).order_by('position')
    
    def get_season_stats(self, season):
        """Get team's statistics for a specific season."""
        home_games = Game.objects.filter(season=season, home_team=self)
        away_games = Game.objects.filter(season=season, away_team=self)
        
        stats = {
            'played': home_games.count() + away_games.count(),
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'goals_for': 0,
            'goals_against': 0,
            'points': 0
        }
        
        # Home games
        for game in home_games:
            if game.home_score is not None and game.away_score is not None:
                stats['goals_for'] += game.home_score
                stats['goals_against'] += game.away_score
                if game.home_score > game.away_score:
                    stats['won'] += 1
                    stats['points'] += 3
                elif game.home_score == game.away_score:
                    stats['drawn'] += 1
                    stats['points'] += 1
                else:
                    stats['lost'] += 1
        
        # Away games
        for game in away_games:
            if game.home_score is not None and game.away_score is not None:
                stats['goals_for'] += game.away_score
                stats['goals_against'] += game.home_score
                if game.away_score > game.home_score:
                    stats['won'] += 1
                    stats['points'] += 3
                elif game.home_score == game.away_score:
                    stats['drawn'] += 1
                    stats['points'] += 1
                else:
                    stats['lost'] += 1
        
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        return stats


class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]

    name = models.CharField(max_length=200)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    nationality = models.CharField(max_length=100)
    birth_date = models.DateField()
    height = models.IntegerField(help_text="Height in cm", null=True, blank=True)
    weight = models.IntegerField(help_text="Weight in kg", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_current_team(self):
        """Get the player's current team."""
        current_contract = self.contracts.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        return current_contract.team if current_contract else None

    def get_season_stats(self, season):
        """Get player's statistics for a specific season."""
        games_played = Game.objects.filter(
            Q(home_team_players=self) | Q(away_team_players=self),
            season=season
        ).count()

        goals = Goal.objects.filter(
            scorer=self,
            game__season=season
        ).count()

        assists = Goal.objects.filter(
            assistant=self,
            game__season=season
        ).count()

        return {
            'games_played': games_played,
            'goals': goals,
            'assists': assists,
        }


class PlayerContract(models.Model):
    """Track player contracts and transfers between teams."""
    player = models.ForeignKey(Player, related_name='contracts', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='contracts', on_delete=models.CASCADE)
    number = models.IntegerField(help_text="Squad number")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.player.name} at {self.team.name} ({self.start_date} to {self.end_date})"


class Game(models.Model):
    season = models.ForeignKey(Season, related_name='games', on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home_games', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_games', on_delete=models.CASCADE)
    home_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    away_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    played_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Match squads
    home_team_players = models.ManyToManyField(Player, related_name='home_games_played')
    away_team_players = models.ManyToManyField(Player, related_name='away_games_played')

    class Meta:
        ordering = ['-played_at', '-created_at']

    def __str__(self):
        scores = f"{self.home_score}-{self.away_score}" if self.home_score is not None else "TBD"
        return f"{self.home_team} vs {self.away_team} ({scores})"

    def save(self, *args, **kwargs):
        # Ensure teams are from the same league
        if self.home_team.league != self.away_team.league:
            raise ValueError("Teams must be from the same league")
        # Ensure the game is in a season for the correct league
        if self.season.league != self.home_team.league:
            raise ValueError("Game season must match teams' league")
        super().save(*args, **kwargs)

    def winner(self):
        """Return the winning team, or None if draw/not played."""
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return None

    def get_goals(self):
        """Get all goals for this game in chronological order."""
        return self.goals.all().order_by('minute')


class Goal(models.Model):
    game = models.ForeignKey(Game, related_name='goals', on_delete=models.CASCADE)
    scorer = models.ForeignKey(Player, related_name='goals', on_delete=models.CASCADE)
    assistant = models.ForeignKey(Player, related_name='assists', on_delete=models.CASCADE, null=True, blank=True)
    minute = models.IntegerField(validators=[MinValueValidator(0)])
    is_penalty = models.BooleanField(default=False)
    is_own_goal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['game', 'minute']

    def __str__(self):
        goal_type = ""
        if self.is_penalty:
            goal_type = " (P)"
        elif self.is_own_goal:
            goal_type = " (OG)"
        
        assist_text = f", assist by {self.assistant.name}" if self.assistant else ""
        return f"{self.scorer.name}{goal_type} {self.minute}'{assist_text}"


class LeagueStanding(models.Model):
    """Cached standings for quick access to league tables."""
    season = models.ForeignKey(Season, related_name='standings', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='standings', on_delete=models.CASCADE)
    position = models.IntegerField()
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    home_wins = models.IntegerField(default=0)
    home_draws = models.IntegerField(default=0)
    home_losses = models.IntegerField(default=0)
    away_wins = models.IntegerField(default=0)
    away_draws = models.IntegerField(default=0)
    away_losses = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    failed_to_score = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-points', '-goal_difference', '-goals_for', 'team__name']
        unique_together = ['season', 'team']

    def __str__(self):
        return f"{self.team.name} - {self.season.name} ({self.points} pts)"

    @classmethod
    def update_standings(cls, season):
        """Update standings for all teams in a season."""
        # Clear existing standings
        cls.objects.filter(season=season).delete()
        
        # Get all teams in the league
        teams = Team.objects.filter(league=season.league)
        
        # Calculate standings for each team
        standings = []
        for position, team in enumerate(teams, 1):
            # Get home games
            home_games = Game.objects.filter(
                season=season,
                home_team=team,
                home_score__isnull=False,
                away_score__isnull=False
            )
            
            # Get away games
            away_games = Game.objects.filter(
                season=season,
                away_team=team,
                home_score__isnull=False,
                away_score__isnull=False
            )
            
            # Initialize stats
            stats = {
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'goals_for': 0,
                'goals_against': 0,
                'points': 0,
                'home_wins': 0,
                'home_draws': 0,
                'home_losses': 0,
                'away_wins': 0,
                'away_draws': 0,
                'away_losses': 0,
                'clean_sheets': 0,
                'failed_to_score': 0
            }
            
            # Calculate home game stats
            for game in home_games:
                stats['played'] += 1
                stats['goals_for'] += game.home_score
                stats['goals_against'] += game.away_score
                
                if game.home_score > game.away_score:
                    stats['won'] += 1
                    stats['home_wins'] += 1
                    stats['points'] += 3
                elif game.home_score == game.away_score:
                    stats['drawn'] += 1
                    stats['home_draws'] += 1
                    stats['points'] += 1
                else:
                    stats['lost'] += 1
                    stats['home_losses'] += 1
                
                if game.away_score == 0:
                    stats['clean_sheets'] += 1
                if game.home_score == 0:
                    stats['failed_to_score'] += 1
            
            # Calculate away game stats
            for game in away_games:
                stats['played'] += 1
                stats['goals_for'] += game.away_score
                stats['goals_against'] += game.home_score
                
                if game.away_score > game.home_score:
                    stats['won'] += 1
                    stats['away_wins'] += 1
                    stats['points'] += 3
                elif game.home_score == game.away_score:
                    stats['drawn'] += 1
                    stats['away_draws'] += 1
                    stats['points'] += 1
                else:
                    stats['lost'] += 1
                    stats['away_losses'] += 1
                
                if game.home_score == 0:
                    stats['clean_sheets'] += 1
                if game.away_score == 0:
                    stats['failed_to_score'] += 1
            
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
            
            standing = cls(
                season=season,
                team=team,
                position=position,
                played=stats['played'],
                won=stats['won'],
                drawn=stats['drawn'],
                lost=stats['lost'],
                goals_for=stats['goals_for'],
                goals_against=stats['goals_against'],
                goal_difference=stats['goal_difference'],
                points=stats['points'],
                home_wins=stats['home_wins'],
                home_draws=stats['home_draws'],
                home_losses=stats['home_losses'],
                away_wins=stats['away_wins'],
                away_draws=stats['away_draws'],
                away_losses=stats['away_losses'],
                clean_sheets=stats['clean_sheets'],
                failed_to_score=stats['failed_to_score']
            )
            standings.append(standing)
        
        # Sort by points, goal difference, goals scored
        standings.sort(key=lambda s: (-s.points, -s.goal_difference, -s.goals_for))
        
        # Update positions and save
        for position, standing in enumerate(standings, 1):
            standing.position = position
            standing.save()
