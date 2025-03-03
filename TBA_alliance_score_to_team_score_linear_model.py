import tbapy
from datetime import datetime
import pandas as pd
import keys
from sklearn.linear_model import Ridge

tba = tbapy.TBA(keys.tba)

# Change this event key to whatever event you want :).
event_key = "2025camb"

event_teams = tba.event_teams(str(event_key))
teams = []
for team in event_teams:
    teams.append(team['key'])

matches = tba.event_matches(event_key)

team_cols = [f't_{t}' for t in teams]
score_cols = ['autoCoralPoints', 'netAlgaeCount','teleopCoralPoints', 'endGameBargePoints']

rows = []
for match in matches:
    row = {f't_{t}': 0 for t in teams}

    for t in match['alliances']['blue']['team_keys']:
        row[f't_{t}'] = 1
    row['autoCoralPoints']    = match['score_breakdown']['blue']['autoCoralPoints']
    row['netAlgaeCount']      = match['score_breakdown']['blue']['netAlgaeCount']
    row['teleopCoralPoints']  = match['score_breakdown']['blue']['teleopCoralPoints']
    row['endGameBargePoints'] = match['score_breakdown']['blue']['endGameBargePoints']
    rows.append(row)

for match in matches:
    row = {f't_{t}': 0 for t in teams}

    for t in match['alliances']['red']['team_keys']:
        row[f't_{t}'] = 1
    row['autoCoralPoints']    = match['score_breakdown']['blue']['autoCoralPoints']
    row['netAlgaeCount']      = match['score_breakdown']['blue']['netAlgaeCount']
    row['teleopCoralPoints']  = match['score_breakdown']['blue']['teleopCoralPoints']
    row['endGameBargePoints'] = match['score_breakdown']['blue']['endGameBargePoints']
    rows.append(row)

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

print(team_perf)
