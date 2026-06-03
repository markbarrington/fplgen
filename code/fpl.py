import json
import random
import csv

from paths import data_file
from strength import teamstrength

from operator import itemgetter

forecastweeks = 6
transferweeks = 4

# Configuration values for this GameWeek
gameweek = 3
hit = 0
transfersavailable = 1
thisseasonfactor = 100.0

# Global variables

players = []
fixtures = []

typecount = []
currentteam = []
endofplayers = -2
transferpatternslot = -2
chipsslot = -1
boostslot = 0
wildcardslot = 1
tcslot = 2
aooslot = 3

# Configuration values for each type of player

#playertypes = ['Goalkeeper','Defender','Midfielder','Forward']
#squadcount = [2,5,5,3]
#playmin = [1,3,0,1]
#playmax = [1,5,5,3]

# scoreteam depends on this ordering.

playertypes = ['Goalkeeper','Defender','Midfielder','Forward']
#squadcount = [3,5,5,2]
#playmin = [1,0,3,1]
#playmax = [3,5,5,1]
#aaomin = [3,5,2,1]

squadcount = [2,5,5,3]
playmin = [1,3,0,1]
playmax = [1,5,5,3]
aaomin = [1,2,5,3]

# Configuration values for rules

squadsize = 15
maxperteam = 3
startbank = 0
budget = 1000

benchboostchip = False
wildcardchip = False
triplecaptain = False
alloutattack = False

#Team IDs

teamid = {

    '1'  : 'Arsenal',
    '2'  : 'Bournemouth',
    '3'  : 'Burnley',
    '4'  : 'Chelsea',
    '5'  : 'Crystal Palace',
    '6'  : 'Everton',
    '7'  : 'Hull',
    '8'  : 'Leicester',
    '9'  : 'Liverpool',
    '10' : 'Man City',
    '11' : 'Man Utd',
    '12' : 'Middlesbrough',
    '13' : 'Southampton',
    '14' : 'Stoke',
    '15' : 'Sunderland',
    '16' : 'Swansea',
    '17' : 'Spurs',
    '18' : 'Watford',
    '19' : 'West Brom',
    '20' : 'West Ham'

}

playertype = {

    '1' : 'Goalkeeper',
    '2' : 'Defender',
    '3' : 'Midfielder',
    '4' : 'Forward'
}

playerexclude = [
    256,    # Mata - uncertain selection at Man Utd
    389,    # Yedlin - transfer to Spurs - uncertain selection
    100,    # Hennessay - uncertain selection
     83,    # Fabregas - Uncertain selection
    368     # Sigurdsson - uncertain selection
]

# Configuration values for scoring

gamesperseason = 38.0

"""
teamstrength = {

'1' : { # Goalkeeper

'Arsenal'        : 0.94,
'Hull'           : 1.12,
'Bournemouth'    : 0.97,
'Chelsea'        : 0.96,
'Crystal Palace' : 1.17,
'Everton'        : 1.00,
'Burnley'        : 1.12,
'Leicester'      : 0.83,
'Liverpool'      : 0.97,
'Man City'       : 0.89,
'Man Utd'        : 0.97,
'Middlesbrough'  : 1.12,
'Watford'        : 1.07,
'Southampton'    : 1.03,
'Stoke'          : 1.02,
'Sunderland'     : 1.06,
'Swansea'        : 0.91,
'Spurs'          : 1.13,
'West Brom'      : 1.11,
'West Ham'       : 0.67

},

'2' : { # Defender

'Arsenal'        : 0.82,
'Hull'           : 1.27,
'Bournemouth'    : 1.03,
'Chelsea'        : 0.76,
'Crystal Palace' : 1.17,
'Everton'        : 0.97,
'Burnley'        : 1.27,
'Leicester'      : 0.63,
'Liverpool'      : 0.86,
'Man City'       : 0.82,
'Man Utd'        : 1.03,
'Middlesbrough'  : 1.27,
'Watford'        : 1.13,
'Southampton'    : 1.00,
'Stoke'          : 1.14,
'Sunderland'     : 1.13,
'Swansea'        : 1.08,
'Spurs'          : 0.73,
'West Brom'      : 1.15,
'West Ham'       : 0.73

},

'3' : { # Midfielder

'Arsenal'        : 0.84,
'Hull'           : 1.16,
'Bournemouth'    : 1.14,
'Chelsea'        : 0.97,
'Crystal Palace' : 0.97,
'Everton'        : 1.01,
'Burnley'        : 1.16,
'Leicester'      : 0.86,
'Liverpool'      : 0.96,
'Man City'       : 0.97,
'Man Utd'        : 0.87,
'Middlesbrough'  : 1.16,
'Watford'        : 0.97,
'Southampton'    : 1.00,
'Stoke'          : 1.01,
'Sunderland'     : 1.12,
'Swansea'        : 1.01,
'Spurs'          : 0.88,
'West Brom'      : 1.10,
'West Ham'       : 0.87

},

'4' : { # Forward

'Arsenal'        : 0.84,
'Hull'           : 1.19,
'Bournemouth'    : 1.09,
'Chelsea'        : 1.03,
'Crystal Palace' : 1.07,
'Everton'        : 0.92,
'Burnley'        : 1.19,
'Leicester'      : 0.90,
'Liverpool'      : 1.10,
'Man City'       : 0.86,
'Man Utd'        : 0.91,
'Middlesbrough'  : 1.19,
'Watford'        : 0.93,
'Southampton'    : 0.92,
'Stoke'          : 1.07,
'Sunderland'     : 1.07,
'Swansea'        : 1.12,
'Spurs'          : 0.70,
'West Brom'      : 0.91,
'West Ham'       : 0.93

}
}
"""

homeaway = {

'1' : { # Goalkeeper

'Arsenal'        : 0.90,
'Hull'           : 0.72,
'Bournemouth'    : 1.20,
'Chelsea'        : 1.60,
'Crystal Palace' : 0.79,
'Everton'        : 1.81,
'Burnley'        : 0.67,
'Leicester'      : 0.88,
'Liverpool'      : 1.37,
'Man City'       : 1.23,
'Man Utd'        : 0.81,
'Middlesbrough'  : 0.74,
'Watford'        : 0.90,
'Southampton'    : 1.01,
'Stoke'          : 1.00,
'Sunderland'     : 0.58,
'Swansea'        : 0.60,
'Spurs'          : 0.79,
'West Brom'      : 1.13,
'West Ham'       : 0.95

},

'2' : { # Defender

'Arsenal'        : 0.85,
'Hull'           : 0.79,
'Bournemouth'    : 0.96,
'Chelsea'        : 1.21,
'Crystal Palace' : 0.88,
'Everton'        : 1.95,
'Burnley'        : 0.57,
'Leicester'      : 0.86,
'Liverpool'      : 0.98,
'Man City'       : 1.31,
'Man Utd'        : 0.65,
'Middlesbrough'  : 0.58,
'Watford'        : 0.63,
'Southampton'    : 0.84,
'Stoke'          : 0.93,
'Sunderland'     : 0.66,
'Swansea'        : 0.49,
'Spurs'          : 0.68,
'West Brom'      : 1.02,
'West Ham'       : 0.96

},

'3' : { # Midfielder

'Arsenal'        : 0.96,
'Hull'           : 0.88,
'Bournemouth'    : 0.93,
'Chelsea'        : 0.93,
'Crystal Palace' : 0.79,
'Everton'        : 0.94,
'Burnley'        : 0.75,
'Leicester'      : 0.94,
'Liverpool'      : 0.87,
'Man City'       : 0.80,
'Man Utd'        : 0.99,
'Middlesbrough'  : 0.66,
'Watford'        : 1.00,
'Southampton'    : 0.73,
'Stoke'          : 0.82,
'Sunderland'     : 0.82,
'Swansea'        : 0.80,
'Spurs'          : 1.08,
'West Brom'      : 0.90,
'West Ham'       : 0.97

},

'4' : { # Forward

'Arsenal'        : 1.08,
'Hull'           : 0.94,
'Bournemouth'    : 1.03,
'Chelsea'        : 0.95,
'Crystal Palace' : 1.40,
'Everton'        : 0.76,
'Burnley'        : 0.67,
'Leicester'      : 0.94,
'Liverpool'      : 0.97,
'Man City'       : 0.71,
'Man Utd'        : 0.68,
'Middlesbrough'  : 0.98,
'Watford'        : 0.91,
'Southampton'    : 0.81,
'Stoke'          : 1.16,
'Sunderland'     : 1.22,
'Swansea'        : 1.07,
'Spurs'          : 1.17,
'West Brom'      : 0.94,
'West Ham'       : 0.81

}
}

fixtureadds = [

    #["West Ham",        ["24 Apr 14:05","Gameweek 34","Watford (H)"]],
    #["Watford",         ["24 Apr 14:05","Gameweek 34","West Ham (A)"]],
    #["Man Utd",         ["24 Apr 14:05","Gameweek 34","Crystal Palace (H)"]],
    #["Crystal Palace",  ["24 Apr 14:05","Gameweek 34","Man Utd (A)"]],
    #["Arsenal",         ["24 Apr 14:05","Gameweek 34","West Brom (H)"]],
    #["West Brom",       ["24 Apr 14:05","Gameweek 34","Arsenal (A)"]],
    #["West Ham",        ["24 Apr 14:05","Gameweek 37","Man Utd (H)"]],
    #["Man Utd",         ["24 Apr 14:05","Gameweek 37","West Ham (A)"]],
    #["Norwich",         ["24 Apr 14:05","Gameweek 37","Watford (H)"]],
    #["Watford",         ["24 Apr 14:05","Gameweek 37","Norwich (A)"]],
    #["Sunderland",      ["24 Apr 14:05","Gameweek 37","Everton (H)"]],
    #["Everton",         ["24 Apr 14:05","Gameweek 37","Sunderland (A)"]],
    #["Liverpool",       ["24 Apr 14:05","Gameweek 37","Chelsea (H)"]],
    #["Chelsea",         ["24 Apr 14:05","Gameweek 37","Liverpool (A)"]]

]

fixtureremove = [

    #["Crystal Palace", 35 ],
    #["Everton", 35 ],
    #["Norwich", 35 ],
    #["Watford", 35 ]

]

class fpl():

    bank = 0.0

    @staticmethod
    def fplreview_gameweek_columns(fieldnames):
        columns = {}
        missing = []
        for week in range(gameweek, gameweek + forecastweeks):
            candidates = [
                "%s_Pts" % week,
                "GW%s_Pts" % week,
                "GW%s Pts" % week,
                "%s_PTS" % week,
                "GW%s_PTS" % week,
            ]
            found = None
            for candidate in candidates:
                if candidate in fieldnames:
                    found = candidate
                    break
            if found is None:
                missing.append("%s_Pts" % week)
            else:
                columns[week - gameweek + 1] = found

        if missing:
            raise ValueError(
                "Missing required fplreview gameweek columns: %s" % ", ".join(missing)
            )

        return columns

    @staticmethod
    def fplreview_price(value):
        price = float(value)
        if price <= 20:
            price *= 10
        return int(round(price))

    @staticmethod
    def fplreview_position(value):
        position = str(value).strip().lower()
        positions = {
            "1": 1,
            "gk": 1,
            "gkp": 1,
            "goalkeeper": 1,
            "2": 2,
            "def": 2,
            "defender": 2,
            "3": 3,
            "mid": 3,
            "midfielder": 3,
            "4": 4,
            "fwd": 4,
            "for": 4,
            "forward": 4,
        }
        if position not in positions:
            raise ValueError("Unknown fplreview position: %s" % value)
        return positions[position]

    @staticmethod
    def fplreview_team(value):
        global teamid

        team_name = str(value).strip()
        for existing_id, existing_name in teamid.items():
            if existing_name.lower() == team_name.lower():
                return int(existing_id), existing_name

        next_id = max(int(existing_id) for existing_id in teamid.keys()) + 1
        teamid[str(next_id)] = team_name
        return next_id, team_name

    @staticmethod
    def map_fplreview_rows(rows, fieldnames):
        required = ["Pos", "ID", "Name", "BV", "SV", "Team"]
        missing = [field for field in required if field not in fieldnames]
        if missing:
            raise ValueError("Missing required fplreview columns: %s" % ", ".join(missing))

        point_columns = fpl.fplreview_gameweek_columns(fieldnames)
        players = []
        for row in rows:
            players.append(fpl.map_fplreview_player(row, point_columns))
        return players

    @staticmethod
    def map_fplreview_player(row, point_columns):
        player_id = int(row["ID"])
        element_type = fpl.fplreview_position(row["Pos"])
        team, team_name = fpl.fplreview_team(row["Team"])
        now_cost = fpl.fplreview_price(row["BV"])
        sellprice = fpl.fplreview_price(row["SV"])

        player = {
            "id": player_id,
            "code": player_id,
            "second_name": row["Name"],
            "web_name": row["Name"],
            "team": team,
            "team_name": team_name,
            "element_type": element_type,
            "type_name": playertypes[element_type - 1],
            "now_cost": now_cost,
            "sellprice": sellprice,
            "status": "a",
            "picked": False,
            "minutes": 0,
            "total_points": 0,
            "tsp": 0,
            "home": 0,
            "away": 0,
            "homegames": 0,
            "awaygames": 0,
            "otherteams": ["NONE"] * forecastweeks,
        }

        lookahead = 0
        for week, column in point_columns.items():
            points = float(row[column])
            player[str(week)] = points
            lookahead += points

        player["thisweekpoints"] = player["1"]
        player["lookaheadpoints"] = lookahead
        player["ppg"] = lookahead / float(forecastweeks)
        player["total_points"] = lookahead
        player["tsp"] = lookahead

        return player

    @staticmethod
    def load_fplreview_players(filename):
        with open(filename, "r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise ValueError("fplreview CSV has no header row")
            rows = list(reader)
            return fpl.map_fplreview_rows(rows, reader.fieldnames)

    @staticmethod
    def write_playerkeydata(loaded_players):
        output = open(data_file('playerkeydata', for_write=True), 'w', encoding='utf-8-sig')

        for player in loaded_players:
            playerdata = player['second_name']
            playerdata += "," + str(player['total_points'])
            playerdata += "," + str(player['minutes'])
            playerdata += "," + str(player['tsp'])
            playerdata += "," + str(player['now_cost'])
            playerdata += "," + player['team_name']
            playerdata += "," + playertype[str(player['element_type'])]
            playerdata += "," + str(player['lookaheadpoints'])
            playerdata += "," + str(player['thisweekpoints'])
            playerdata += "," + str(player['ppg'])
            for week in range(1,forecastweeks+1):
                playerdata += "," + str(player[str(week)])
            output.write(playerdata + '\n')

        output.close()

    # Read the fplreview export into the player global variable.
    # Output a playerkeydata inspection file.
    @staticmethod
    def getplayerdata(filename=None):
        global players, fixtures

        fixtures = []
        if filename is None:
            filename = data_file('fplreview.csv')

        imported_players = fpl.load_fplreview_players(filename)

        players = imported_players
        fpl.write_playerkeydata(players)

    # Generate a four week lookahead score for a player
    @staticmethod
    def lookaheadpoints(player, currentweek):
        # Get points per game for player during last season
        global players, fixtures

        ppg = fpl.pointspergame(player)


        if gameweek == 1:
            # Boost score for players who play most minutes
            minutes = 0
            games = 38
            # Get last seasons total minutes
            history = fixtures[player['id']-1]['history_past']
            for season in history:
                if season['season_name'] == "2015/16":
                    minutes = season['minutes']
        else:
            # Get minutes and games this season

            minutes = player['minutes']
            games = gameweek - 1

        # Calculate minutes per game
        if games == 0 or minutes == 0:
            minutespergame = 0
        else:
            minutespergame = minutes / float(games)

        # Get points boosts for high minute averages
        minuteboost = 1
        #if gameweek == 1 and minutespergame < 20:
        #    minuteboost = 0.2

        # Player opponents

        player['otherteams'] = []

        # twp - this weeks points
        # lap - look ahead points
        twp = 0
        lap = 0
        # Week scores are weighted in favor of current week
        weekweight = 1
        for week in range(currentweek, currentweek + forecastweeks):
            # Get this weeks fixture
            fixture = "Gameweek " + str(week)
            playerfixtures = fixtures[player['id']-1]['fixtures']

            # Check all the gameweeks looking for this week
            # Assumes each week has no more than one game for the player

            for thisweeksgame in playerfixtures:

                if thisweeksgame['event_name'] == fixture:

                    #removefixture = False
                    #for removegame in fixtureremove:
                    #    if player['team_name'] == removegame[0] and removegame[1] == week:
                    #        removefixture = True

                    #if thisweeksgame[2] != "-" and removefixture == False:

                    # Player has game this week
                    # Find name of opponent
                    otherteam = thisweeksgame['opponent_name']
                    player['otherteams'].append(otherteam)
                    #print otherteam

                    # Calculate strength of opponent for this week
                    sos = fpl.strengthofschedule(str(player['element_type']),player['team'],otherteam)

                    # Set factor for home game vs away game

                    if thisweeksgame['is_home'] == True:
                        home = 2.0 - homeaway[str(player['element_type'])][teamid[str(player['team'])]]
                        if player['homegames'] > 3:
                            ppg = player['home'] / float(player['homegames'])
                        else:
                            ppg = 0
                    else:
                        home = homeaway[str(player['element_type'])][teamid[str(player['team'])]]
                        if player['awaygames'] > 3:
                            ppg = player['away'] / float(player['awaygames'])
                        else:
                            ppg = 0

                    # Set ppg to 0 if player on remove list

                    if player['id'] in playerexclude:
                        ppg = 0

                    # exclude players with zero scores

                    #if ppg == 0:
                    #    player['status'] = 'z'

                    # temp hack - trying per player home v away points.

                    home = 1.0

                    # Points this week is set to
                    #     player points per game *
                    #     strength of opponent *
                    #     home game factor *
                    #     week weighting - set to 1.0, 0.75, 0.5, 0.25
                    ptw = ( ppg * sos * home ) * weekweight
                    ptw = ptw * minuteboost

                    if str(week - currentweek + 1) not in player:
                        player[str(week - currentweek + 1)] = ptw
                    else:
                        player[str(week - currentweek + 1)] += ptw

                    #print player[str(week - currentweek + 1)]

                    # Set this week points for this week
                    if week == currentweek:
                        twp = ptw
                    # Set lookahead points
                    lap += ptw

                    #else:

                    #    player[str(week - currentweek + 1)] = 0
                    #    player['otherteams'].append("NONE")
                    #    #continue

            #weekweight = 0.75

        # Store values in global player variable
        player['thisweekpoints'] = twp
        player['lookaheadpoints'] = lap




    # Calculate points per game for player
    @staticmethod
    def pointspergame(player):
        global players, fixtures

        ppg = 0
        # Get points per game for last season

        history = fixtures[player['id']-1]['history_past']
        for season in history:
            if season['season_name'] == "2015/16":
                ppg = season['total_points'] / float(gamesperseason)

        games = 0
        if gameweek <= 10:
            tsp = player['total_points']
            games = gameweek
        else:
            tsp = 0
            pts = []
            fixtures = player['fixture_history']['all']
            for fixture in fixtures:
                if fixture[1] >= gameweek - 10:
                    tsp += fixture[19]
                    pts.append(fixture[19])
                    games += 1
            if games < 8:                       # count for blank fixtures but not new players
                games = 8
            average = tsp / 10.0
            tsp = 0
            for pt in pts:
                if pt > (average * 2.0):
                    pt = average * 2.0
                tsp += pt

        # Add in points per game for this season
        # Apply factor to increase relevance of this seasons games
        if gameweek != 1:
            # 10% weight for this season in gameweek 2
            # 20% weight for this season in gameweek 3
            # 40% weight for this season in gameweek 4
            # 60% weight for this season in gameweek 5
            # 80% weight for this season in gameweek 6
            # 90% weight for this season in gameweek 7, 8, 9, 10
            # 100% weight for week 11 on
            factor = 1.0
            ppg = (ppg*(1-factor)) + (factor * (tsp / games))

        player['tsp'] = tsp
        player['ppg'] = ppg

        #if player['status'] != "a":
        #    ppg = 0

        return ppg

    # Calculate strength of opponent
    # Uses teamstrength list. Based on weighted average season end position
    #     for last three seasons
    @staticmethod
    def strengthofschedule(playertype, playerteam, otherteam):
        # Calculate relative strength of opponents (+1 -> -1)
        # Normalise to be in the range 0 - 1.0
        sos = teamstrength[playertype][otherteam]
        return sos

    # Return a random player from the list of players
    @staticmethod
    def getrandomplayer(replace):

        attempts = 0
        while attempts <= 1000:
            attempts += 1

            player = players[random.randint(0,len(players)-1)]

            if player['status'] != 'a':
                continue

            #if player['now_cost'] > replace['now_cost']:
            #    continue

            if player['element_type'] == replace['element_type']:
                # Add the player to the team
                # print("Replace OK %s" % attempts)

                return player

        print("Replace Failed %s" % attempts)
        return player

    @staticmethod
    def mutatepattern(pattern):

        fixed = False
        if fixed == True:
            pattern = [1,1,1,1,1]
        else:
            pattern = fpl.getrandompattern()

            #transfers = transfersavailable
            #for i, transfer in enumerate(pattern):
            #    if random.random() <= 1.0 / transferweeks:
            #        if transfers == 2:
            #            tf = random.randint(0,2)
            #        else:
            #            tf = random.randint(0,1)
            #    else:
            #        tf = transfer

            #    if tf == 0:
            #        transfers = 2
            #    else:
            #        transfers = 1
            #        if i < (transferweeks-1):
            #            if pattern[i+1] == 2:
            #                pattern[i+1] = 1

            #    transfer = tf
            #    pattern[i] = transfer

        return pattern

    @staticmethod
    def getrandompattern():

        #if transfersavailable == 1:
        #    return transferpatternsone[random.randint(0,len(transferpatternsone)-1)]
        #else:
        #    return transferpatternstwo[random.randint(0,len(transferpatternstwo)-1)]

        fixed = False
        if fixed == True:
            transferpattern = [1,1,1,1,1]
        else:
            transfers = transfersavailable
            transferpattern = []
            transferpattern.append(0) # No transfer in first week
            for i in range(0,transferweeks-1):
                ttw = random.randint(0,transfers)
                transferpattern.append(ttw)
                transfers -= ttw
                if transfers != 2:
                    transfers += 1

        return transferpattern

    @staticmethod
    def getrandomindex(player):
        position = player['type_name']

        if position == 'Goalkeeper':
            maxindex = 2
        elif position == 'Defender' or position == 'Midfielder':
            maxindex = 5
        else:
            maxindex = 3

        return random.randint(1,maxindex)

    @staticmethod
    def mutatechips(chips):

        top = forecastweeks + 1
        if top < 5:
            top = 5
        chips = random.sample(range(1,top+1),4)

        if benchboostchip == False:
            chips[boostslot] = 0
        if wildcardchip == False:
            chips[wildcardslot] = 0
        if triplecaptain == False:
            chips[tcslot] = 0
        if alloutattack == False:
            chips[aooslot] = 0

        return chips

    @staticmethod
    def getrandomchips():

        #strat1 = [2,1,5,0]
        #strat2 = [7,6,4,0]

        #return strat1

        top = forecastweeks + 1
        if top < 5:
            top = 5
        chips = random.sample(range(1,top+1),4)

        if benchboostchip == False:
            chips[boostslot] = 0
        if wildcardchip == False:
            chips[wildcardslot] = 0
        if triplecaptain == False:
            chips[tcslot] = 0
        if alloutattack == False:
            chips[aooslot] = 0

        return chips

    # Generate a team of 15 players
    @staticmethod
    def generateteam():

        team = []
        transferpositions = []

        #for squadmember in currentteam:
        #    team.append(squadmember)
        #fpl.printteam(team,True)
        #print fpl.validteam(team)

        for idx, positionmax in enumerate(squadcount):
            for i in range(positionmax):
                attempts = 0
                while attempts <= 1000:
                    attempts += 1
                    # Get a random player
                    player = players[random.randint(0,len(players)-1)]
                    # Check player is available
                    if player['status'] != 'a':
                        continue
                    # check player is unique to this team
                    unique = True
                    for otherplayer in team:
                        if otherplayer['id'] == player['id']:
                            unique = False
                    if unique == False:
                        continue
                    # Check player is the right type
                    if player['element_type'] != idx + 1:
                        continue
                    # Add the player
                    team.append(player)
                    break
                if attempts > 1000:
                    team.append(player)



        # Add transfer players + wildcard team
        wctransfers = 0
        if wildcardchip == True:
            wctransfers = 15

        transfers = transferweeks + hit + wctransfers
        if transfersavailable == 2:
            transfers += 1

        for i in range(transfers):
            # Loop to find a valid player to add
            # If can't find in 1000 attempts add the last player anyway
            attempts = 0
            while attempts <= 1000:
                attempts += 1
                # Get a random player
                player = players[random.randint(0,len(players)-1)]
                # Check player is available
                if player['status'] != "a":
                    continue
                # Check player is unique to this team
                unique = True
                for otherplayer in team:
                    if otherplayer['code'] == player['code']:
                        unique = False
                if unique == False:
                    continue
                # Add the player as transfer
                team.append(player)
                #transferpositions.append(player['type_name'])
                break
            if attempts > 1000:
                # Failed to find valid player - Add last player
                team.append(player)

        transferpattern = fpl.getrandompattern()
        #if transfersavailable == 1:
        #    transferpattern = transferpatternsone[random.randint(0,len(transferpatternsone)-1)]
        #else:
        #    transferpattern = transferpatternstwo[random.randint(0,len(transferpatternstwo)-1)]

        team.append(transferpattern)

        #strat1 = [2,1,5,0]
        #strat2 = [7,6,4,0]

        #chips = strat1

        chips = fpl.getrandomchips()
        team.append(chips)

        return team


    # Calculate the value of a team in terms of cost
    @staticmethod
    def teamvalue(team):
        teamvalue = 0
        for player in team[:15]:
            teamvalue += player['now_cost']
        return teamvalue

    # Repair team - Checks if team was made invalid by random evolution process
    # Replace invalid teams with a random valid team
    @staticmethod
    def repairteam(team):
        #if fpl.validteam(team) != True:
        #    team = fpl.generateteam()
        return team

    # Check if a team is valid
    @staticmethod
    def validteam(team):

        # No more than 3 players per Club
        teamcount = {}
        #fpl.printteam(team[:15],False)

        for player in team[:15]:

            if player['team'] in teamcount.keys():
                teamcount[player['team']] += 1
            else:
                teamcount[player['team']] = 1

        for club in teamcount:
            if teamcount[club] > 3:
                #fpl.printteam(team[:15],False)
                #print "Too Many From One Club"
                return False

        # Each player only once in each team
        for idx1, player in enumerate(team[:15]):
            for idx2, otherplayer in enumerate(team[:15]):
                if idx1 != idx2:
                    #print endofplayers, idx1, idx2
                    if player['id'] == otherplayer['id']:
                        #fpl.printteam(team[:15],False)
                        #print "Duplicate Player"
                        return False

        # No more than 1000 value (equivalent to 100 budget in game)
        if fpl.teamvalue(team) > budget:
            #fpl.printteam(team[:15],False)
            #print "Team Over Budget ", fpl.teamvalue(team)
            return False

        # Check for right number of each type of player
        for idx, count in enumerate(squadcount):
            clubs = []
            number = 0
            for player in team[:15]:
                if player['element_type'] == idx + 1:
                    number += 1
                    if number > count:
                        #fpl.printteam(team[:15],False)
                        #print "Bad Squad Formation"
                        return False
                    if player['team_name'] in clubs:
                        return False
                    else:
                        clubs.append(player['team_name'])
        # Player must be available
        #   for player in team[:-2]:
        #       if player['status'] != 'a':
        #           return False

        return True

    @staticmethod
    def transfer(team,week,playerindex,display,boostweek,tcweek,aooweek):

        transferplayer = team[playerindex]
        transfertypeindex = playerindex - 15
        playerout = []

        maxpoints = 0
        maxidx = -1
        points = 0

        #display = True

        value = fpl.teamvalue(team[:15])
        if display == True:
            print("Transfer Check")
            print("Player %s" % transferplayer['second_name'].encode('ascii', errors='ignore'))
            print("Team Value %s" % value)

        sortedteam = sorted(team[:15], key=itemgetter(str(week)), reverse=True)
        for player in sortedteam:
            player['picked'] = False
        maxpoints = fpl.score(sortedteam,week,boostweek,tcweek,aooweek)

        count = 1
        for idx, player in enumerate(team[:15]):

            if display == True:
                print("Checking %s" % player['second_name'].encode('ascii', errors='ignore'))

            # Check if they are the same type

            if transferplayer['element_type'] != player['element_type']:
                if display == True:
                    print("Wrong type")
                continue

            # Check if they are in budget

            if transferplayer['now_cost'] > player['sellprice'] + fpl.bank:
                if display == True:
                    print("Too expensive %s %s" % (player['sellprice'], fpl.bank))
                continue

            # Construct the new team with the transfer player
            newteam = team[:]
            newteam[idx] = transferplayer
            if display == True:
                print("New team")
                fpl.printteam(newteam[:endofplayers],False)

            # Check if team is valid and score team

            if fpl.validteam(newteam[:15]) == False:
                if display == True:
                    print("Invalid Team")
                continue

            points = 0
            for i in range(week,forecastweeks+1):
                sortedteam = sorted(newteam[:15], key=itemgetter(str(i)), reverse=True)
                for player in sortedteam:
                    player['picked'] = False
                points += fpl.score(sortedteam,i,boostweek,tcweek,aooweek)
                if display == True:
                    print("New Points %s" % points)

            if points > maxpoints:
                maxidx = idx
                maxpoints = points
                if display == True:
                    print("Max Points %s" % maxpoints)

        if maxidx != -1:
            player = team[maxidx]
            fpl.bank = fpl.bank + player['sellprice'] - transferplayer['now_cost']
            newteam = team[:maxidx]
            newteam.append(transferplayer)
            newteam = newteam + team[maxidx+1:]
            if display == True:
                print("New Team Final")
                fpl.printteam(newteam[:endofplayers],False)
        else:
            newteam = team
            if display == True:
                print("Same Team")
                fpl.printteam(newteam[:endofplayers],False)

        return newteam

    @staticmethod
    def score(team,week,boostweek,tcweek,aooweek,debug=False):

        points = 0
        pickedteam = []
        typecount = [0,0,0,0]

        #for player in players:
        #    player['picked'] = False

        #penalty for defenders playing attackers

        oppattack = []
        oppdefend = []

        aoo = False
        if week == aooweek and alloutattack == True:
            aoo = True
            min = aaomin
        else:
            min = playmin

        # Pick the highest value players that are required to be in the team
        # 1 Goalkeeper, 3 Defenders and 1 Forward = 5 players total
        for idx, count in enumerate(min):
            if count != 0:
                picked = 0
                for player in team[:15]:
                    if player['element_type'] == idx + 1:
                        # Don't pick a defender or goalkeeper against an attacking player
                        skip = False

                        #print teamid[str(player['team'])]
                        if player['element_type'] == 2 or player['element_type'] == 1:
                            if teamid[str(player['team'])] in oppattack:
                                skip = True

                        if player['element_type'] == 4:
                            if teamid[str(player['team'])] in oppdefend:
                                skip = True

                        if skip == False:

                            if player['element_type'] == 4:
                                oppattack.append(player['otherteams'][week-1])
                            if player['element_type'] == 2 or player['element_type'] == 1:
                                oppdefend.append(player['otherteams'][week-1])

                            pickedteam.append(player)
                            picked += 1
                            typecount[idx] += 1
                            player['picked'] = True
                    if picked == count:
                        break

        # Fill in the other 6 players by highest look ahead point score
        if aoo != True:
            playersneeded = 6
            for player in team[:15]:
                if player['picked'] == True:
                    continue

                # Check we don't have more than
                # 1 Goalkeeper, 5 Defenders, 5 Midfielders or 3 Forwards.
                idx = player['element_type'] - 1
                if typecount[idx] == playmax[idx]:
                    continue


                # Don't pick a defender or goalkeeper against an attacking player
                skip = False

                if player['element_type'] == 2 or player['element_type'] == 1:
                    if player['team'] in oppattack:
                        skip = True

                if player['element_type'] == 4:
                    if player['team'] in oppdefend:
                        skip = True

                if skip == False:

                    if player['element_type'] == 4:
                        oppattack.append(player['otherteams'][week-1])

                    if player['element_type'] == 2 or player['element_type'] == 1:
                        oppdefend.append(player['otherteams'][week-1])

                    pickedteam.append(player)
                    playersneeded -= 1
                    typecount[idx] += 1
                    player['picked'] = True

                if playersneeded == 0:
                    break

        if debug:
            print ("Team Score")

        max = 0
        # Score the picked team
        usedcaptain = False
        for player in pickedteam:
            #if player['status'] == 'a':
            points += player[str(week)]
            if debug:
                print (player['second_name'].encode('ascii', errors='ignore'), player[str(week)], points)
            if player[str(week)] > max:
                max = player[str(week)]

        points += max
        if debug:
            print ("Captain points", max, points)

        if week == tcweek and triplecaptain == True:
            points += max
            if debug:
                print ("Triple Captain points", max, points)

        # Score the non-picked players
        # Apply factor to reduce their impact on the overall score

        if week == boostweek and benchboostchip == True:
            factor = 1.0
        else:
            factor = 0.0
        for player in team[:15]:
            if player not in pickedteam:
                if week == boostweek and benchboostchip == True:
                    player['picked'] = True
                if player['status'] == 'a':
                    points += player[str(week)] * factor
                    if debug:
                        print (player['second_name'].encode('ascii', errors='ignore'), player[str(week)], points)

        return points

    # Produce a score for a team
    @staticmethod
    def scoreteam(team,display=False):

        # Check it's a valid team to score
        if fpl.validteam(team) == False:
            #fpl.printteam(team[:-2],True)
            #print("Invalid team")
            return 0

        for player in team[:endofplayers]:
            player['picked'] = False

        transferpattern = team[transferpatternslot]
        boostweek = team[chipsslot][boostslot]
        tcweek = team[chipsslot][tcslot]
        aooweek = team[chipsslot][aooslot]
        wcweek = team[chipsslot][wildcardslot]

        playerindex = 15
        wcindex = playerindex + transferweeks + hit

        fpl.bank = budget - fpl.teamvalue(team)

        points = 0
        for week in range(1,forecastweeks+1):

            pickedteam = []
            typecount = [0,0,0,0]

            if week <= transferweeks and week != 1: # Dont transfer first week for new team generation.
                if week == wcweek and wildcardchip == True:
                    if week != forecastweeks:
                        if team[transferpatternslot][week] == 2:
                            team[transferpatternslot][week] = 1
                    for i in range(0,15):
                        team = fpl.transfer(team,week,wcindex,False,boostweek,tcweek,aooweek)
                        wcindex += 1
                else:
                    transfers = transferpattern[week-1]
                    if hit != 0 and week == 1:
                        transfers += hit
                    for i in range(0,transfers):
                        team = fpl.transfer(team,week,playerindex,False,boostweek,tcweek,aooweek)
                        playerindex += 1

            # Sort the team by week points. Highest to Lowest
            sortedteam = sorted(team[:15], key=itemgetter(str(week)), reverse=True)

            # score the team
            for player in team[:endofplayers]:
                player['picked'] = False
            points += fpl.score(sortedteam,week,boostweek,tcweek,aooweek)
            if week == 1 and hit != 0:
                points -= (4 * hit)

            # Print out the team if needed
            if display == True:
                print("Week %s Gameweek %s" % (week, str(gameweek + week - 1)))
                fpl.printteam(sortedteam,True)
                print("Transfers")
                fpl.printteam(team[15:endofplayers],False)
                print("End Transfers")
                print("Transfer Pattern %s" % team[transferpatternslot])
                print("Chip Weeks %s" % team[chipsslot])
                print("Points", points)

        return points

    # Print out the team
    @staticmethod
    def printteam(team,value):

        for player in team:
            playerdata = player['second_name'].encode('ascii', errors='ignore').decode('ascii')
            playerdata += "," + str(player['total_points'])
            playerdata += "," + str(player['tsp'])
            playerdata += "," + str(player['now_cost'])
            playerdata += "," + player['team_name']
            playerdata += "," + playertype[str(player['element_type'])]
            playerdata += "," + str(player['id'])
            playerdata += "," + "%.2f" % (player['lookaheadpoints'])
            playerdata += "," + "%.2f" % (player['thisweekpoints'])
            for week in range(1,forecastweeks+1):
                playerdata += "," + "%.2f" % (player[str(week)])

            if player['picked'] == True:
                playerdata += ", Picked"

            print (playerdata)

        if value == True:
            print ("Team value %s" % fpl.teamvalue(team))
            print ("Bank %s" % fpl.bank)
