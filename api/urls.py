from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeagueViewSet, SeasonViewSet, TeamViewSet,
    GameViewSet, LeagueStandingViewSet, PlayerViewSet,
    GoalViewSet, UserViewSet, StatsViewSet,
    predict_winner, predict_season
)

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
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/user/', UserViewSet.as_view({'get': 'me'}), name='user_me'),
    
    # Prediction endpoints
    path('predict/match/', predict_winner, name='predict_match'),
    path('predict/season/', predict_season, name='predict_season'),
    
    # Include router URLs
    path('', include(router.urls)),
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
