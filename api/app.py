from flask import Flask, jsonify, request
import ipl
import json  # Add this import

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the IPL API Service"

@app.route('/api/ipl-teams', methods=['GET'])
def get_ipl_teams():  # Renamed for clarity
    teams = ipl.teamsAPI()
    return jsonify(teams)

@app.route('/api/teamvteam', methods=['GET'])  # Added methods
def team_vs_team():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    if not team1 or not team2:
        return jsonify({"error": "Please provide both team1 and team2 parameters"}), 400
    
    # Add existence check
    all_teams = ipl.teamsAPI()['teams']
    if team1 not in all_teams or team2 not in all_teams:
        return jsonify({"error": f"Invalid team(s): {team1}, {team2}. Valid teams: {all_teams}"}), 400
    
    matches = ipl.teamVteamAPI(team1, team2)
    return jsonify(matches)

@app.route('/api/team-records', methods=['GET'])
def team_records():
    team = request.args.get('team')
    if not team:
        return jsonify({"error": "Please provide the team parameter"}), 400
    
    teams = ipl.teamsAPI()['teams']
    if team not in teams:
        return jsonify({"error": f"Team '{team}' not found"}), 404
    
    response_str = ipl.teamAPI(team)  # JSON string
    response = json.loads(response_str)  # Parse to dict
    return jsonify(response)

@app.route('/api/batting-records', methods=['GET'])
def batting_records():
    batsman = request.args.get('batsman')
    if not batsman:
        return jsonify({"error": "Please provide the batsman parameter"}), 400
    
    response_str = ipl.batsmanAPI(batsman)  # JSON string
    try:
        response = json.loads(response_str)  # Parse to dict
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid data from backend"}), 500
    
    # Check if effectively "not found" (zero activity)
    if response[batsman]['all']['innings'] == 0:
        return jsonify({"error": f"Batsman '{batsman}' not found"}), 404
    return jsonify(response)

@app.route('/api/bowling-records', methods=['GET'])
def bowling_records():
    bowler = request.args.get('bowler')
    if not bowler:
        return jsonify({"error": "Please provide the bowler parameter"}), 400
    
    response_str = ipl.bowlerAPI(bowler)  # JSON string
    try:
        response = json.loads(response_str)  # Parse to dict
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid data from backend"}), 500
    
    # Check if effectively "not found" (zero activity)
    if response[bowler]['all']['innings'] == 0:
        return jsonify({"error": f"Bowler '{bowler}' not found"}), 404
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)