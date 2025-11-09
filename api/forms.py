from django import forms
from .models import League, Season, Team, Game, Player, PlayerContract, Goal


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name', 'country']


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['league', 'name', 'is_active', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'league', 'short_name', 'founded_year']


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['season', 'home_team', 'away_team', 'played_at', 'home_score', 'away_score']
        widgets = {
            'played_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()
        home = cleaned.get('home_team')
        away = cleaned.get('away_team')
        season = cleaned.get('season')
        if home and away and home == away:
            raise forms.ValidationError('Home team and away team must be different')
        if season and home and home.league != season.league:
            raise forms.ValidationError('Home team and season must belong to same league')
        if season and away and away.league != season.league:
            raise forms.ValidationError('Away team and season must belong to same league')
        return cleaned


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'position', 'nationality', 'birth_date', 'height', 'weight']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PlayerContractForm(forms.ModelForm):
    class Meta:
        model = PlayerContract
        fields = ['player', 'team', 'number', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        player = cleaned.get('player')
        team = cleaned.get('team')
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if start and end and start > end:
            raise forms.ValidationError('End date must be after start date')

        # Check for overlapping contracts
        if player and start and end:
            overlapping = PlayerContract.objects.filter(
                player=player,
                start_date__lte=end,
                end_date__gte=start
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise forms.ValidationError('Player already has a contract during this period')
        
        return cleaned


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['game', 'scorer', 'assistant', 'minute', 'is_penalty', 'is_own_goal']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.game:
            players = (
                self.instance.game.home_team_players.all() |
                self.instance.game.away_team_players.all()
            ).distinct()
            self.fields['scorer'].queryset = players
            self.fields['assistant'].queryset = players
    
    def clean(self):
        cleaned = super().clean()
        game = cleaned.get('game')
        scorer = cleaned.get('scorer')
        assistant = cleaned.get('assistant')
        minute = cleaned.get('minute')

        if game and minute:
            if minute > 120:  # Allow for extra time
                raise forms.ValidationError('Invalid minute (max 120)')

        if scorer and assistant and scorer == assistant:
            raise forms.ValidationError('Scorer and assistant must be different players')

        if game and scorer and scorer not in game.home_team_players.all() and scorer not in game.away_team_players.all():
            raise forms.ValidationError('Scorer must be in one of the teams')

        if game and assistant and assistant not in game.home_team_players.all() and assistant not in game.away_team_players.all():
            raise forms.ValidationError('Assistant must be in one of the teams')

        return cleaned