from rest_framework import serializers
from .models import League, Season, Team, Game, LeagueStanding, Player, Goal
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'nationality', 'birth_date', 'height', 'weight', 'created_at']


class GoalSerializer(serializers.ModelSerializer):
    scorer = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all())
    assistant = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Goal
        fields = ['id', 'game', 'scorer', 'assistant', 'minute', 'is_penalty', 'is_own_goal', 'created_at']


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'name', 'country', 'created_at']


class SeasonSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    league_id = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(),
        source='league',
        write_only=True
    )

    class Meta:
        model = Season
        fields = ['id', 'name', 'league', 'league_id', 'is_active', 'start_date', 'end_date', 'created_at']


class TeamSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    league_id = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(),
        source='league',
        write_only=True
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'league', 'league_id', 'short_name', 'founded_year', 'created_at']


class GameSerializer(serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True)
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True
    )
    home_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='home_team',
        write_only=True
    )
    away_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='away_team',
        write_only=True
    )
    winner_id = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'id', 'season', 'season_id',
            'home_team', 'home_team_id', 'away_team', 'away_team_id',
            'home_score', 'away_score', 'played_at', 'created_at',
            'winner_id'
        ]

    def get_winner_id(self, obj):
        winner = obj.winner()
        return winner.id if winner else None


class LeagueStandingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    season = SeasonSerializer(read_only=True)

    class Meta:
        model = LeagueStanding
        fields = [
            'id', 'season', 'team', 'position',
            'played', 'won', 'drawn', 'lost',
            'goals_for', 'goals_against', 'goal_difference',
            'points', 'last_updated'
        ]
