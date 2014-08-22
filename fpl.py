import Individual

import json
import random
from operator import itemgetter

# Configuration values for this GameWeek
gameweek = 2
transfersavailable = 1

# Global variables

players = []
typecount = []

# Configuration values for each type of player

playertypes = ['Goalkeeper','Defender','Midfielder','Forward']
squadcount = [2,5,5,3]
playmin = [1,3,0,1]
playmax = [1,5,5,3]

# Configuration values for rules

squadsize = 15
budget = 1000
maxperteam = 3

# Configuration values for scoring

gamesperseason = 38.0
teamstrength = {
'Man City': 1,
'Chelsea' : 2,
'Arsenal' : 2,
'Liverpool' : 3,
'Man Utd' : 3,
'Spurs' : 3,
'Everton' : 3,
'Stoke' : 6,
'Newcastle' : 6,
'Swansea' : 6,
'Southampton' : 7,
'West Ham' : 8,
'West Brom' : 8,
'Sunderland' : 9,
'Crystal Palace' : 9,
'Aston Villa' : 9,
'Hull' : 10,
'QPR' : 11,
'Burnley' : 12,
'Leicester' : 12 }

class fpl():

    # Read the playerdata into the player global variable. 
    # Output a playerkeydata file
    # Generate the four week lookahead score for each player
    @staticmethod
    def getplayerdata():
        output = open('playerkeydata','w')
        f = open('playerdata','r')

        for line in f:

            # Get the player data
            player = json.loads(line)    
            player['picked'] = False

            # Generate the four week lookahead score for the player
            fpl.lookaheadpoints(player, gameweek)

            # Add to the players global variable  
            players.append(player)

            # Output key data for inspection to a file
            playerdata = player['second_name'].encode('ascii', errors='ignore')
            playerdata += "," + str(player['total_points'])
            playerdata += "," + str(player['now_cost'])
            playerdata += "," + player['team_name']
            playerdata += "," + player['type_name']
            playerdata += "," + str(player['lookaheadpoints'])

            output.write(playerdata + '\n')

        f.close()
        output.close()

    # Generate a four week lookahead score for a player
    @staticmethod
    def lookaheadpoints(player, currentweek):
        # Get points per game for player during last season
        ppg = fpl.pointspergame(player)

        # twp - this weeks points
        # lap - look ahead points
        twp = 0
        lap = 0
        # Week scores are weighted in favor of current week
        weekweight = 1
        for week in range(currentweek, currentweek + 4):
            # Get this weeks fixture
            fixture = "Gameweek " + str(week)
            fixtures = player['fixtures']['all']

            # Check all the gameweeks looking for this week
            # Assumes each week has no more than one game for the player
            gamethisweek = False
            for thisweeksgame in fixtures:
                if thisweeksgame[1] == fixture:
                    gamethisweek = True
                    break

            if gamethisweek == True:

                # Player has game this week
                # Find name of opponent
                split = thisweeksgame[2].find('(')
                otherteam = thisweeksgame[2][0:split-1]
                # Calculate strength of opponent for this week
                sos = fpl.strengthofschedule(player['team_name'],otherteam)

                # Set factor for home game vs away game
                if '(H)' in thisweeksgame[2]:
                    home = 1.0
                else:
                    home = 0.5

                # Points this week is set to
                #     player points per game *
                #     strength of opponent *
                #     home game factor *
                #     week weighting - set to 1.0, 0.75, 0.5, 0.25
                ptw = ( ppg * sos * home ) * weekweight
                # Set this week points for this week
                if week == currentweek:
                    twp = ptw
                # Set lookahead points
                lap += ptw

            weekweight = weekweight - 0.25

        # Boost score for players who play most minutes
        minutes = 0
        games = 38
        # Get last seasons total minutes
        history = player['season_history']
        for season in history:
            if season[0] == "2013/14":
                minutes = season[1]

        # Get minutes and games this season
        # Apply factor to increase relevance of this seasons minutes
        if gameweek != 1:
            minutes += player['minutes'] * 2.0
            games += ((gameweek - 1) * 2.0)
            if player['minutes'] == 0:
                lap = lap / 10.0
                twp = twp / 10.0

        # Calculate minutes per game
        if games == 0 or minutes == 0:
            minutespergame = 0
        else:
            minutespergame = minutes / float(games)

        # Add points boosts for high minute averages
        if minutespergame > 80:
            lap += 3
            twp += 1
        elif minutespergame > 60:
            lap += 1

        # Store values in global player variable
        player['thisweekpoints'] = twp
        player['lookaheadpoints'] = lap

    # Calculate points per game for player
    @staticmethod
    def pointspergame(player):
        ppg = 0
        # Get points per game for last season
        history = player['season_history']
        for season in history:
            if season[0] == "2013/14":
                ppg = season[16] / float(gamesperseason)

        # Add in points per game for this season
        # Apply factor to increase relevance of this seasons games
        if gameweek != 1:
            ppg += ((player['total_points'] / float(gamesperseason) * 2.0))
        
        return ppg

    # Calculate strength of opponent
    # Uses teamstrength list. Based on weighted average season end position
    #     for last three seasons
    @staticmethod
    def strengthofschedule(playerteam, otherteam):
        # Calculate relative strength of opponents (+11 -> -11)
        # Normalise to be in the range 1/22 - 1.0
        sos = teamstrength[otherteam] - teamstrength[playerteam]
        sos += 11
        sos = float(sos) / 22
        return sos

    # Return a random player from the list of players
    @staticmethod
    def getrandomplayer():
        player = players[random.randint(0,len(players)-1)]
        return player

    # Generate a team of 15 players
    @staticmethod
    def generateteam():
        team = []
        teamvalue = 0
        # Loop count times for each type of player required
        for idx, count in enumerate(squadcount):
            for i in range(count):
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
                    # Check the player doesn't take the team over budget
                    if teamvalue + player['now_cost'] > budget:
                        continue
                    # Check the player is the right type
                    if player['type_name'] == playertypes[idx]:
                        # Add the player to the team
                        team.append(player)
                        teamvalue += player['now_cost']
                        break
                if attempts > 1000:
                    # Failed to find valid player - Add last player
                    team.append(player)
                    teamvalue += player['now_cost'] 
        return team

    # Calculate the value of a team in terms of cost
    @staticmethod
    def teamvalue(team):
        teamvalue = 0
        for player in team:
            teamvalue += player['now_cost']
        return teamvalue

    # Repair team - Checks if team was made invalid by random evolution process
    # Replace invalid teams with a random valid team
    @staticmethod
    def repairteam(team):
        if fpl.validteam(team) != True:
            team = fpl.generateteam()
        return team

    # Check if a team is valid
    @staticmethod
    def validteam(team):

        # No more than 3 players per Club
        teamcount = {}
        for player in team:
            if player['team_name'] in teamcount.keys():
                teamcount[player['team_name']] += 1
            else:
                teamcount[player['team_name']] = 1

        for club in teamcount:
            if teamcount[club] > 3:
                return False

        # Each player only once in each team
        for idx1, player in enumerate(team):
            for idx2, otherplayer in enumerate(team):
                if idx1 != idx2:
                    if player['code'] == otherplayer['code']:
                        return False

        # No more than 1000 value (equivalent to 100 budget in game)
        if fpl.teamvalue(team) > budget:
            return False

        # Check for right number of each type of player 
        for idx, count in enumerate(squadcount):
            number = 0
            for player in team:
                if player['type_name'] == playertypes[idx]:
                    number += 1
                    if number > count:
                        return False               

        # Player must be available
        for player in team:
            if player['status'] != 'a':
                return False

        return True            

    # Produce a score for a team
    @staticmethod
    def scoreteam(team,display=False):
        pickedteam = []
        typecount = [0,0,0,0]

        # Check it's a valid team to score
        if fpl.validteam(team) == False:
            return 0

        # Sort the team by look ahead points. Highest to Lowest
        sortedteam = sorted(team, key=itemgetter('lookaheadpoints'), reverse=True)

        for player in team:
            player['picked'] = False

        # Pick the highest value players that are required to be in the team
        # 1 Goalkeeper, 3 Defenders and 1 Forward = 5 players total
        for idx, count in enumerate(playmin):
            if count != 0:
                picked = 0
                for player in sortedteam:
                    if player['type_name'] == playertypes[idx]:
                        pickedteam.append(player)
                        picked += 1
                        typecount[idx] += 1
                        player['picked'] = True
                    if picked == count:
                        break
    
        # Fill in the other 6 players by highest look ahead point score
        playersneeded = 6
        for player in sortedteam:
            if player['picked'] == True:
                continue

            # Check we don't have more than
            # 1 Goalkeeper, 5 Defenders, 5 Midfielders or 3 Forwards.
            idx = playertypes.index(player['type_name'])
            if typecount[idx] == playmax[idx]:
                continue

            pickedteam.append(player)
            playersneeded -= 1
            typecount[idx] += 1
            player['picked'] = True

            if playersneeded == 0:
                break

        # Score the picked team    
        points = 0
        for player in pickedteam:
            if player['status'] == 'a':
                points += player['lookaheadpoints']

        # Score the non-picked players
        # Apply factor to reduce their impact on the overall score
        for player in team:
            if player not in pickedteam:
                if player['status'] == 'a':
                    points += player['lookaheadpoints'] * 0.1

        # Print out the team if needed
        if display == True:
            fpl.printteam(sortedteam)
            print "Points", points

        return points

    # Print out the team
    @staticmethod
    def printteam(team):
        for player in team:
            playerdata = player['second_name'].encode('ascii', errors='ignore')
            playerdata += "," + str(player['total_points'])
            playerdata += "," + str(player['now_cost'])
            playerdata += "," + player['team_name']
            playerdata += "," + player['type_name']
            playerdata += "," + str(player['code'])
            playerdata += "," + str(player['lookaheadpoints'])
            playerdata += "," + str(player['thisweekpoints'])

            if player['picked'] == True:
                playerdata += ", Picked"

            print playerdata
        
        print "Team value %s" % fpl.teamvalue(team)


