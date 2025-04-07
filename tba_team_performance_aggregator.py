import tbapy
from datetime import datetime
import pandas as pd
import gspread
import keys
from sklearn.linear_model import Ridge
import time

tba = tbapy.TBA(keys.tba)
gc = gspread.service_account(filename="secrets.json")

# Define score columns globally
score_cols = ['adjustPoints', 'algaePoints', 'autoBonusAchieved', 'autoCoralCount', 'autoCoralPoints', 
              'autoLineRobot1', 'autoLineRobot2', 'autoLineRobot3', 'autoMobilityPoints', 'autoPoints', 
              'autoReef', 'bargeBonusAchieved', 'coopertitionCriteriaMet', 'coralBonusAchieved', 
              'endGameBargePoints', 'endGameRobot1', 'endGameRobot2', 'endGameRobot3', 'foulCount', 
              'foulPoints', 'g206Penalty', 'g410Penalty', 'g418Penalty', 'g428Penalty', 'netAlgaeCount', 
              'rp', 'techFoulCount', 'teleopCoralCount', 'teleopCoralPoints', 'teleopPoints', 
              'teleopReef', 'totalPoints', 'wallAlgaeCount']

def convert_to_numeric(value):
    if isinstance(value, dict):
        # For dictionary values (like robot positions), return 1 if any value is 'Yes'
        return 1 if any(v == 'Yes' for v in value.values()) else 0
    elif isinstance(value, str):
        if value.lower() == 'yes':
            return 1
        elif value.lower() == 'no':
            return 0
        try:
            return float(value)
        except ValueError:
            return 0
    elif value is None:
        return 0
    return value

def calculate_team_performance(event_key):
    try:
        event_teams = tba.event_teams(str(event_key))
        teams = [team['key'] for team in event_teams]
        
        matches = tba.event_matches(event_key)
        if not matches:
            print(f"No matches found for event {event_key}")
            return None
            
        team_cols = [f't_{t}' for t in teams]
        
        rows = []
        for match in matches:
            if 'score_breakdown' not in match or not match['score_breakdown']:
                continue
                
            # Blue alliance
            row = {f't_{t}': 0 for t in teams}
            for t in match['alliances']['blue']['team_keys']:
                row[f't_{t}'] = 1

            for col in score_cols:
                value = match['score_breakdown']['blue'].get(col, 0)
                row[col] = convert_to_numeric(value)
            rows.append(row)
            
            # Red alliance
            row = {f't_{t}': 0 for t in teams}
            for t in match['alliances']['red']['team_keys']:
                row[f't_{t}'] = 1
            for col in score_cols:
                value = match['score_breakdown']['red'].get(col, 0)
                row[col] = convert_to_numeric(value)
            rows.append(row)
        
        if not rows:
            print(f"No valid match data found for event {event_key}")
            return None
            
        df = pd.DataFrame(rows)
        
        # Ensure all columns exist
        for col in team_cols + score_cols:
            if col not in df.columns:
                df[col] = 0
        
        x = df[team_cols]
        y = df[score_cols]
        
        # Train models for each component
        models = {}
        for comp in score_cols:
            model = Ridge(alpha=1.0, fit_intercept=False)
            model.fit(x, y[comp])
            models[comp] = model
        
        # Get team performance
        team_perf = pd.DataFrame({
            'team': [t.replace('t_', '') for t in team_cols]
        })
        for comp, model in models.items():
            team_perf[comp] = model.coef_
        
        return team_perf
        
    except Exception as e:
        print(f"Error in calculate_team_performance for event {event_key}: {str(e)}")
        return None

# Open the scouting sheet
scouting_sheet = gc.open("Scouting Sheet - Pre Qualifier").sheet1

# Create new spreadsheet for performance analysis
try:
    performance_sheet = gc.open("Team Performance Analysis").sheet1
except gspread.exceptions.SpreadsheetNotFound:
    performance_sheet = gc.create("Team Performance Analysis").sheet1

# Get all team numbers from the scouting sheet
team_numbers = []
for x in range(3, 51):  # Assuming same range as original script
    team_number = scouting_sheet.acell(f'A{x}').value
    if team_number and team_number.strip():  # Only add non-empty values
        team_numbers.append(team_number)

# Create headers in the performance sheet
headers = [['Team', 'Event'] + score_cols]
performance_sheet.update(range_name='A1', values=headers)

current_row = 2
for team_number in team_numbers:
    print(f"Processing team {team_number}...")
    events = tba.team_events(int(team_number), 2025)  # Changed to 2024
    
    for event in events:
        event_key = event['key']
        try:
            team_perf = calculate_team_performance(event_key)
            if team_perf is not None:
                team_data = team_perf[team_perf['team'] == f'frc{team_number}'].iloc[0]
                
                # Write to sheet
                row_data = [[
                    team_number,
                    event_key
                ] + [team_data[col] for col in score_cols]]
                performance_sheet.update(range_name=f'A{current_row}', values=row_data)
                current_row += 1
            
        except Exception as e:
            print(f"Error processing team {team_number} at event {event_key}: {str(e)}")
        
        time.sleep(5)  # Rate limiting for TBA API

print("Analysis complete!") 