from flask import Flask, jsonify, request
import ipl
import json
from functools import wraps
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ─── API Key Authentication ───────────────────────────────────────────────────

VALID_API_KEYS = {"test-key-123", "ipl-client-key"}

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key not in VALID_API_KEYS:
            return jsonify({"error": "Unauthorized. Provide a valid X-API-Key header"}), 401
        return f(*args, **kwargs)
    return decorated

# ─── Caching Setup ───────────────────────────────────────────────────────────

cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
})
cache.init_app(app)

# ─── Rate Limiting Setup ──────────────────────────────────────────────────────

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the IPL API Service",
        "note": "All /api/* endpoints require X-API-Key header",
        "endpoints": [
            "/api/ipl-teams",
            "/api/teamvteam?team1=&team2=",
            "/api/team-records?team=",
            "/api/batting-records?batsman=",
            "/api/bowling-records?bowler="
        ]
    })

@app.route('/api/ipl-teams', methods=['GET'])
@require_api_key
@cache.cached(timeout=300)
@limiter.limit("30 per minute")
def get_ipl_teams():
    teams = ipl.teamsAPI()
    return jsonify(teams)

@app.route('/api/teamvteam', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def team_vs_team():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    if not team1 or not team2:
        return jsonify({"error": "Please provide both team1 and team2 parameters"}), 400

    all_teams = ipl.teamsAPI()['teams']
    if team1 not in all_teams or team2 not in all_teams:
        return jsonify({"error": f"Invalid team(s): {team1}, {team2}. Valid teams: {all_teams}"}), 400

    matches = ipl.teamVteamAPI(team1, team2)
    return jsonify(matches)

@app.route('/api/team-records', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def team_records():
    team = request.args.get('team')
    if not team:
        return jsonify({"error": "Please provide the team parameter"}), 400

    teams = ipl.teamsAPI()['teams']
    if team not in teams:
        return jsonify({"error": f"Team '{team}' not found"}), 404

    response_str = ipl.teamAPI(team)
    response = json.loads(response_str)
    return jsonify(response)

@app.route('/api/batting-records', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def batting_records():
    batsman = request.args.get('batsman')
    if not batsman:
        return jsonify({"error": "Please provide the batsman parameter"}), 400

    # Fuzzy match player name
    all_batsmen = ipl.ball_withmatch['batter'].unique().tolist()
    matched_batsman = ipl.findPlayer(batsman, all_batsmen)

    print(f"Searched: {batsman} → Matched: {matched_batsman}")

    response_str = ipl.batsmanAPI(matched_batsman)
    try:
        response = json.loads(response_str)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid data from backend"}), 500

    if response[matched_batsman]['all']['innings'] == 0:
        return jsonify({"error": f"Batsman '{batsman}' not found"}), 404

    return jsonify(response)

@app.route('/api/bowling-records', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def bowling_records():
    bowler = request.args.get('bowler')
    if not bowler:
        return jsonify({"error": "Please provide the bowler parameter"}), 400

    # Fuzzy match player name
    all_bowlers = ipl.ball_withmatch['bowler'].unique().tolist()
    matched_bowler = ipl.findPlayer(bowler, all_bowlers)

    response_str = ipl.bowlerAPI(matched_bowler)
    try:
        response = json.loads(response_str)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid data from backend"}), 500

    if response[matched_bowler]['all']['innings'] == 0:
        return jsonify({"error": f"Bowler '{bowler}' not found"}), 404

    return jsonify(response)

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(port=5000, debug=False)