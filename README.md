# Football League Management System

A Django web application for managing football leagues, teams, players, and matches. Track league standings, match results, and player statistics in real-time.

This project is coded by Copilot completely.

## Features

### League Management
- Create and manage multiple leagues
- Track league seasons
- Real-time league standings
- Team performance statistics

### Team Management
- Team profiles with detailed information
- Player roster management
- Team statistics and performance tracking
- Historical match data

### Match Management
- Schedule and record matches
- Live score updates
- Goal tracking with scorer and assist information
- Team lineups for each match
- Match statistics and commentary

### Player Management
- Player profiles with personal information
- Performance statistics
- Contract management
- Position and squad number tracking

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5
- **Database**: SQLite (can be easily switched to PostgreSQL for production)
- **API**: Django REST Framework

## Project Structure

```
django-app/
│
├── api/                    # Main application directory
│   ├── management/        # Custom management commands
│   ├── migrations/        # Database migrations
│   ├── templates/        # HTML templates
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL routing
│   └── forms.py          # Form definitions
│
├── myproject/            # Project configuration
│   ├── settings.py      # Project settings
│   └── urls.py          # Main URL routing
│
├── templates/           # Global templates
│   ├── base.html       # Base template
│   ├── dashboard.html  # Main dashboard
│   └── lists/          # List view templates
│
└── static/             # Static files (CSS, JS, images)
```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd django-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Load sample data:
   ```bash
   python manage.py seed_data
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000/ in your browser

## API Endpoints

### Teams
- `GET /api/teams/` - List all teams
- `POST /api/teams/` - Create a new team
- `GET /api/teams/<id>/` - Get team details
- `PUT /api/teams/<id>/` - Update team
- `DELETE /api/teams/<id>/` - Delete team

### Games
- `GET /api/games/` - List all games
- `POST /api/games/` - Create a new game
- `GET /api/games/<id>/` - Get game details
- `PUT /api/games/<id>/` - Update game
- `DELETE /api/games/<id>/` - Delete game

### Match Prediction
- `GET /api/predict/?team1=<id>&team2=<id>` - Get match prediction

The prediction endpoint uses a simple historical win-rate heuristic with Laplace smoothing. This provides a basic probability estimate based on past performance and can be extended with more sophisticated models.

## Database Models

### League
- Name
- Country
- Founded date
- Teams (relationship)

### Season
- Name (e.g., "2025/2026")
- League (relationship)
- Start/End dates
- Active status

### Team
- Name
- League (relationship)
- Country
- Founded date
- Players (through PlayerContract)

### Player
- Name
- Nationality
- Birth date
- Position
- Current team (through PlayerContract)

### Game
- Season (relationship)
- Home/Away teams
- Date and time
- Scores
- Goals (relationship)

### Goal
- Game (relationship)
- Scorer (Player relationship)
- Assistant (Player relationship)
- Minute
- Team

### LeagueStanding
- Season (relationship)
- Team (relationship)
- Current statistics (points, wins, draws, etc.)

## Custom Management Commands

### seed_data
Populates the database with sample data including:
- League creation
- Teams with players
- Full season fixture generation
- Random match results and goals
- Automatic standings updates

Usage:
```bash
python manage.py seed_data [--league "League Name"] [--teams 20]
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
