import pandas as pd
import numpy as np
import json
from thefuzz import process

class NPEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NPEncoder, self).default(obj)

ipl_matches_url = "https://drive.google.com/uc?id=1NQpjbVD157y1fxF2i-9KyJEswQPCUCqC"
ipl_matches = pd.read_csv(ipl_matches_url)

ipl_balls_url = "https://drive.google.com/uc?id=1OHOH_nTOL2QwXD3Y9gP81c-JY8Qi64kY"
ipl_balls = pd.read_csv(ipl_balls_url)

ball_withmatch = ipl_balls.merge(ipl_matches, left_on='match_id', right_on='id', how='inner').copy()
ball_withmatch.drop(columns=['id'], inplace=True)

batter_data = ball_withmatch.copy()

# ─── Fuzzy Search ─────────────────────────────────────────────────────────────

def findPlayer(name, player_list):
    # First try exact match (case insensitive)
    name_lower = name.lower().strip()
    for player in player_list:
        if player.lower().strip() == name_lower:
            return player
    
    # Then try last name exact match
    # e.g "Virat Kohli" → last name "Kohli"
    name_parts = name_lower.split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1]  # "kohli"
        first_initial = name_parts[0][0]  # "v"
        
        # Look for "X Kohli" pattern in player list
        candidates = []
        for player in player_list:
            player_parts = player.lower().strip().split()
            if len(player_parts) >= 2:
                # Last name matches
                if player_parts[-1] == last_name:
                    # First initial matches
                    if player_parts[0][0] == first_initial:
                        candidates.append(player)
        
        if len(candidates) == 1:
            return candidates[0]  # Only one match, return it
        elif len(candidates) > 1:
            # Multiple matches, use fuzzy on candidates only
            result = process.extractOne(name, candidates)
            if result:
                return result[0]
    
    # Fall back to fuzzy on full list
    result = process.extractOne(name, player_list)
    if result is None:
        return name
    match, score = result
    if score >= 70:
        return match
    return name

# ─── Teams ────────────────────────────────────────────────────────────────────

def teamsAPI():
    teams = np.unique(ipl_matches[['team1', 'team2']])
    team_dict = {
        'teams': teams.tolist()
    }
    return team_dict

def teamVteamAPI(team1, team2):
    matches = ipl_matches[((ipl_matches['team1'] == team1) & (ipl_matches['team2'] == team2)) |
                          ((ipl_matches['team1'] == team2) & (ipl_matches['team2'] == team1))]
    total_matches = matches.shape[0]
    matches_won_team1 = matches[matches['winner'] == team1].shape[0]
    matches_won_team2 = matches[matches['winner'] == team2].shape[0]
    draws = total_matches - (matches_won_team1 + matches_won_team2)
    response = {
        'total_matches': total_matches,
        team1: matches_won_team1,
        team2: matches_won_team2,
        'draws': draws
    }
    return response

def team1vsteam2(team, team2):
    df = ipl_matches[((ipl_matches['team1'] == team) & (ipl_matches['team2'] == team2)) |
                     ((ipl_matches['team2'] == team) & (ipl_matches['team1'] == team2))].copy()
    mp = df.shape[0]
    won = df[df.winner == team].shape[0]
    nr = df[df.winner.isna()].shape[0]
    loss = mp - won - nr
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr}

def allRecord(team):
    df = ipl_matches[(ipl_matches['team1'] == team) | (ipl_matches['team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.winner == team].shape[0]
    nr = df[df.winner.isna()].shape[0]
    loss = mp - won - nr
    nt = df[(df.match_type == 'Final') & (df.winner == team)].shape[0]
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr, 'title': nt}

def teamAPI(team, matches=ipl_matches):
    df = matches[(matches['team1'] == team) | (matches['team2'] == team)].copy()
    self_record = allRecord(team)
    TEAMS = matches.team1.unique()
    against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
    data = {team: {'overall': self_record, 'against': against}}
    return json.dumps(data, cls=NPEncoder)

# ─── Batting ──────────────────────────────────────────────────────────────────

def batsmanRecord(batsman, df):
    if df.empty:
        return {
            'innings': 0,
            'runs': 0,
            'fours': 0,
            'sixes': 0,
            'avg': np.nan,
            'strikeRate': np.nan,
            'fifties': 0,
            'hundreds': 0,
            'highest_score': '0',
            'notOut': 0,
            'mom': 0
        }
    out = df[df.player_dismissed == batsman].shape[0]
    df = df[df['batter'] == batsman]
    if df.empty:
        return {
            'innings': 0,
            'runs': 0,
            'fours': 0,
            'sixes': 0,
            'avg': np.nan,
            'strikeRate': np.nan,
            'fifties': 0,
            'hundreds': 0,
            'highest_score': '0',
            'notOut': out,
            'mom': 0
        }
    innings = df.match_id.unique().shape[0]
    runs = df.batsman_runs.sum()
    fours = df[(df.batsman_runs == 4)].shape[0]
    sixes = df[(df.batsman_runs == 6)].shape[0]
    if out:
        avg = runs / out
    else:
        avg = np.inf
    nballs = df[~(df.extras_type == 'wides')].shape[0]
    if nballs:
        strike_rate = runs / nballs * 100
    else:
        strike_rate = 0
    gb = df.groupby('match_id').sum()
    fifties = gb[(gb.batsman_runs >= 50) & (gb.batsman_runs < 100)].shape[0]
    hundreds = gb[gb.batsman_runs >= 100].shape[0]
    try:
        highest_score = gb.batsman_runs.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_runs.sort_values(ascending=False).head(1).index[0]
        if (df[df.match_id == hsindex].player_dismissed == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = str(gb.batsman_runs.max()) + '*'
    not_out = innings - out
    mom = df[df.player_of_match == batsman].drop_duplicates('match_id', keep='first').shape[0]
    data = {
        'innings': innings,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strikeRate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highest_score': highest_score,
        'notOut': not_out,
        'mom': mom
    }
    return data

def batsmanVsTeam(batsman, team, df):
    df = df[df.bowling_team == team].copy()
    return batsmanRecord(batsman, df)

def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.inning.isin([1, 2])]
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = ipl_matches.team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'all': self_record,
                  'against': against}
    }
    return json.dumps(data, cls=NPEncoder)

# ─── Bowling ──────────────────────────────────────────────────────────────────

bowler_data = batter_data.copy()

def bowlerRun(row):
    if row['extras_type'] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return row['total_runs']

bowler_data['bowler_run'] = bowler_data.apply(bowlerRun, axis=1)

def bowlerWicket(kind):
    if pd.isna(kind):
        return 0
    if kind in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return 1
    else:
        return 0

bowler_data['isBowlerWicket'] = bowler_data['dismissal_kind'].apply(bowlerWicket)

def bowlerRecord(bowler, df):
    if df.empty:
        return {
            'innings': 0,
            'wicket': 0,
            'economy': np.nan,
            'average': np.nan,
            'avg': np.nan,
            'strikeRate': np.nan,
            'fours': 0,
            'sixes': 0,
            'best_figure': np.nan,
            '3+w': 0,
            'mom': 0
        }
    df = df[df['bowler'] == bowler]
    if df.empty:
        return {
            'innings': 0,
            'wicket': 0,
            'economy': 0,
            'average': np.nan,
            'avg': np.nan,
            'strikeRate': np.nan,
            'fours': 0,
            'sixes': 0,
            'best_figure': np.nan,
            '3+w': 0,
            'mom': 0
        }
    innings = df.match_id.unique().shape[0]
    nballs = df[~df['extras_type'].isin(['wides', 'no_balls'])].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = df[(df.batsman_runs == 4)].shape[0]
    sixes = df[(df.batsman_runs == 6)].shape[0]
    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf
    if wicket:
        strike_rate = nballs / wicket
    else:
        strike_rate = np.nan
    gb = df.groupby('match_id').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]
    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True]) \
                    [['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:
        best_figure = f'{int(best_wicket[0][0])}/{int(best_wicket[0][1])}'
    else:
        best_figure = np.nan
    mom = df[df.player_of_match == bowler].drop_duplicates('match_id', keep='first').shape[0]
    data = {
        'innings': innings,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'avg': avg,
        'strikeRate': strike_rate,
        'fours': fours,
        'sixes': sixes,
        'best_figure': best_figure,
        '3+w': w3,
        'mom': mom
    }
    return data

def bowlerVsTeam(bowler, team, df):
    df = df[df.batting_team == team].copy()
    return bowlerRecord(bowler, df)

def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.inning.isin([1, 2])]
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = ipl_matches.team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'all': self_record,
                 'against': against}
    }
    return json.dumps(data, cls=NPEncoder)