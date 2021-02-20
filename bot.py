import discord
import os
from discord.ext import tasks, commands
from utils import roomgen as rg
from utils.uploaders.sul import SulUploader

CHANNEL = 
SUL_API_KEY = ""
RENDER_DIR = "render"

class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, command_prefix="curvewars", **kwargs)

        self.messagelist = {}
        self.filelist = {}
        self.uploader = SulUploader(key=SUL_API_KEY)

    @tasks.loop(seconds=10.0)
    async def postRenders(self):
        channel = self.get_channel(CHANNEL)
        rg.roomGen()

        messagekeys = list(self.messagelist.keys())
        for k in messagekeys:
            if not k in [RENDER_DIR + "/" + k for k in os.listdir(RENDER_DIR)]:
                await self.messagelist[k]["message"].delete()
                del self.messagelist[k]

        for filename in os.listdir(RENDER_DIR):
            filename = RENDER_DIR + "/" + filename
            mtime = os.path.getmtime(filename)

            if filename in self.messagelist:
                if mtime > self.messagelist[filename]["mtime"]:
                    # edit message to have new message
                    ret = self.uploader.delete(self.messagelist[filename]["file_id"])
                    if not ret:
                        print("Got {0} while deleting {1}. Ignoring.".format(ret, self.messagelist[filename]["file_id"]))

                    url, self.messagelist[filename]["file_id"] = self.uploader.uploadFile(filename)

                    embed = discord.Embed()
                    embed.set_image(url=url)

                    await self.messagelist[filename]["message"].edit(embed=embed)

            else:
                url, fid = self.uploader.uploadFile(filename)

                embed = discord.Embed()
                embed.set_image(url=url)

                msg = await channel.send(embed=embed)

                self.messagelist[filename] = {
                    "mtime": mtime,
                    "file_id": fid,
                    "message": msg
                }

bot = Bot()

@bot.event
async def on_command_error(ctx, error):
    pass

@bot.event
async def on_ready():
    print("Started")
    bot.postRenders.start()

bot.run('')
