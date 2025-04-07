import tbapy
from datetime import datetime
import pandas as pd
import gspread
import keys
import time

tba = tbapy.TBA(keys.tba)

gc = gspread.service_account(filename="secrets.json")

current_dateTime = datetime.now()
matches = tba.team_matches(581, year=2025)

#Example Scouting sheet: https://imgur.com/a/TVyDZ70

wks = gc.open("Scouting Sheet - Pre Qualifier").sheet1

wks.update_acell("B1", str(current_dateTime))

for x in range (3, 51):
    team_number_row = 'A' + str(x)
    team_name_row   = 'B' + str(x)
    team_event_1    = 'C' + str(x)
    team_event_2    = 'D' + str(x)
    team_event_3    = 'E' + str(x)
    win_loss        = 'F' + str(x)
    team_event_4    = 'H' + str(x)
    team_number = wks.acell(team_number_row).value
    team = tba.team('frc'+str(team_number))
    try:
        wks.update_acell(team_name_row, team['nickname'])
    except:
        try:
            wks.update_acell(team_name_row, team['name'])
        except:
            print(KeyError)
            None
    i = 0
    events = tba.team_events(int(team_number), 2025)
    wins = 0
    matches = 0
    for event in events:
        i += 1
        key = event['key']
        try:
            status = tba.team_status(int(team_number), key)
        except:
            None
        if (i == 1):
            try:
                wks.update_acell(team_event_1, str(status['qual']['ranking']['record']))
                wins += int(status['qual']['ranking']['record']['wins'])
                matches += wins + int(status['qual']['ranking']['record']['losses']) + int(status['qual']['ranking']['record']['ties'])
            except:
                None
        
        if (i == 2):
            try:
                wks.update_acell(team_event_2, str(status['qual']['ranking']['record']))
                wins += int(status['qual']['ranking']['record']['wins'])
                matches += wins + int(status['qual']['ranking']['record']['losses']) + int(status['qual']['ranking']['record']['ties'])
            except:
                None

        if (i == 3):
            try:
                wks.update_acell(team_event_3, str(status['qual']['ranking']['record']))
                wins += int(status['qual']['ranking']['record']['wins'])
                matches += wins + int(status['qual']['ranking']['record']['losses']) + int(status['qual']['ranking']['record']['ties'])
            except:
                None
        wks.update_acell(win_loss, str(wins) + str('/' + str(matches)))
        if (i == len(events)):
            try:
                wks.update_acell(team_event_4, str(status['overall_status_str']))
            except:
                continue 
        if i > 3:
            continue
        time.sleep(5)
