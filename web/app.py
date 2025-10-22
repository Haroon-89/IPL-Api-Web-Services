from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)
API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')  # Easy to change for prod

def api_request(endpoint, params=None):
    """Helper for API calls with error handling."""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises for 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API error: {str(e)}. Ensure API is running on {API_URL}."}

@app.route('/')
def home():
    teams_data = api_request('/api/ipl-teams')
    teams = teams_data.get('teams', []) if 'error' not in teams_data else []
    return render_template('home.html', teams=teams)

@app.route('/teamvteam')
def team_vs_team():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    result = {}
    if team1 and team2:
        result = api_request('/api/teamvteam', {'team1': team1, 'team2': team2})
    
    teams_data = api_request('/api/ipl-teams')
    teams = teams_data.get('teams', []) if 'error' not in teams_data else []
    error = result.get('error') if isinstance(result, dict) else None
    return render_template('teamvteam.html', result=result, teams=teams, error=error, selected_team1=team1, selected_team2=team2)

@app.route('/team_records')
def team_records():
    team = request.args.get('team')
    result = {}
    if team:
        result = api_request('/api/team-records', {'team': team})
    
    teams_data = api_request('/api/ipl-teams')
    teams = teams_data.get('teams', []) if 'error' not in teams_data else []
    error = result.get('error') if isinstance(result, dict) else None
    return render_template('team_records.html', result=result, teams=teams, error=error, selected_team=team)

@app.route('/batting-records')
def batting_records():
    batsman = request.args.get('batsman')
    result = {}
    against_top3 = []
    if batsman:
        result = api_request('/api/batting-records', {'batsman': batsman})
        # Pre-process: Sort and slice against dict for top 3 (alphabetical for simplicity; could sort by runs if needed)
        if result and batsman in result and 'against' in result[batsman]:
            against_top3 = sorted(result[batsman]['against'].items())[:3]  # List of (team, stats_dict)
    
    error = result.get('error') if isinstance(result, dict) else None
    return render_template('batting_records.html', result=result, error=error, selected_batsman=batsman, against_top3=against_top3)

@app.route('/bowling-records')
def bowling_records():
    bowler = request.args.get('bowler')
    result = {}
    against_top3 = []
    if bowler:
        result = api_request('/api/bowling-records', {'bowler': bowler})
        # Pre-process: Sort and slice against dict for top 3
        if result and bowler in result and 'against' in result[bowler]:
            against_top3 = sorted(result[bowler]['against'].items())[:3]
    
    error = result.get('error') if isinstance(result, dict) else None
    return render_template('bowling_records.html', result=result, error=error, selected_bowler=bowler, against_top3=against_top3)

if __name__ == '__main__':
    app.run(debug=True, port=8000)