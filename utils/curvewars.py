import requests
import json

loginUser = ""
loginPass = ""

# Validates Client for API Access
def Validate():
    loginPage = requests.post("https://curvewars.com/api/auth/login", json={"username":loginUser, "password":loginPass})
    response = json.loads(loginPage.text)
    cookie = {"cwtoken": response["token"]}
    header = {"Authorization": "Bearer "+response["token"], "Cookie": "cwtoken="+response["token"]}
    return(cookie, header)

# Returns Basic User Info
def BasicProfile(username):
    token = Validate()
    request = requests.post("https://curvewars.com/api/stat", json={"username":username}, cookies=token[0], headers=token[1])
    try:
        response = json.loads(request.text)
        print(response)
        for i in response[0]["stat"]:
            if username in i["player"].values():
                userLoc = i["player"]
        results = {
            "id": userLoc["id"],
            "username": userLoc["username"],
            "country": userLoc["country"],
            "email": userLoc["email"],
            "playerStates": {
                "isAdmin": userLoc["isAdmin"],
                "isMod": userLoc["isModerator"],
                "isChamp": userLoc["isChamp"],
                "premiumLevel": userLoc["premiumLvl"]
                },
            "balances": {
                "coins": userLoc["coins"],
                "diamonds": userLoc["diamonds"],
                "gPoints": userLoc["gPoints"]
                },
            "preferences": {    
                "controls": {"leftKey": userLoc["leftKey"], "rightKey": userLoc["rightKey"]},
                "keylag": userLoc["keylag"],
                "icon": userLoc["icon"],
                "clantag": userLoc["clantag"],
                "favColor": userLoc["preferedColor"],
                },
            "FFA": {
                "totalGames": userLoc["ffaPlays"],
                "gamesWon": userLoc["ffaWins"],
                "rank": userLoc["ffaRank"],
                },
            "Team": {
                "totalGames": userLoc["teamPlays"],
                "gamesWon": userLoc["teamWins"],
                "rank": userLoc["teamRank"],
                },
            "1v1": {
                "totalGames": userLoc["ovoPlays"],
                "gamesWon": userLoc["ovoWins"],
                "rank": userLoc["ovoRank"],
                },
            }
        return json.dumps(results)
    except Exception as e:
        return(e)

# Returns MatchID of 10 Matches
def MatchHistory(username, page):
    
    return results 

# Returns Every Active Room
def ActiveRooms():
    results = {}
    request = requests.get("https://curvewars.com/matchmake/")
    response = json.loads(request.text)
    def gameType(string):
        return {'ffa':'FFA','two':'Two Teams','three':'Three Teams'}[string]
    for idx, val in enumerate(response):
        if val["name"] == "main" and val["maxClients"] == 500: continue
        gameLoc = val["metadata"]
        def getPlayers():
            players = gameLoc["players"]
            if gameLoc["game_type"] == "ffa":
                return {p["username"]: p for p in players}
            else:
                teams = [[], [], []]
                for x in players:
                    teams[x["team"]].append(x)
                teamsD = {"teamOne": teams[0], "teamTwo": teams[1], "teamThree": teams[2]}
                return {k: {p["username"]: p for p in v} for k, v in teamsD.items()}
        teamScores = gameLoc["teamWinners"]
        results[idx] = {
                "Room Name": gameLoc["name"],
                "Player Count": gameLoc["players_in"],
                "Average Rank": gameLoc.get("avg_rank", 0),
                "Game Started": gameLoc["game_started"],
                "Settings": {
                    "Gamemode": gameType(gameLoc["game_type"]),
                    "Ranked": gameLoc["ranked"],
                    "Total Players": gameLoc["players_count"],
                    "Drop Probability": gameLoc["drop_probability"],
                    "Map Size": gameLoc["room_size"],
                    "Powerups": gameLoc["powerups"],
                    },
                "Players": getPlayers(),
                "RoomID": val["roomId"],
                "Team Score": {
                    "teamOne": teamScores["0"],
                    "teamTwo": teamScores["1"],
                    "teamThree": teamScores["2"],
                },
            }
    return json.dumps(results)

def MatchResults(matchid):
    pass

# Returns All In-Game Media
def gameMedia():
    icons = {}
    powerups = {}
    colors = {}
    media = {}
    request = requests.get("https://curvewars.com/api/media/")
    response = json.loads(request.text)
    for i in response["icons"]:
        def coinVal():
            if "coins" in i:
                return i["coins"]
            else:
                return "0"
        icons[int(i["id"])] = {
            "name": i["name"],
            "coins": coinVal(),
            "file": i["icon"],
            "desc": i["description"],
            }
    for i in response["colors"]:
        colors[int(i["id"])] = {
            "name": i["name"],
            "coins": i["costs"],
            "file": i["texture"],
            "pattern": i["pattern"],
            "contains": i["colors"],
            }
    for i in response["powerups"]:
        powerups[int(i["id"])] = {
            "file": i["icon"],
            }
    media = {"icons": icons, "colors": colors, "powerups": powerups}
    return json.dumps(media)
