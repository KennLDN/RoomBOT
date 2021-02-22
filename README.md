![# RoomBOT](https://i.imgur.com/5NuvUvC.png)

A python powered discord bot, sending a live list of CurveWars rooms to a channel.
Originally built for the official CurveWars discord server.

### Features
* Generates an image representing each room, detailing the players, the teams, average rank and powerups.
* Uploads images to an image host to allow the bot to edit it's messages.
* Updates the image in the channel only if room details are changed.
* Includes a quick join link to enter the specified room from Discord.

### How to use
1. Install requirements.txt
2. Copy config.py.example to config.py and fill out the fields
3. Run bot.py

### Extra
* Python 3.9 is required.
* s-ul.eu is currently the only available image host.
* This bot takes advantage of utils/curvewars.py, a CurveWars API adaptation for easier interaction.
* Take a look at the [Contributors](CONTRIBUTORS.md)
