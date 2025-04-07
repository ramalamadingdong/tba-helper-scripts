import tbapy
from datetime import datetime
import pandas as pd
import keys
from sklearn.linear_model import Ridge
import gspread

tba = tbapy.TBA(keys.tba)

# Initialize Google Sheets
gc = gspread.service_account(filename="secrets.json")

# Change this event key to whatever event you want :).
event_key = "2025mnum"

event_teams = tba.event_teams(str(event_key))
teams = []
for team in event_teams:
    teams.append(team['key'])

matches = tba.event_matches(event_key)

team_cols = [f't_{t}' for t in teams]
score_cols = ['autoCoralPoints', 'netAlgaeCount','teleopCoralPoints', 'endGameBargePoints', 'totalPoints']

rows = []
for match in matches:
    # Skip matches without score breakdown data
    if match['score_breakdown'] is None:
        print(f"Skipping match {match['key']} - no score data available")
        continue
        
    row = {f't_{t}': 0 for t in teams}

    for t in match['alliances']['blue']['team_keys']:
        row[f't_{t}'] = 1
    row['autoCoralPoints']    = match['score_breakdown']['blue']['autoCoralPoints']
    row['netAlgaeCount']      = match['score_breakdown']['blue']['netAlgaeCount']
    row['teleopCoralPoints']  = match['score_breakdown']['blue']['teleopCoralPoints']
    row['endGameBargePoints'] = match['score_breakdown']['blue']['endGameBargePoints']
    row['totalPoints']        = match['score_breakdown']['blue']['totalPoints']

    rows.append(row)

for match in matches:
    # Skip matches without score breakdown data
    if match['score_breakdown'] is None:
        continue
        
    row = {f't_{t}': 0 for t in teams}

    for t in match['alliances']['red']['team_keys']:
        row[f't_{t}'] = 1
    row['autoCoralPoints']    = match['score_breakdown']['red']['autoCoralPoints']
    row['netAlgaeCount']      = match['score_breakdown']['red']['netAlgaeCount']
    row['teleopCoralPoints']  = match['score_breakdown']['red']['teleopCoralPoints']
    row['endGameBargePoints'] = match['score_breakdown']['red']['endGameBargePoints']
    row['totalPoints']        = match['score_breakdown']['red']['totalPoints']
    rows.append(row)

# Check if we have any data to process
if not rows:
    print("No match data available with scores. Try a different event or wait for matches to be played.")
    exit()

df = pd.DataFrame(rows)

x = df[team_cols]
y = df[score_cols]

# --- Model Training ---
# Train models for each component
models = {}

for comp in score_cols:
    model = Ridge(alpha=1.0, fit_intercept=False)
    model.fit(x, y[comp])
    models[comp] = model

# Combine results
team_perf = pd.DataFrame({
    'team': [t.replace('t_', '') for t in team_cols]
})
for comp, model in models.items():
    team_perf[comp] = model.coef_

# Print results to console
print(team_perf)

# Create or open a Google Sheet
try:
    sheet = gc.open("Scouting Sheet - Pre Qualifier")
except gspread.exceptions.SpreadsheetNotFound:
    sheet = gc.create(f"Team Performance - {event_key}")

# Get the first worksheet
worksheet = None
if worksheet is None:
    worksheet = sheet.add_worksheet(title="Team Performance", rows=100, cols=20)

# Update the sheet with headers
headers = ['Team'] + score_cols
worksheet.update(values=[headers], range_name='A1')

# Update the sheet with data
data = [team_perf['team'].tolist()]
for col in score_cols:
    data.append(team_perf[col].tolist())
data = list(zip(*data))  # Transpose the data
worksheet.update(values=data, range_name=f'A2:Z{len(data)+1}')

print(f"Results have been uploaded to Google Sheet: Team Performance - {event_key}")
