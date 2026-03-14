from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)
API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')

def api_request(endpoint, params=None):
    """Helper for API calls with error handling."""
    try:
        url = f"{API_URL}{endpoint}"
        headers = {"X-API-Key": "test-key-123"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
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
    return render_template('teamvteam.html', result=result, teams=teams, error=error, 
                         selected_team1=team1, selected_team2=team2)

@app.route('/team_records')
def team_records():
    team = request.args.get('team')
    result = {}
    if team:
        result = api_request('/api/team-records', {'team': team})

    teams_data = api_request('/api/ipl-teams')
    teams = teams_data.get('teams', []) if 'error' not in teams_data else []
    error = result.get('error') if isinstance(result, dict) else None
    return render_template('team_records.html', result=result, teams=teams, 
                         error=error, selected_team=team)

@app.route('/batting-records')
def batting_records():
    batsman = request.args.get('batsman')
    result = {}
    against_top3 = []
    matched_batsman = batsman  # default to original
    if batsman:
        result = api_request('/api/batting-records', {'batsman': batsman})
        # Get the actual matched name from result keys
        if result and 'error' not in result:
            matched_batsman = list(result.keys())[0]
        if result and matched_batsman and matched_batsman in result and 'against' in result[matched_batsman]:
            against_top3 = sorted(result[matched_batsman]['against'].items())[:3]

    error = result.get('error') if isinstance(result, dict) else None
    return render_template('batting_records.html', 
                         result=result, 
                         error=error, 
                         selected_batsman=matched_batsman,
                         against_top3=against_top3)

@app.route('/bowling-records')
def bowling_records():
    bowler = request.args.get('bowler')
    result = {}
    against_top3 = []
    matched_bowler = bowler  # default to original
    if bowler:
        result = api_request('/api/bowling-records', {'bowler': bowler})
        # Get the actual matched name from result keys
        if result and 'error' not in result:
            matched_bowler = list(result.keys())[0]
        if result and matched_bowler and matched_bowler in result and 'against' in result[matched_bowler]:
            against_top3 = sorted(result[matched_bowler]['against'].items())[:3]

    error = result.get('error') if isinstance(result, dict) else None
    return render_template('bowling_records.html', 
                         result=result, 
                         error=error, 
                         selected_bowler=matched_bowler,
                         against_top3=against_top3)

if __name__ == '__main__':
    app.run(debug=False, port=8000)