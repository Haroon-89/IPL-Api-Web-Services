# IPL Stats Web App

A Flask-based web application for exploring Indian Premier League (IPL) cricket statistics. Features team records, head-to-head matchups, batting and bowling performances. Powered by public IPL datasets with a modular dual-server API backend, API key authentication, rate limiting, and fuzzy player name search.

## Features
- **Team Records**: View overall and against-specific stats (matches played, wins, losses, titles).
- **Team vs. Team**: Head-to-head match history and win counts.
- **Batting Records**: Player stats like runs, average, strike rate, highest score, vs. teams.
- **Bowling Records**: Wickets, economy, best figures, vs. teams.
- **Fuzzy Search**: Search players by full name (e.g., "Virat Kohli" instead of "V Kohli").
- **API Key Authentication**: All API endpoints secured with key-based auth.
- **Rate Limiting**: 30 requests per minute per endpoint, 100 per hour global limit.
- **Response Caching**: Frequently accessed endpoints cached for faster responses.
- Responsive UI with dropdown selectors for teams/players.
- Comprehensive error handling (400/404/500 responses).

Data covers IPL seasons up to 2023. For 2024/2025 updates, see [Data Sources](#data-sources).

## Tech Stack
- **Backend**: Flask (Web: port 8000, API: port 5000)
- **Data Processing**: Pandas, NumPy
- **Frontend**: Jinja2 templates, HTML/CSS
- **Security**: API key authentication, Flask-Limiter for rate limiting
- **Caching**: Flask-Caching with SimpleCache
- **Fuzzy Search**: thefuzz + python-Levenshtein
- **JSON Handling**: Custom encoder for NumPy types (NaN/inf → null)

## Project Structure
```
IPL-Api-Web-Services/
├── api/
│   ├── app.py         # Flask API server with auth, caching, rate limiting
│   └── ipl.py         # Core data logic, functions, fuzzy search
├── web/
│   ├── app.py         # Flask web server
│   └── templates/     # HTML templates
│       ├── base.html
│       ├── home.html
│       ├── team_records.html
│       ├── teamvteam.html
│       ├── batting_records.html
│       └── bowling_records.html
├── root.py            # Launcher script (starts both servers)
├── requirements.txt   # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+
- Internet access (initial CSV download from Google Drive)

### Installation
```bash
# Clone the repository
git clone https://github.com/Haroon-89/IPL-Api-Web-Services.git
cd IPL-Api-Web-Services

# Install dependencies
pip install -r requirements.txt
```

### Run the App
```bash
python root.py
```
- Waits for API to fully load dataset before starting web server
- API runs on `http://127.0.0.1:5000`
- Web runs on `http://127.0.0.1:8000`
- Press Ctrl+C to stop both servers

### Access Pages
- Home: `http://127.0.0.1:8000/`
- Team Records: `http://127.0.0.1:8000/team_records?team=Chennai Super Kings`
- Team vs Team: `http://127.0.0.1:8000/teamvteam?team1=Mumbai Indians&team2=Chennai Super Kings`
- Batting: `http://127.0.0.1:8000/batting-records?batsman=Virat Kohli`
- Bowling: `http://127.0.0.1:8000/bowling-records?bowler=Jasprit Bumrah`

## API Endpoints
All GET requests. Base URL: `http://127.0.0.1:5000/api/`

**Authentication**: All endpoints require `X-API-Key` header:
```
X-API-Key: test-key-123
```

| Endpoint | Parameters | Description |
|----------|------------|-------------|
| `/ipl-teams` | None | List all IPL teams |
| `/teamvteam` | `team1`, `team2` | Head-to-head stats |
| `/team-records` | `team` | Team overall & vs. others |
| `/batting-records` | `batsman` | Batsman stats & vs. teams (fuzzy search supported) |
| `/bowling-records` | `bowler` | Bowler stats & vs. teams (fuzzy search supported) |

**Error Responses**:
- `400` — Missing required parameters
- `401` — Invalid or missing API key
- `404` — Player or team not found
- `500` — Internal data processing error

## Fuzzy Search
Player names are automatically matched using fuzzy search — no need to know exact dataset format:
```
"Virat Kohli"   → matches → "V Kohli"
"Jasprit Bumrah" → matches → "JJ Bumrah"
"MS Dhoni"      → matches → "MS Dhoni"
```

## Requirements
```
flask
pandas
numpy
requests
flask-caching
flask-limiter
thefuzz
python-Levenshtein
```

Install all:
```bash
pip install -r requirements.txt
```

## Data Sources
- **Matches**: IPL Matches CSV (~800 rows, seasons 2008-2023)
- **Balls**: IPL Balls CSV (~200k rows, ball-by-ball data)
- Loaded via Pandas on startup from Google Drive.
- For 2024/2025 updates: Replace URLs in `api/ipl.py` with updated CSVs from Kaggle or cricsheet.org.

## Known Limitations
- Data only covers IPL seasons up to 2023
- Dataset loads from Google Drive on startup — requires internet connection
- In-memory caching resets on server restart

## License
MIT License — free to use and modify.

## Author
**Haroon Iqbal** — [GitHub](https://github.com/Haroon-89)