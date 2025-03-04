# tba-helper-scripts
The Blue Alliance (FRC data website) gives some pretty awesome data, but it's sometimes isn't as clear / isn't as helpful so here are some scripts to make it more helpful

## Create a keys.py file
Place keys.py file in the same directory and fill it with your TBA key you can get it from https://www.thebluealliance.com/account

## TBA_alliance_score_to_team_score_linear_model:
* Event selection:
Currently this is set up to predict based on a singlur event, you can obviously get much more accurate data if you include more than 1 event (maybe?) depends on if the team did major changes between events.

* TODO
- Increase granularity in Data because it will prob increase accuracy significantly.
- Make some deductions based on data.
- Include penalties
- Endless optimizations to think about.

## scouting_to_google_sheet
* Make sure to follow the instructions for gspread.