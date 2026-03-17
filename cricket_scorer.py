import json
import os
import getpass
import time
from datetime import datetime

class Player:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.balls_faced = 0
        self.wickets = 0  # if bowler
        self.overs_bowled = 0
        self.runs_conceded = 0
        self.is_out = False

class Team:
    def __init__(self, name, captain, players):
        self.name = name
        self.captain = captain
        self.players = [Player(p) for p in players]
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0

class Match:
    def __init__(self, match_type, team_a, team_b):
        self.match_type = match_type  # 'Test'
        self.team_a = team_a
        self.team_b = team_b
        self.current_innings = 0  # 0 for team_a, 1 for team_b
        self.current_over = 0
        self.current_ball = 0
        self.current_bowler = None
        self.current_striker = None
        self.current_non_striker = None
        self.current_over_balls = []
        self.match_log = []
        self.start_time = time.time()
        self.paused_time = 0
        self.target = None
        self.series = {self.team_a.name: 0, self.team_b.name: 0}
        self.continuation_level = 0
        self.last_delta = {'runs': 0, 'wickets': 0, 'over_ball': None, 'ball_incremented': False, 'log_entry': None, 'swap': False, 'new_striker': None, 'old_striker': None, 'bowler_wickets': 0}

    def get_current_team(self):
        return self.team_a if self.current_innings == 0 else self.team_b

    def get_opposite_team(self):
        return self.team_b if self.current_innings == 0 else self.team_a

    def save_state(self, filename, password):
        data = {
            'password': password,
            'match_type': self.match_type,
            'team_a': {
                'name': self.team_a.name,
                'captain': self.team_a.captain,
                'players': [{'name': p.name, 'runs': p.runs, 'balls_faced': p.balls_faced, 'wickets': p.wickets, 'overs_bowled': p.overs_bowled, 'runs_conceded': p.runs_conceded, 'is_out': p.is_out} for p in self.team_a.players],
                'score': self.team_a.score,
                'wickets': self.team_a.wickets,
                'overs': self.team_a.overs,
                'balls': self.team_a.balls
            },
            'team_b': {
                'name': self.team_b.name,
                'captain': self.team_b.captain,
                'players': [{'name': p.name, 'runs': p.runs, 'balls_faced': p.balls_faced, 'wickets': p.wickets, 'overs_bowled': p.overs_bowled, 'runs_conceded': p.runs_conceded, 'is_out': p.is_out} for p in self.team_b.players],
                'score': self.team_b.score,
                'wickets': self.team_b.wickets,
                'overs': self.team_b.overs,
                'balls': self.team_b.balls
            },
            'current_innings': self.current_innings,
            'current_over': self.current_over,
            'current_ball': self.current_ball,
            'current_bowler': self.current_bowler.name if self.current_bowler else None,
            'current_striker': self.current_striker.name if self.current_striker else None,
            'current_non_striker': self.current_non_striker.name if self.current_non_striker else None,
            'current_over_balls': self.current_over_balls,
            'match_log': self.match_log,
            'last_delta': self.last_delta,
            'start_time': self.start_time,
            'paused_time': self.paused_time,
            'target': self.target,
            'series': self.series,
            'continuation_level': self.continuation_level
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_state(cls, filename, password):
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            data = json.load(f)
        if data['password'] != password:
            return None
        team_a_data = data['team_a']
        team_a = Team(team_a_data['name'], team_a_data['captain'], [p['name'] for p in team_a_data['players']])
        for i, p in enumerate(team_a.players):
            p.runs = team_a_data['players'][i]['runs']
            p.balls_faced = team_a_data['players'][i]['balls_faced']
            p.wickets = team_a_data['players'][i]['wickets']
            p.overs_bowled = team_a_data['players'][i]['overs_bowled']
            p.runs_conceded = team_a_data['players'][i]['runs_conceded']
            p.is_out = team_a_data['players'][i].get('is_out', False)
        team_a.score = team_a_data['score']
        team_a.wickets = team_a_data['wickets']
        team_a.overs = team_a_data['overs']
        team_a.balls = team_a_data['balls']

        team_b_data = data['team_b']
        team_b = Team(team_b_data['name'], team_b_data['captain'], [p['name'] for p in team_b_data['players']])
        for i, p in enumerate(team_b.players):
            p.runs = team_b_data['players'][i]['runs']
            p.balls_faced = team_b_data['players'][i]['balls_faced']
            p.wickets = team_b_data['players'][i]['wickets']
            p.overs_bowled = team_b_data['players'][i]['overs_bowled']
            p.runs_conceded = team_b_data['players'][i]['runs_conceded']
            p.is_out = team_b_data['players'][i].get('is_out', False)
        team_b.score = team_b_data['score']
        team_b.wickets = team_b_data['wickets']
        team_b.overs = team_b_data['overs']
        team_b.balls = team_b_data['balls']

        match = cls(data['match_type'], team_a, team_b)
        match.current_innings = data['current_innings']
        match.current_over = data['current_over']
        match.current_ball = data['current_ball']
        match.current_bowler = next((p for p in (team_b.players if match.current_innings == 0 else team_a.players) if p.name == data['current_bowler']), None) if data['current_bowler'] else None
        match.current_striker = next((p for p in (team_a.players if match.current_innings == 0 else team_b.players) if p.name == data['current_striker']), None) if data['current_striker'] else None
        match.current_non_striker = next((p for p in (team_a.players if match.current_innings == 0 else team_b.players) if p.name == data['current_non_striker']), None) if data['current_non_striker'] else None
        match.current_over_balls = data.get('current_over_balls', [])
        match.match_log = data['match_log']
        match.last_delta = data.get('last_delta', {'runs': 0, 'wickets': 0, 'over_ball': None, 'ball_incremented': False, 'log_entry': None, 'swap': False, 'new_striker': None, 'old_striker': None, 'bowler_wickets': 0})
        match.start_time = data['start_time']
        match.paused_time = data['paused_time']
        match.target = data.get('target', None)
        match.series = data.get('series', {match.team_a.name: 0, match.team_b.name: 0})
        match.continuation_level = data.get('continuation_level', 0)
        return match

def get_password():
    return getpass.getpass("Enter password: ")

def find_player_by_name(players, name):
    """Find a player by name (case-insensitive). Returns the player object or None."""
    name_lower = name.lower()
    for p in players:
        if p.name.lower() == name_lower:
            return p
    return None

def get_player_names_lower(players):
    """Get list of player names in lowercase for validation."""
    return [p.name.lower() for p in players]

def create_new_match():
    match_type = 'Test'

    print("Team A:")
    players_a = []
    player_count = 1
    while True:
        player = input(f"Player {player_count} (or press Enter to finish): ").strip()
        if not player:
            break
        players_a.append(player)
        player_count += 1
    
    captain_a = input("Enter captain from the players: ").strip()
    while captain_a.lower() not in [p.lower() for p in players_a]:
        captain_a = input("Invalid. Enter captain from the players: ").strip()

    print("Team B:")
    players_b = []
    player_count = 1
    while True:
        player = input(f"Player {player_count} (or press Enter to finish): ").strip()
        if not player:
            break
        players_b.append(player)
        player_count += 1
    
    captain_b = input("Enter captain from the players: ").strip()
    while captain_b.lower() not in [p.lower() for p in players_b]:
        captain_b = input("Invalid. Enter captain from the players: ").strip()

    overs = None
    if match_type == 'Normal':
        overs = int(input("Number of overs: "))

    team_a = Team("Team A", captain_a, players_a)
    team_b = Team("Team B", captain_b, players_b)

    # Set initial players
    striker = input("Enter striker (batsman on strike): ").strip()
    while striker.lower() not in [p.lower() for p in players_a]:
        striker = input("Invalid. Enter striker from Team A players: ").strip()

    non_striker = input("Enter non-striker (runner): ").strip()
    while non_striker.lower() not in [p.lower() for p in players_a] or non_striker.lower() == striker.lower():
        non_striker = input("Invalid. Enter non-striker from Team A players, different from striker: ").strip()

    bowler = input("Enter bowler: ").strip()
    while bowler.lower() not in [p.lower() for p in players_b]:
        bowler = input("Invalid. Enter bowler from Team B players: ").strip()

    match = Match(match_type, team_a, team_b)
    match.current_striker = find_player_by_name(team_a.players, striker)
    match.current_non_striker = find_player_by_name(team_a.players, non_striker)
    match.current_bowler = find_player_by_name(team_b.players, bowler)
    return match

def play_ball(match):
    team = match.get_current_team()
    print(f"\nOver {match.current_over + 1}, Ball {match.current_ball + 1}")
    print(f"{team.name} - {team.score}/{team.wickets}")
    bowler_name = match.current_bowler.name if match.current_bowler else 'None'
    batsman_name = match.current_striker.name if match.current_striker else 'None'
    print(f"Bowler: {bowler_name} to Batsman: {batsman_name}")
    over_display = " | ".join(f"|{b}|" for b in match.current_over_balls) if match.current_over_balls else "| | | | | |"
    print(f"Over: {over_display}")

    # Batter stats
    if match.current_striker:
        print(f"Striker: {match.current_striker.name} ({match.current_striker.runs} runs, {match.current_striker.balls_faced} balls)")
    if match.current_non_striker:
        print(f"Non-striker: {match.current_non_striker.name} ({match.current_non_striker.runs} runs, {match.current_non_striker.balls_faced} balls)")

    # Bowler stats
    if match.current_bowler:
        wickets = match.current_bowler.wickets
        runs_conceded = match.current_bowler.runs_conceded
        balls_bowled = match.current_bowler.overs_bowled * 6
        print(f"Bowler: {match.current_bowler.name} ({wickets} wickets, {runs_conceded} runs conceded, {balls_bowled} balls)")

    option = input("Enter option (Run/Dot/Wicket/Wide/No ball/Rollback/Declare/Add player): ").strip().capitalize()
    while option not in ['Run', 'Dot', 'Wicket', 'Wide', 'No ball', 'Rollback', 'Declare', 'Add player']:
        option = input("Invalid. Enter Run, Dot, Wicket, Wide, No ball, Rollback, Declare, or Add player: ").strip().capitalize()

    if option == 'Run':
        run_type = input("Enter run type (1/4/Bye): ").strip()
        while run_type not in ['1', '4', 'Bye']:
            run_type = input("Invalid. Enter 1, 4, or Bye: ").strip()
        runs = int(run_type) if run_type != 'Bye' else 0
        if run_type == 'Bye':
            runs = int(input("Enter runs for bye: "))
        team.score += runs
        if match.current_striker:
            match.current_striker.runs += runs
            match.current_striker.balls_faced += 1
        if run_type == '1':
            # Swap striker and non-striker
            match.current_striker, match.current_non_striker = match.current_non_striker, match.current_striker
        if match.current_bowler:
            match.current_bowler.runs_conceded += runs
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: {run_type} run(s)")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        match.current_over_balls.append(run_type)

    elif option == 'Dot':
        dot_type = input("Enter dot type (Bye/0): ").strip().capitalize()
        while dot_type not in ['Bye', '0']:
            dot_type = input("Invalid. Enter Bye or 0: ").strip().capitalize()
        if dot_type == 'Bye':
            runs = int(input("Enter runs for bye: "))
            team.score += runs
            match.current_over_balls.append('LB')
        else:
            runs = 0
            match.current_over_balls.append('0')
        if match.current_striker:
            match.current_striker.balls_faced += 1
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: Dot ({dot_type})")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")

    elif option == 'Wicket':
        wicket_type = input("Enter wicket type (Slip/Catch/Bowled/Run out): ").strip().capitalize()
        while wicket_type not in ['Slip', 'Catch', 'Bowled', 'Run out']:
            wicket_type = input("Invalid. Enter Slip, Catch, Bowled, or Run out: ").strip().capitalize()
        team.wickets += 1
        if match.current_bowler:
            match.current_bowler.wickets += 1
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: Wicket ({wicket_type})")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        # Mark current striker as out
        if match.current_striker:
            match.current_striker.is_out = True
        # Prompt for new batsman
        available_batsmen = [p.name for p in team.players if not p.is_out and p != match.current_non_striker]
        new_batsman = None
        if available_batsmen:
            print(f"Available batsmen: {', '.join(available_batsmen)}")
            new_batsman = input("Enter new batsman: ").strip()
            while new_batsman.lower() not in [p.lower() for p in available_batsmen]:
                new_batsman = input("Invalid. Enter new batsman from available: ").strip()
            match.current_striker = find_player_by_name(team.players, new_batsman)
        else:
            print("No more batsmen available.")
        match.current_over_balls.append('W')

    elif option == 'Wide':
        extra_runs = 0
        team.score += extra_runs
        if match.current_bowler:
            match.current_bowler.runs_conceded += extra_runs
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: Wide")
        print(f"Extra runs for Wide: {extra_runs}")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        match.current_over_balls.append('WD')

    elif option == 'No ball':
        extra_runs = 0
        team.score += extra_runs
        if match.current_bowler:
            match.current_bowler.runs_conceded += extra_runs
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: No ball")
        print(f"Extra runs for No ball: {extra_runs}")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        match.current_over_balls.append('NB')

    elif option == 'Declare':
        if match.current_innings == 0 and team.wickets == 0:
            print(f"Declared. {team.name} scored {team.score}.")
            match.target = team.score + 1
            print(f"Target for {match.get_opposite_team().name}: {match.target}")
            match.match_log.append(f"Declared at {team.score} runs.")
            comment = input("Write something or press enter to cancel: ").strip()
            if comment:
                match.match_log.append(f"Comment: {comment}")
            # Start second innings
            match.current_innings = 1
            match.current_over = 0
            match.current_ball = 0
            match.current_over_balls = []
            bowling = match.get_opposite_team()
            bowling.score = 0
            bowling.wickets = 0
            bowling.overs = 0
            bowling.balls = 0
            for p in bowling.players:
                p.is_out = False
                p.runs = 0
                p.balls_faced = 0
            striker = input(f"Enter striker for second innings (from {bowling.name}): ").strip()
            while striker.lower() not in [p.lower() for p in [p.name for p in bowling.players]]:
                striker = input(f"Invalid. Enter striker from {bowling.name} players: ").strip()
            non_striker = input(f"Enter non-striker for second innings (from {bowling.name}): ").strip()
            while non_striker.lower() not in [p.lower() for p in [p.name for p in bowling.players]] or non_striker.lower() == striker.lower():
                non_striker = input(f"Invalid. Enter non-striker from {bowling.name} players, different from striker: ").strip()
            bowler = input(f"Enter bowler for second innings (from {team.name}): ").strip()
            while bowler.lower() not in [p.lower() for p in [p.name for p in team.players]]:
                bowler = input(f"Invalid. Enter bowler from {team.name} players: ").strip()
            match.current_striker = find_player_by_name(bowling.players, striker)
            match.current_non_striker = find_player_by_name(bowling.players, non_striker)
            match.current_bowler = find_player_by_name(team.players, bowler)
        else:
            print("Cannot declare unless in first innings with no wickets fallen.")
            # Don't increment ball or anything

    elif option == 'Add player':
        team_choice = input("Which team to add player to (A/B): ").strip().upper()
        while team_choice not in ['A', 'B']:
            team_choice = input("Invalid. Enter A or B: ").strip().upper()
        
        target_team = match.team_a if team_choice == 'A' else match.team_b
        new_player_name = input(f"Enter new player name for {target_team.name}: ").strip()
        while new_player_name in [p.name for p in target_team.players]:
            new_player_name = input(f"Player already exists. Enter a different name: ").strip()
        
        new_player = Player(new_player_name)
        target_team.players.append(new_player)
        print(f"Player '{new_player_name}' added to {target_team.name}.")

    elif option == 'Rollback':
        team.score -= match.last_delta['runs']
        team.wickets -= match.last_delta['wickets']
        if match.last_delta['over_ball'] and match.current_over_balls:
            match.current_over_balls.pop()
        if match.last_delta['ball_incremented']:
            match.current_ball -= 1
            if match.current_ball < 0:
                match.current_ball = 5
                match.current_over -= 1
                # Undo over end effects
                match.current_striker, match.current_non_striker = match.current_non_striker, match.current_striker
                team.overs -= 1
                if match.current_bowler:
                    match.current_bowler.overs_bowled -= 1
        if match.last_delta['log_entry'] and match.match_log:
            match.match_log.pop()
        if match.last_delta['swap']:
            match.current_striker, match.current_non_striker = match.current_non_striker, match.current_striker
        if match.last_delta['old_striker']:
            match.current_striker = next(p for p in team.players if p.name == match.last_delta['old_striker'])
            match.current_striker.is_out = False
        if match.current_bowler and match.last_delta['bowler_wickets']:
            match.current_bowler.wickets -= match.last_delta['bowler_wickets']
        match.last_delta = {'runs': 0, 'wickets': 0, 'over_ball': None, 'ball_incremented': False, 'log_entry': None, 'swap': False, 'new_striker': None, 'old_striker': None, 'bowler_wickets': 0}
        # Don't increment for rollback

    if option not in ['Wide', 'No ball', 'Rollback', 'Declare', 'Add player']:
        match.current_ball += 1
        if match.current_ball == 6:
            match.current_ball = 0
            match.current_over += 1
            match.current_over_balls = []
            # Swap striker and non-striker at end of over
            match.current_striker, match.current_non_striker = match.current_non_striker, match.current_striker
            team.overs += 1
            if match.current_bowler:
                match.current_bowler.overs_bowled += 1
            
            # Automatically change bowler after every over
            bowling_team = match.get_opposite_team()
            bowler = input(f"Enter new bowler (from {bowling_team.name}): ").strip()
            while bowler.lower() not in [p.lower() for p in [p.name for p in bowling_team.players]]:
                bowler = input(f"Invalid. Enter bowler from {bowling_team.name} players: ").strip()
            match.current_bowler = find_player_by_name(bowling_team.players, bowler)

    if option not in ['Rollback', 'Add player']:
        # set last_delta
        last_delta = {'runs': 0, 'wickets': 0, 'over_ball': None, 'ball_incremented': False, 'log_entry': None, 'swap': False, 'new_striker': None, 'old_striker': None, 'bowler_wickets': 0}
        if option == 'Run':
            last_delta['runs'] = runs
            last_delta['over_ball'] = run_type
            last_delta['ball_incremented'] = True
            last_delta['log_entry'] = f"Ball {match.current_over+1}.{match.current_ball+1}: {run_type} run(s)"
            if run_type == '1':
                last_delta['swap'] = True
        elif option == 'Dot':
            last_delta['runs'] = runs  # for bye
            last_delta['over_ball'] = 'LB' if dot_type == 'Bye' else '0'
            last_delta['ball_incremented'] = True
            last_delta['log_entry'] = f"Ball {match.current_over+1}.{match.current_ball+1}: Dot ({dot_type})"
        elif option == 'Wicket':
            last_delta['wickets'] = 1
            last_delta['over_ball'] = 'W'
            last_delta['ball_incremented'] = True
            last_delta['log_entry'] = f"Ball {match.current_over+1}.{match.current_ball+1}: Wicket ({wicket_type})"
            last_delta['old_striker'] = match.current_striker.name
            last_delta['new_striker'] = new_batsman
            last_delta['bowler_wickets'] = 1
        elif option == 'Wide':
            last_delta['over_ball'] = 'WD'
            last_delta['log_entry'] = f"Ball {match.current_over+1}.{match.current_ball+1}: Wide"
        elif option == 'No ball':
            last_delta['over_ball'] = 'NB'
            last_delta['log_entry'] = f"Ball {match.current_over+1}.{match.current_ball+1}: No ball"
        elif option == 'Declare':
            last_delta['log_entry'] = f"Declared at {team.score} runs."
        match.last_delta = last_delta

    elif option == 'Wide':
        team.score += 1
        if match.current_bowler:
            match.current_bowler.runs_conceded += 1
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: Wide")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        # Don't increment ball, re-bowl

    elif option == 'No ball':
        team.score += 1
        if match.current_bowler:
            match.current_bowler.runs_conceded += 1
        match.match_log.append(f"Ball {match.current_over+1}.{match.current_ball+1}: No ball")
        comment = input("Write something or press enter to cancel: ").strip()
        if comment:
            match.match_log.append(f"Comment: {comment}")
        # Don't increment ball, re-bowl


def handle_test_series(match):
    """Handle end-of-innings + series rules.

    Returns True if the match/series should end, or False to continue.
    """
    batting = match.get_current_team()
    bowling = match.get_opposite_team()

    # If chasing team reaches the target before all out, match ends immediately
    if match.current_innings != 0 and match.target is not None and batting.score >= match.target:
        print(f"{batting.name} wins by {len(batting.players) - batting.wickets} wickets!")
        match.series[batting.name] += 1
        if match.series[batting.name] == match.series[bowling.name]:
            print(f"{batting.name} wins the series (stumps tied).")
        return True

    # Inning not complete yet
    if batting.wickets < len(batting.players) - 1:
        return False

    # First innings complete -> set target and start second innings
    if match.current_innings == 0:
        print(f"First innings complete. {batting.name} scored {batting.score}.")
        match.target = batting.score + 1
        print(f"Target for {bowling.name}: {match.target}")
        match.current_innings = 1
        match.current_over = 0
        match.current_ball = 0
        match.current_over_balls = []

        batting.score = 0
        batting.wickets = 0
        batting.overs = 0
        batting.balls = 0
        for p in batting.players:
            p.is_out = False
            p.runs = 0
            p.balls_faced = 0

        striker = input(f"Enter striker for second innings (from {bowling.name}): ").strip()
        while striker.lower() not in [p.lower() for p in [p.name for p in bowling.players]]:
            striker = input(f"Invalid. Enter striker from {bowling.name} players: ").strip()
        non_striker = input(f"Enter non-striker for second innings (from {bowling.name}): ").strip()
        while non_striker.lower() not in [p.lower() for p in [p.name for p in bowling.players]] or non_striker.lower() == striker.lower():
            non_striker = input(f"Invalid. Enter non-striker from {bowling.name} players, different from striker: ").strip()
        bowler = input(f"Enter bowler for second innings (from {batting.name}): ").strip()
        while bowler.lower() not in [p.lower() for p in [p.name for p in batting.players]]:
            bowler = input(f"Invalid. Enter bowler from {batting.name} players: ").strip()

        match.current_striker = find_player_by_name(bowling.players, striker)
        match.current_non_striker = find_player_by_name(bowling.players, non_striker)
        match.current_bowler = find_player_by_name(batting.players, bowler)
        return False

    # Second (or later) innings complete
    lead = (match.target - 1) - batting.score

    # Batting team chased successfully
    if lead < 0:
        print(f"{batting.name} wins by {len(batting.players) - batting.wickets} wickets!")
        match.series[batting.name] += 1
        if match.series[batting.name] == match.series[bowling.name]:
            print(f"{batting.name} wins the series (stumps tied).")
        return True

    # Match tied
    if lead == 0:
        print("Match drawn.")
        if match.series[batting.name] == match.series[bowling.name]:
            print("Series drawn.")
        return True

    # Batting team lost by `lead` runs -> continue chase with lead + 30
    print(f"{bowling.name} leads by {lead} runs.")
    if match.continuation_level > 0:
        print(f"{bowling.name} wins the series.")
        match.series[bowling.name] += 1
        return True
    else:
        match.continuation_level += 1
        new_target = lead + 1
        print(f"{batting.name} must now chase {new_target} to continue the match.")

        batting.score = 0
        batting.wickets = 0
        batting.overs = 0
        batting.balls = 0
        for p in batting.players:
            p.is_out = False
            p.runs = 0
            p.balls_faced = 0

        match.target = new_target
        match.current_over = 0
        match.current_ball = 0
        match.current_over_balls = []

        striker = input(f"Enter striker for the new chase (from {batting.name}): ").strip()
        while striker.lower() not in [p.lower() for p in [p.name for p in batting.players]]:
            striker = input(f"Invalid. Enter striker from {batting.name} players: ").strip()
        non_striker = input(f"Enter non-striker for the new chase (from {batting.name}): ").strip()
        while non_striker.lower() not in [p.lower() for p in [p.name for p in batting.players]] or non_striker.lower() == striker.lower():
            non_striker = input(f"Invalid. Enter non-striker from {batting.name} players, different from striker: ").strip()
        bowler = input(f"Enter bowler for the new chase (from {bowling.name}): ").strip()
        while bowler.lower() not in [p.lower() for p in [p.name for p in bowling.players]]:
            bowler = input(f"Invalid. Enter bowler from {bowling.name} players: ").strip()

        match.current_striker = find_player_by_name(batting.players, striker)
        match.current_non_striker = find_player_by_name(batting.players, non_striker)
        match.current_bowler = find_player_by_name(bowling.players, bowler)
        return False


def main():
    filename = 'cricket_match.json'
    password = get_password()
    match = Match.load_state(filename, password)
    if match is None:
        print("No existing match or wrong password. Creating new match.")
        match = create_new_match()
        password = input("Enter new password: ").strip()
    else:
        print("Match loaded successfully.")

    while True:
        try:
            play_ball(match)

            if handle_test_series(match):
                match.save_state(filename, password)
                break

            match.save_state(filename, password)
        except KeyboardInterrupt:
            print("\nMatch paused.")
            match.paused_time += time.time() - match.start_time
            match.save_state(filename, password)
            break

if __name__ == "__main__":
    main()