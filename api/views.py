from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count
from django.db.models import Q, Sum, Prefetch
from .models import (
    League, Season, Team, Game, LeagueStanding,
    Player, PlayerContract, Goal
)
from .serializers import (
    LeagueSerializer, SeasonSerializer, TeamSerializer,
    GameSerializer, LeagueStandingSerializer
)
from .serializers import UserSerializer
from django.contrib.auth.models import User
from .forms import (
    LeagueForm, SeasonForm, TeamForm, GameForm,
    PlayerForm, PlayerContractForm, GoalForm
)
from django.urls import reverse
from django.shortcuts import get_object_or_404


def index(request):
    """Redirect to the dashboard view."""
    return redirect('dashboard')


def dashboard(request):
    """Dashboard view showing league standings and recent games."""
    # Get the first league (in a real app, you'd select based on user preference)
    league = League.objects.first()
    if not league:
        return render(request, 'dashboard.html', {'error': 'No leagues found'})

    # Get active season
    season = league.seasons.filter(is_active=True).first()
    if not season:
        return render(request, 'dashboard.html', {'error': 'No active season found'})

    # Get standings
    standings = LeagueStanding.objects.filter(season=season)

    # Get recent and upcoming games
    now = timezone.now()
    recent_games = Game.objects.filter(
        season=season,
        played_at__lt=now,
        home_score__isnull=False
    ).order_by('-played_at')[:5]

    upcoming_games = Game.objects.filter(
        season=season,
        played_at__gt=now
    ).order_by('played_at')[:5]

    # Get next matchday games
    next_matchday_date = upcoming_games.first().played_at.date() if upcoming_games.exists() else None
    next_matchday_games = []
    if next_matchday_date:
        next_matchday_games = Game.objects.filter(
            season=season,
            played_at__date=next_matchday_date
        ).order_by('played_at')

    # Calculate form table (last 5 games)
    form_data = []
    for standing in standings:
        team_games = Game.objects.filter(
            Q(home_team=standing.team) | Q(away_team=standing.team),
            season=season,
            played_at__lt=now,
            home_score__isnull=False
        ).order_by('-played_at')[:5]

        form = []
        for game in team_games:
            if game.home_team == standing.team:
                if game.home_score > game.away_score:
                    form.append('W')
                elif game.home_score < game.away_score:
                    form.append('L')
                else:
                    form.append('D')
            else:
                if game.away_score > game.home_score:
                    form.append('W')
                elif game.away_score < game.home_score:
                    form.append('L')
                else:
                    form.append('D')
        
        form_data.append({
            'team': standing.team,
            'form': form[::-1]  # Reverse to show oldest to newest
        })

    # Calculate top scorers and assisters
    top_scorers = Player.objects.filter(
        goals__game__season=season
    ).annotate(
        goals_count=Count('goals')
    ).order_by('-goals_count')[:5]
    
    # Get top assisters
    top_assisters = Player.objects.filter(
        assists__game__season=season
    ).annotate(
        assists_count=Count('assists')
    ).order_by('-assists_count')[:5]

    # League level statistics
    games_qs = Game.objects.filter(season=season, home_score__isnull=False, away_score__isnull=False)
    total_games = games_qs.count()
    agg = games_qs.aggregate(total_home=Sum('home_score'), total_away=Sum('away_score'))
    total_goals = (agg.get('total_home') or 0) + (agg.get('total_away') or 0)
    avg_goals_per_game = (total_goals / total_games) if total_games else 0
    # total clean sheets across teams (sum of standing clean_sheets)
    total_clean_sheets = sum([s.clean_sheets for s in standings]) if standings else 0

    context = {
        'league': league,
        'season': season,
        'standings': standings,
        'recent_games': recent_games,
        'upcoming_games': upcoming_games,
        'next_matchday_games': next_matchday_games,
        'next_matchday_date': next_matchday_date,
        'form_data': form_data,
        'top_scorers': [{'player': p, 'goals': p.goals_count} for p in top_scorers],
        'top_assisters': [{'player': p, 'assists': p.assists_count} for p in top_assisters],
        'league_stats': {
            'total_games': total_games,
            'total_goals': total_goals,
            'avg_goals_per_game': avg_goals_per_game,
            'total_clean_sheets': total_clean_sheets,
        },
    }
    return render(request, 'dashboard.html', context)


def add_league(request):
    if request.method == 'POST':
        form = LeagueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = LeagueForm()
    return render(request, 'forms/add_league.html', {'form': form, 'title': 'Add League'})


def add_season(request):
    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SeasonForm()
    return render(request, 'forms/add_season.html', {'form': form, 'title': 'Add Season'})


def add_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TeamForm()
    return render(request, 'forms/add_team.html', {'form': form, 'title': 'Add Team'})


def add_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            # update standings for that season
            season = form.cleaned_data.get('season')
            LeagueStanding.update_standings(season)
            return redirect('list_games')
    else:
        form = GameForm()
    return render(request, 'forms/add_game.html', {'form': form, 'title': 'Add Game'})


# List views
def list_leagues(request):
    leagues = League.objects.all().order_by('name')
    return render(request, 'lists/league_list.html', {'leagues': leagues, 'title': 'Leagues'})


def list_seasons(request):
    seasons = Season.objects.all().order_by('-name')
    return render(request, 'lists/season_list.html', {'seasons': seasons, 'title': 'Seasons'})


def list_teams(request):
    teams = Team.objects.all().order_by('name')
    return render(request, 'lists/team_list.html', {'teams': teams, 'title': 'Teams'})


def list_games(request):
    games = Game.objects.all().order_by('-played_at')
    return render(request, 'lists/game_list.html', {'games': games, 'title': 'Games'})


# Edit views
def edit_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    if request.method == 'POST':
        form = LeagueForm(request.POST, instance=league)
        if form.is_valid():
            form.save()
            return redirect('list_leagues')
    else:
        form = LeagueForm(instance=league)
    return render(request, 'forms/add_league.html', {'form': form, 'title': f'Edit League: {league.name}'})


def edit_season(request, pk):
    season = get_object_or_404(Season, pk=pk)
    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            return redirect('list_seasons')
    else:
        form = SeasonForm(instance=season)
    return render(request, 'forms/add_season.html', {'form': form, 'title': f'Edit Season: {season.name}'})


def edit_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect('list_teams')
    else:
        form = TeamForm(instance=team)
    return render(request, 'forms/add_team.html', {'form': form, 'title': f'Edit Team: {team.name}'})


def edit_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == 'POST':
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            game = form.save()
            LeagueStanding.update_standings(game.season)
            return redirect('list_games')
    else:
        form = GameForm(instance=game)
    return render(request, 'forms/add_game.html', {'form': form, 'title': f'Edit Game: {game.home_team.name} vs {game.away_team.name}'})


# Delete views
def delete_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    league.delete()
    return redirect('list_leagues')


def delete_season(request, pk):
    season = get_object_or_404(Season, pk=pk)
    season.delete()
    return redirect('list_seasons')


def delete_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    team.delete()
    return redirect('list_teams')


def delete_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    season = game.season  # store before deletion
    game.delete()
    LeagueStanding.update_standings(season)  # update standings after deletion
    return redirect('list_games')


# Player views
def list_players(request):
    players = Player.objects.annotate(
        goals_count=Count('goals'),
        assists_count=Count('assists')
    ).order_by('name')
    return render(request, 'lists/player_list.html', {'players': players, 'title': 'Players'})


def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    now = timezone.now()
    context = {
        'player': player,
        'now': now,
        'stats': player.get_season_stats(
            # Get stats for current active season
            Season.objects.filter(is_active=True).first()
        ),
    }
    return render(request, 'player_detail.html', context)


def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_players')
    else:
        form = PlayerForm()
    return render(request, 'forms/add_player.html', {'form': form, 'title': 'Add Player'})


def edit_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('list_players')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'forms/add_player.html', {'form': form, 'title': f'Edit Player: {player.name}'})


def delete_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    player.delete()
    return redirect('list_players')


# Contract views
def add_contract(request):
    initial = {}
    if 'player' in request.GET:
        initial['player'] = request.GET['player']
    if 'team' in request.GET:
        initial['team'] = request.GET['team']

    if request.method == 'POST':
        form = PlayerContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_detail', pk=form.cleaned_data['player'].id)
    else:
        form = PlayerContractForm(initial=initial)
    return render(request, 'forms/add_contract.html', {'form': form, 'title': 'Add Contract'})


def edit_contract(request, pk):
    contract = get_object_or_404(PlayerContract, pk=pk)
    if request.method == 'POST':
        form = PlayerContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return redirect('player_detail', pk=contract.player.id)
    else:
        form = PlayerContractForm(instance=contract)
    return render(request, 'forms/add_contract.html', {
        'form': form,
        'title': f'Edit Contract: {contract.player.name} at {contract.team.name}'
    })


def delete_contract(request, pk):
    contract = get_object_or_404(PlayerContract, pk=pk)
    player_id = contract.player.id
    contract.delete()
    return redirect('player_detail', pk=player_id)


# Goal views
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save()
            season = goal.game.season
            LeagueStanding.update_standings(season)  # update standings when goal added
            return redirect('list_games')
    else:
        initial = {}
        if 'game' in request.GET:
            initial['game'] = request.GET['game']
        form = GoalForm(initial=initial)
    return render(request, 'forms/add_goal.html', {'form': form, 'title': 'Add Goal'})


def edit_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save()
            LeagueStanding.update_standings(goal.game.season)
            return redirect('list_games')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'forms/add_goal.html', {
        'form': form,
        'title': f'Edit Goal: {goal.game.home_team.name} vs {goal.game.away_team.name}'
    })


def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    season = goal.game.season
    goal.delete()
    LeagueStanding.update_standings(season)
    return redirect('list_games')


class LeagueViewSet(viewsets.ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

    @action(detail=True, methods=['get'])
    def standings(self, request, pk=None):
        """Get standings for the current active season of the league."""
        league = self.get_object()
        try:
            active_season = league.seasons.get(is_active=True)
            standings = LeagueStanding.objects.filter(season=active_season)
            serializer = LeagueStandingSerializer(standings, many=True)
            return Response(serializer.data)
        except Season.DoesNotExist:
            return Response(
                {"detail": "No active season found for this league."},
                status=status.HTTP_404_NOT_FOUND
            )


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    @action(detail=True, methods=['post'])
    def update_standings(self, request, pk=None):
        """Update standings for this season."""
        season = self.get_object()
        LeagueStanding.update_standings(season)
        standings = LeagueStanding.objects.filter(season=season)
        serializer = LeagueStandingSerializer(standings, many=True)
        return Response(serializer.data)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer

    @action(detail=True, methods=['get'])
    def fixtures(self, request, pk=None):
        """Get all fixtures for a team in the current active season."""
        team = self.get_object()
        try:
            active_season = team.league.seasons.get(is_active=True)
            games = Game.objects.filter(
                Q(home_team=team) | Q(away_team=team),
                season=active_season
            ).order_by('played_at', 'created_at')
            serializer = GameSerializer(games, many=True)
            return Response(serializer.data)
        except Season.DoesNotExist:
            return Response(
                {"detail": "No active season found for this team's league."},
                status=status.HTTP_404_NOT_FOUND
            )


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class LeagueStandingViewSet(viewsets.ModelViewSet):
    queryset = LeagueStanding.objects.all()
    serializer_class = LeagueStandingSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Minimal readonly user viewset. Provides a `me` action for the current user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return the currently authenticated user's serialized data."""
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    """CRUD for players."""
    queryset = Player.objects.all().order_by('name')
    # import serializer lazily to avoid circular import issues
    from .serializers import PlayerSerializer
    serializer_class = PlayerSerializer


class GoalViewSet(viewsets.ModelViewSet):
    """CRUD for goals."""
    queryset = Goal.objects.all().select_related('scorer', 'assistant', 'game')
    from .serializers import GoalSerializer
    serializer_class = GoalSerializer


class StatsViewSet(viewsets.ViewSet):
    """Simple stats endpoints. `list` returns top scorers."""
    def list(self, request):
        top = Player.objects.annotate(goals_count=Count('goals')).order_by('-goals_count')[:10]
        from .serializers import PlayerSerializer
        serializer = PlayerSerializer(top, many=True)
        return Response({'top_scorers': serializer.data})


@api_view(['GET'])
def predict_winner(request):
    """Predict a winner between two teams using simple historical win rates.

    Query params: team1, team2 (ids)
    Returns: {winner_id, team1_win_rate, team2_win_rate, predicted_winner_id, probability}
    """
    t1 = request.query_params.get('team1')
    t2 = request.query_params.get('team2')
    if not t1 or not t2:
        return Response({'detail': 'Please provide team1 and team2 ids as query params.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        t1 = int(t1); t2 = int(t2)
    except ValueError:
        return Response({'detail': 'team1 and team2 must be integer ids.'}, status=status.HTTP_400_BAD_REQUEST)
    if t1 == t2:
        return Response({'detail': 'Provide two different team ids.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        team1 = Team.objects.get(pk=t1)
        team2 = Team.objects.get(pk=t2)
    except Team.DoesNotExist:
        return Response({'detail': 'One or both teams do not exist.'}, status=status.HTTP_404_NOT_FOUND)

    # compute wins and total matches between/overall — we'll use overall matches involving the team
    def stats(team):
        played = Game.objects.filter(Q(home_team=team) | Q(away_team=team)).exclude(home_score__isnull=True, away_score__isnull=True)
        wins = 0
        for g in played:
            w = g.winner()
            if w and w.id == team.id:
                wins += 1
        total = played.count()
        return wins, total

    w1, n1 = stats(team1)
    w2, n2 = stats(team2)

    # win rate with Laplace smoothing
    rate1 = (w1 + 1) / (n1 + 2) if n1 >= 0 else 0.5
    rate2 = (w2 + 1) / (n2 + 2) if n2 >= 0 else 0.5

    # normalize to probability
    s = rate1 + rate2
    prob1 = rate1 / s if s > 0 else 0.5
    prob2 = rate2 / s if s > 0 else 0.5

    predicted = team1.id if prob1 >= prob2 else team2.id

    return Response({
        'team1': team1.id,
        'team2': team2.id,
        'team1_win_rate': round(rate1, 3),
        'team2_win_rate': round(rate2, 3),
        'predicted_winner': predicted,
        'probability': round(max(prob1, prob2), 3),
    })


@api_view(['GET'])
def predict_season(request):
    """Simple season winner prediction: returns team with highest points in latest standings if available.

    Query params: season (id). If omitted, use active season of the first league.
    """
    season_id = request.query_params.get('season')
    try:
        if season_id:
            season = Season.objects.get(pk=int(season_id))
        else:
            season = Season.objects.filter(is_active=True).first()
    except (ValueError, Season.DoesNotExist):
        return Response({'detail': 'Invalid or missing season id.'}, status=status.HTTP_400_BAD_REQUEST)

    if not season:
        return Response({'detail': 'No season found.'}, status=status.HTTP_404_NOT_FOUND)

    # Use cached standings if available
    standing = LeagueStanding.objects.filter(season=season).order_by('-points', '-goal_difference').first()
    if not standing:
        return Response({'detail': 'No standings available for this season.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'predicted_winner': standing.team.id, 'team': standing.team.name, 'points': standing.points})

def league_detail(request, pk):
    """View for showing detailed league information."""
    league = get_object_or_404(League, pk=pk)
    seasons = league.seasons.all().order_by('-start_date')
    active_season = league.seasons.filter(is_active=True).first()

    if active_season:
        standings = LeagueStanding.objects.filter(season=active_season)
        recent_games = Game.objects.filter(
            season=active_season,
            played_at__lt=timezone.now()
        ).exclude(
            home_score__isnull=True
        ).order_by('-played_at')[:5]
        
        upcoming_games = Game.objects.filter(
            season=active_season,
            played_at__gt=timezone.now()
        ).order_by('played_at')[:5]
    else:
        standings = []
        recent_games = []
        upcoming_games = []

    return render(request, 'league_detail.html', {
        'league': league,
        'seasons': seasons,
        'active_season': active_season,
        'standings': standings,
        'recent_games': recent_games,
        'upcoming_games': upcoming_games,
    })

def season_detail(request, pk):
    """View for showing detailed season information."""
    season = get_object_or_404(Season.objects.select_related('league'), pk=pk)
    # Teams are related to a league, not directly to a season. Use the season's league.
    teams = Team.objects.filter(league=season.league)
    games = Game.objects.filter(season=season).order_by('played_at')
    now = timezone.now()

    return render(request, 'season_detail.html', {
        'season': season,
        'teams': teams,
        'games': games,
        'now': now,
    })

def team_detail(request, pk):
    """View for showing detailed team information."""
    try:
        # Ensure league is properly loaded with the team
        team = get_object_or_404(Team.objects.select_related('league'), pk=pk)
        if not team.league_id:
            raise Http404("Team has no associated league")
        
        # Get current players
        current_players = PlayerContract.objects.filter(
            team=team,
            start_date__lte=timezone.now()
        ).select_related('player').filter(
            Q(end_date__isnull=True) | Q(end_date__gt=timezone.now())
        )

        # Get all games for the team
        games = Game.objects.filter(
            Q(home_team=team) | Q(away_team=team)
        ).select_related('home_team', 'away_team', 'season').order_by('-played_at')
    except Exception as e:
        print(f"Error in team_detail: {str(e)}")  # For debugging
        raise

    return render(request, 'team_detail.html', {
        'team': team,
        'current_players': current_players,
        'games': games,
    })

def game_detail(request, game_id):
    """View for showing detailed game information including goals and players."""
    game = get_object_or_404(
        Game.objects.prefetch_related(
            Prefetch('goals', queryset=Goal.objects.select_related('scorer', 'assistant')),
        ), 
        id=game_id
    )
    
    # Get players for both teams at the time of the game
    home_players = PlayerContract.objects.filter(
        team=game.home_team,
        start_date__lte=game.played_at
    ).select_related('player').filter(
        Q(end_date__isnull=True) | Q(end_date__gt=game.played_at)
    )
    
    away_players = PlayerContract.objects.filter(
        team=game.away_team,
        start_date__lte=game.played_at
    ).select_related('player').filter(
        Q(end_date__isnull=True) | Q(end_date__gt=game.played_at)
    )
    
    return render(request, 'game_detail.html', {
        'game': game,
        'home_players': home_players,
        'away_players': away_players,
    })
    
    return render(request, 'game_detail.html', {
        'game': game,
        'home_players': home_players,
        'away_players': away_players
    })
