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

Below is a concise list of the API endpoints provided by the project. Most API resources are exposed as DRF viewsets under `/api/` and support standard REST verbs (GET, POST, PUT/PATCH, DELETE) unless noted.

- Authentication (JWT - SPA friendly)
   - `POST /auth/token/` — obtain access + refresh tokens (response includes `user` object)
      - body: `{ "username": "...", "password": "..." }`
   - `POST /auth/token/refresh/` — refresh access token (body: `{ "refresh": "<token>" }`)
   - `POST /auth/token/verify/` — verify a token
   - `GET /auth/user/` — (named `user_me`) returns current user (`me` action; requires Authorization header)

- Users
   - `GET /api/users/` — list users
   - `GET /api/users/<id>/` — retrieve user

- Leagues / Seasons / Standings
   - `GET /api/leagues/` — list leagues
   - `GET /api/leagues/<id>/` — league detail
   - `GET /api/seasons/` — list seasons
   - `GET /api/seasons/<id>/` — season detail
   - `GET /api/standings/` — list cached standings

- Teams / Players / Contracts / Goals
   - `GET /api/teams/`, `POST /api/teams/`, `GET/PUT/DELETE /api/teams/<id>/`
   - `GET /api/players/`, `GET /api/players/<id>/`
   - `GET /api/goals/`, `POST /api/goals/`, `GET/PUT/DELETE /api/goals/<id>/`

- Games
   - `GET /api/games/`, `POST /api/games/`, `GET/PUT/DELETE /api/games/<id>/`

- Stats & Predictions
   - `GET /api/stats/` — simple stats endpoints (e.g. `top_scorers`)
   - `GET /predict/match/?team1=<id>&team2=<id>` — basic match prediction (heuristic)
   - `GET /predict/season/?season=<id>` — basic season winner prediction

Examples (token + request)

- Obtain token (curl):

```bash
curl -X POST http://127.0.0.1:8000/auth/token/ \
   -H "Content-Type: application/json" \
   -d '{"username":"apitest","password":"TestPass123"}'
```

Response contains `access`, `refresh` and a `user` object. Use the access token for authorized API calls:

```http
Authorization: Bearer <access_token>
```

SPA notes
- CORS is enabled for `http://localhost:3000` in development (`myproject/settings.py`). The token endpoint returns user info alongside tokens to simplify SPA login flow. For production, review token storage/rotation and consider httpOnly cookies for refresh tokens.

The prediction endpoints use simple heuristics (historical win rates with Laplace smoothing) — they are intentionally basic and intended as examples that can be replaced by a model service.

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
