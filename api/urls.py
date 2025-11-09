from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView
)
from .views import (
    # viewsets
    LeagueViewSet, SeasonViewSet, TeamViewSet,
    GameViewSet, LeagueStandingViewSet, PlayerViewSet,
    GoalViewSet, UserViewSet, StatsViewSet,
    # function-based API endpoints / pages
    predict_winner, predict_season,
    index, dashboard,
    add_league, add_season, add_team, add_game,
    edit_league, edit_season, edit_team, edit_game,
    delete_league, delete_season, delete_team, delete_game,
    list_leagues, list_seasons, list_teams, list_games,
    list_players, add_player, player_detail, edit_player, delete_player,
    add_contract, edit_contract, delete_contract,
    add_goal, edit_goal, delete_goal,
    league_detail, season_detail, team_detail, game_detail,
)
from .views import CustomTokenObtainPairView

# API router for viewsets
router = DefaultRouter()
router.register('leagues', LeagueViewSet, basename='league')
router.register('seasons', SeasonViewSet, basename='season')
router.register('teams', TeamViewSet, basename='team')
router.register('games', GameViewSet, basename='game')
router.register('standings', LeagueStandingViewSet, basename='standing')
router.register('players', PlayerViewSet, basename='player')
router.register('goals', GoalViewSet, basename='goal')
router.register('users', UserViewSet, basename='user')
router.register('stats', StatsViewSet, basename='stats')

urlpatterns = [
    # Authentication endpoints
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/user/', UserViewSet.as_view({'get': 'me'}), name='user_me'),
    
    # Prediction endpoints
    path('predict/match/', predict_winner, name='predict_match'),
    path('predict/season/', predict_season, name='predict_season'),
    
    # Include router URLs
    # path('', include(router.urls)),
    # Site/listing pages (HTML views)
    path('leagues/', list_leagues, name='list_leagues'),
    path('seasons/', list_seasons, name='list_seasons'),
    path('teams/', list_teams, name='list_teams'),
    path('games/', list_games, name='list_games'),
    path('leagues/<int:pk>/', league_detail, name='league_detail'),
    path('seasons/<int:pk>/', season_detail, name='season_detail'),
    path('teams/<int:pk>/', team_detail, name='team_detail'),
    # Add views
    path('leagues/add/', add_league, name='add_league'),
    path('seasons/add/', add_season, name='add_season'),
    path('teams/add/', add_team, name='add_team'),
    path('games/add/', add_game, name='add_game'),
    
    # Edit views
    path('leagues/<int:pk>/edit/', edit_league, name='edit_league'),
    path('seasons/<int:pk>/edit/', edit_season, name='edit_season'),
    path('teams/<int:pk>/edit/', edit_team, name='edit_team'),
    path('games/<int:pk>/edit/', edit_game, name='edit_game'),
    
    # Delete views
    path('leagues/<int:pk>/delete/', delete_league, name='delete_league'),
    path('seasons/<int:pk>/delete/', delete_season, name='delete_season'),
    path('teams/<int:pk>/delete/', delete_team, name='delete_team'),
    path('games/<int:pk>/delete/', delete_game, name='delete_game'),
    
    # Player management
    path('players/', list_players, name='list_players'),
    path('players/add/', add_player, name='add_player'),
    path('players/<int:pk>/', player_detail, name='player_detail'),
    path('players/<int:pk>/edit/', edit_player, name='edit_player'),
    path('players/<int:pk>/delete/', delete_player, name='delete_player'),
    
    # Contracts
    path('contracts/add/', add_contract, name='add_contract'),
    path('contracts/<int:pk>/edit/', edit_contract, name='edit_contract'),
    path('contracts/<int:pk>/delete/', delete_contract, name='delete_contract'),
    
    # Goals
    path('goals/add/', add_goal, name='add_goal'),
    path('goals/<int:pk>/edit/', edit_goal, name='edit_goal'),
    path('goals/<int:pk>/delete/', delete_goal, name='delete_goal'),
    
    # API routes
    path('api/', include(router.urls)),
    
    # Predictions
    path('predict/', predict_winner, name='predict'),
    path('games/<int:game_id>/', game_detail, name='game_detail'),
]
