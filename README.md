# IPL Stats Web App

A Flask-based web application for exploring Indian Premier League (IPL) cricket statistics. Features include team records, head-to-head matchups, batting and bowling performances. Powered by public IPL datasets, with a modular API backend.


## Features
- **Team Records**: View overall and against-specific stats (matches played, wins, losses, titles).
- **Team vs. Team**: Head-to-head match history and win counts.
- **Batting Records**: Player stats like runs, average, strike rate, highest score, vs. teams.
- **Bowling Records**: Wickets, economy, best figures, vs. teams.
- Responsive UI with dropdown selectors for teams/players.
- Error handling for invalid queries.

Data covers IPL seasons up to 2023 (based on source CSVs). For 2024/2025 updates, see [Data Sources](#data-sources).

## Tech Stack
- **Backend**: Flask (Web: port 8000, API: port 5000)
- **Data Processing**: Pandas, NumPy
- **Frontend**: Jinja2 templates, basic HTML/CSS (no JS framework)
- **JSON Handling**: Custom encoder for NumPy types (NaN/inf → null)
- **Deployment**: Local dev with subprocesses; easy Docker-ize

## Quick Start
1. **Prerequisites**:
   - Python 3.8+ (venv recommended)
   - Install dependencies: `pip install flask requests pandas numpy`
   - Internet access (initial CSV download from Google Drive)

2. **Project Structure**:
   ```
   ipl-stats-app/
   ├── api/
   │   ├── app.py         # Flask API server
   │   └── ipl.py         # Core data logic & functions
   ├── web/
   │   ├── app.py         # Flask web server
   │   └── templates/     # HTML templates (home.html, team_records.html, etc.)
   ├── run.py             # Launcher script (starts both servers)
   └── README.md          # This file
   ```

3. **Run the App**:
   ```bash
   # From project root
   python run.py
   ```
   - Starts API on `http://localhost:5000`
   - Starts Web on `http://localhost:8000`
   - Press Ctrl+C to stop.

4. **Access Pages**:
   - Home: `http://localhost:8000/` (team list)
   - Team Records: `http://localhost:8000/team_records?team=Chennai%20Super%20Kings`
   - Team vs. Team: `http://localhost:8000/teamvteam?team1=Mumbai%20Indians&team2=Chennai%20Super%20Kings`
   - Batting: `http://localhost:8000/batting-records?batsman=Virat%20Kohli`
   - Bowling: `http://localhost:8000/bowling-records?bowler=Jasprit%20Bumrah`

## API Endpoints
All GET requests. Base URL: `http://localhost:5000/api/`

| Endpoint | Parameters | Description | Response Example |
|----------|------------|-------------|------------------|
| `/ipl-teams` | None | List all IPL teams | `{"teams": ["Mumbai Indians", "Chennai Super Kings", ...]}` |
| `/teamvteam` | `team1`, `team2` | Head-to-head stats | `{"total_matches": 30, "Mumbai Indians": 15, "Chennai Super Kings": 14, "draws": 1}` |
| `/team-records` | `team` | Team overall & vs. others | `{"Chennai Super Kings": {"overall": {"matchesplayed": 200, "won": 110, ...}, "against": {...}}}` |
| `/batting-records` | `batsman` | Batsman stats & vs. teams | `{"Virat Kohli": {"all": {"runs": 7000, "avg": 38.5, ...}, "against": {...}}}` |
| `/bowling-records` | `bowler` | Bowler stats & vs. teams | `{"Jasprit Bumrah": {"all": {"wicket": 150, "economy": 7.2, ...}, "against": {...}}}` |

- **Error Responses**: `{"error": "Message"}` (e.g., 400 for missing params, 404 for invalid team/player).
- **Notes**: Players with 0 innings return 404. NaN values (e.g., infinite avg) render as `null`.

## Data Sources
- **Matches**: [IPL Matches CSV](https://drive.google.com/uc?id=1NQpjbVD157y1fxF2i-9KyJEswQPCUCqC) (~800 rows, seasons 2008-2023)
- **Balls**: [IPL Balls CSV](https://drive.google.com/uc?id=1OHOH_nTOL2QwXD3Y9gP81c-JY8Qi64kY) (~200k rows, ball-by-ball data)
- Loaded via Pandas on first run. For 2024/2025: Replace URLs with updated CSVs (e.g., from Kaggle or cricsheet.org).

## Development & Debugging
- **Environment**: Set `API_URL` env var for prod (default: `http://127.0.0.1:5000`).
- **Debug Mode**: Enabled by default (`debug=True`).
- **Common Issues**:
  - **Jinja2 UndefinedError**: Fixed by parsing JSON strings in API routes (double-serialization bug).
  - **NaN in JSON**: Custom `NPEncoder` handles NumPy NaN/inf.
  - **CSV Download Fails**: Ensure Google Drive access; fallback to local files.
  - **Outdated Data**: As of October 22, 2025, update CSVs for IPL 2025 (e.g., Chennai Super Kings' latest titles).
- **Testing**: Use `curl` for API (e.g., `curl "http://localhost:5000/api/team-records?team=CSK"`). Add unit tests for `ipl.py` functions.
- **Extensions**: Add charts (Matplotlib/Plotly), player search, season filters.

## Contributing
- Fork, PR with tests.
- Issues: Report bugs (e.g., player name mismatches like "MS Dhoni" vs. "Dhoni").
- License: MIT (feel free to use/modify).

## Credits
- Data: Public IPL datasets via Google Drive.
- Inspired by cricket analytics tutorials.
- Fixed bugs from community debugging (e.g., template type errors).
