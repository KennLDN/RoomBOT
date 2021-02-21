from PIL import Image, ImageDraw, ImageFont
from utils.curvewars import CurveWarsWrapper
from os import listdir, remove
from json import loads as jsonloads
from requests import get
from itertools import product
from collections import defaultdict

class RoomGen:

    def __init__(self):
        self.freg = ImageFont.truetype("assets/fonts/Regular.ttf", 16)
        self.fbold = ImageFont.truetype("assets/fonts/Bold.ttf", 16)
        self.fbolds = ImageFont.truetype("assets/fonts/Bold.ttf", 13)
        self.fboldl = ImageFont.truetype("assets/fonts/Bold.ttf", 18)
        self.fblackl = ImageFont.truetype("assets/fonts/Black.ttf", 18)

        self.cw = CurveWarsWrapper()
        self.gameMedia = jsonloads(self.cw.GameMedia)

        self.lastRooms = {}

    @staticmethod
    def boolToString(string):
        return "Yes" if string else "No"

    def generate(self):
        activeRoom = jsonloads(self.cw.ActiveRooms)
        actID = []
        for i in activeRoom.values():
            actID.append(i["RoomID"]+".png")

            if i in self.lastRooms.values():
                continue

            # init
            room = Image.new("RGBA", (700,372), color = (24,25,26))
            room_w, room_h = room.size

            # logo
            logo = Image.open("assets/images/logo.png", "r")
            logo_w, logo_h = logo.size
            room.paste(logo, (20,20))

            # stats
            roomStarted = ImageDraw.Draw(room)
            roomStarted.text((220,19), "In Progress?: " + self.boolToString(i["Game Started"]), font=self.fbold, fill=(200,200,200,255))
            avgRank = ImageDraw.Draw(room)
            avgRank.text((220,39), "Average Rank: " + str(round(i["Average Rank"] if i["Average Rank"] else 0)), font=self.fbold, fill=(200,200,200,255))

            # powerups
            pl_w = 463
            pl_h = 20
            puc = 0
            active = []
            inactive = []
            for x in self.gameMedia["powerups"]:
                if x in i["Settings"]["Powerups"]:
                    active.append(x)
                else:
                    inactive.append(x)
            powerups = active + inactive
            for x in powerups:
                # Local Files Used Due to SVG Incompat with PIL, Cairo adds overhead
                if x in active:
                    exec("pu"+str(x)+"= Image.open('assets/powerups/enabled/"+str(x)+".png')")
                else:
                    exec("pu"+str(x)+"= Image.open('assets/powerups/disabled/"+str(x)+".png')")
                room.paste(locals()["pu"+str(x)], (pl_w, pl_h))
                puc +=1
                pl_w = pl_w+27
                if puc == 8:
                    pl_h = pl_h+27
                    pl_w = 463

            # room name
            roomName = ImageDraw.Draw(room)
            separator = Image.open('assets/images/separator.png', 'r')
            room.paste(separator, (0,99))
            roomName_w, roomName_h = roomName.textsize(i["Room Name"], font=self.fboldl)
            for j in range(8):
                for x in product([j,-j], repeat=2):
                    roomName.text((((room_w - roomName_w) / 2) + x[0], 88 + x[1]), i["Room Name"], font=self.fboldl, fill=(24,25,26))
            roomName.text(((room_w-roomName_w)/2,88), i["Room Name"], font=self.fboldl, fill=("white"))

            # game mode
            vs = ImageDraw.Draw(room)
            vs_w, vs_h = vs.textsize("- VS -", font=self.fbold)
            if i["Settings"]["Gamemode"] == "FFA":
                free_w, free_h = vs.textsize("FREE", font=self.fbold)
                for_w, for_h = vs.textsize("FOR", font=self.fbold)
                all_w, all_h = vs.textsize("ALL", font=self.fbold)
                vs.text(((room_w-free_w)/2, (((room_h-free_h)/2)+15)), "FREE", font=self.fbold, fill=(200, 200, 200, 255))
                vs.text(((room_w-for_w)/2,((room_h-for_h)/2)+50), "FOR", font=self.fbold, fill=(200, 200, 200, 255))
                vs.text(((room_w-all_w)/2, ((room_h-all_h)/2)+87), "ALL", font=self.fbold, fill=(200, 200, 200, 255))
            elif i["Settings"]["Gamemode"] == "Two Teams":
                team1_w, team1_h = vs.textsize("TRIANGLE", font=self.fbold)
                team2_w, team2_h = vs.textsize("SQUARE", font=self.fbold)
                t1s_w, t1s_h = vs.textsize(str(i["Team Score"]["teamOne"]), font=self.fboldl)
                t2s_w, t2s_h = vs.textsize(str(i["Team Score"]["teamTwo"]), font=self.fboldl)
                vs.text(((room_w-vs_w)/2,((room_h-vs_h)/2)+50), "- VS -", font=self.fbold, fill=(200, 200, 200, 255))
                vs.text(((room_w-team1_w)/2, ((room_h-team1_h)/2)), "TRIANGLE", font=self.fbold, fill=(255,150,87,255))
                vs.text(((room_w-team2_w)/2, ((room_h-team2_h)/2)+102), "SQUARE", font=self.fbold, fill=(56,177,139,255))
                if i["Game Started"] == True:
                    vs.text(((room_w-t1s_w)/2, ((room_h-t1s_h)/2)-30), str(i["Team Score"]["teamOne"]), font=self.fboldl, fill=(255,150,87,255))
                    vs.text(((room_w-t2s_w)/2, ((room_h-t2s_h)/2)+132), str(i["Team Score"]["teamTwo"]), font=self.fboldl, fill=(56,177,139,255))
            else:
                vs.text((((room_w-vs_w)/3)-30,((room_h-vs_h)/2)+50), "- VS -", font=self.fbold, fill=(200, 200, 200, 255))
                vs.text((((room_w*2-vs_w)/3)-50,((room_h-vs_h)/2)+50), "- VS -", font=self.fbold, fill=(200, 200, 200, 255))
                vs.text((40, 120), "TRIANGLE "+str(i["Team Score"]["teamOne"]), font=self.fbolds, fill=(255,150,87,255))
                vs.text((260, 120), "SQUARE "+str(i["Team Score"]["teamTwo"]), font=self.fbolds, fill=(56,177,139,255))
                vs.text((480, 120), "SQUARE "+str(i["Team Score"]["teamThree"]), font=self.fbolds, fill=(86,177,56,255))

            # players (bit lazy tbh)
            pDisp = ImageDraw.Draw(room)
            def printUser(mode, team, flip, gap, x, y):
                if mode == "ffaRank" and flip == True:
                    scan = leftP
                elif mode == "ffaRank" and flip == False:
                    scan = rightP
                else:
                    scan = players[team]
                for u in scan:
                    if mode == "teamRank":
                        pInfo = i["Players"][team][u]
                    else:
                        pInfo = i["Players"][u]
                    pDisp_w, pDisp_h = pDisp.textsize(u, font=self.fbold)
                    pRank_w, pRank_h = pDisp.textsize(str(pInfo[mode]), font=self.fbolds)
                    pCol = Image.open(get("https://curvewars.com" + self.gameMedia["colors"][str(pInfo["color"])]["file"], stream=True).raw)
                    pCol = pCol.resize((10, 37), Image.ANTIALIAS)
                    if flip == True:
                        x1, x2 = x-pDisp_w, x-pRank_w
                        colPoints = [(x+20+4, 130+y+gap+4), (x+20+14, 130+y+gap+41)]
                        colShadow = ImageDraw.Draw(room)
                        colShadow.rectangle(colPoints, fill=(52,54,56,255), outline=(24,25,26,255))
                        room.paste(pCol, (x+20, 130+y+gap))
                    else:
                        x1, x2 = x,x
                        colPoints = [(x1-30-4, 130+y+gap+4), (x1-30+6, 130+y+gap+41)]
                        colShadow = ImageDraw.Draw(room)
                        colShadow.rectangle(colPoints, fill=(52,54,56,255), outline=(24,25,26,255))
                        room.paste(pCol, (x1-30, 130+y+gap))
                    pDisp.text((x1, 130+y+gap), u, font=self.fbold, fill=("white"))
                    pDisp.text((x2, 152+y+gap), str(pInfo[mode]), font=self.fbolds, fill=("white"))
                    gap += 47
            if i["Settings"]["Gamemode"] == "FFA":
                nPair = 0
                leftP = []
                rightP = []
                for u in i["Players"]:
                    if (nPair % 2) == 0:
                        leftP.append(u)
                        nPair += 1
                    else:
                        rightP.append(u)
                        nPair += 1
                printUser("ffaRank", "", True, 23, 236, 0)
                printUser("ffaRank", "", False, 26, 463, 0)
                    
            if i["Settings"]["Gamemode"] in ("Two Teams", "Three Teams"):
                players = i["Players"]
                gaps = defaultdict(int)
                gaps.update({1: 85, 2: 65, 3: 47, 4: 23})
                lGap = gaps[len(players["teamOne"])]
                rGap = gaps[len(players["teamTwo"])]
                tGap = gaps[len(players["teamThree"])]
                if i["Settings"]["Gamemode"] == "Three Teams":
                    hPos1 = 60
                    hPos2 = 290
                    hPos3 = 500
                    revFirst = False
                else:
                    hPos1 = 236
                    hPos2 = 463
                    hPos3 = 0
                    revFirst = True
                printUser("teamRank", "teamOne", revFirst, 0, hPos1, lGap)
                printUser("teamRank", "teamTwo", False, 0, hPos2, rGap)
                printUser("teamRank", "teamThree", False, 0, hPos3, tGap)
                
            
            
            room.save("render/"+i["RoomID"]+".png")

        self.lastRooms = activeRoom.copy()
        #delete non existant rooms                 
        for filename in listdir("render"):
            if filename.endswith(".png") and filename not in actID:
                remove("render/"+filename)
