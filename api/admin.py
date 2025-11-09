from django.contrib import admin
from .models import League, Season, Team, Game, LeagueStanding


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at')
    search_fields = ('name', 'country')
    list_filter = ('country',)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'is_active', 'start_date', 'end_date')
    list_filter = ('league', 'is_active')
    search_fields = ('name', 'league__name')
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        # First, deactivate all seasons in the same league
        for season in queryset:
            Season.objects.filter(league=season.league).update(is_active=False)
        # Then activate selected seasons
        queryset.update(is_active=True)
    make_active.short_description = "Make selected seasons active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Make selected seasons inactive"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'short_name', 'founded_year', 'created_at')
    list_filter = ('league',)
    search_fields = ('name', 'short_name')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('get_match_display', 'season', 'played_at', 'get_score_display')
    list_filter = ('season', 'played_at', 'season__league')
    search_fields = ('home_team__name', 'away_team__name')
    raw_id_fields = ('home_team', 'away_team')
    date_hierarchy = 'played_at'
    
    def get_match_display(self, obj):
        return f"{obj.home_team.name} vs {obj.away_team.name}"
    get_match_display.short_description = 'Match'
    
    def get_score_display(self, obj):
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.home_score} - {obj.away_score}"
        return "Not played"
    get_score_display.short_description = 'Score'


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('team', 'season', 'position', 'played', 'won', 'drawn', 'lost', 'goals_for', 'goals_against', 'goal_difference', 'points')
    list_filter = ('season', 'season__league')
    search_fields = ('team__name',)
    readonly_fields = ('position', 'played', 'won', 'drawn', 'lost', 'goals_for', 'goals_against', 'goal_difference', 'points', 'last_updated')
    ordering = ('season', 'position')

    def has_add_permission(self, request):
        return False  # Standings are automatically generated
