import discord
from os import listdir
from os.path import getmtime
from discord.ext import tasks, commands
from utils.roomgen import RoomGen
from utils.uploaders.sul import SulUploader

JOIN_URL = "https://curvewars.com/lobby/{0}"

try:
    from config import BOT_TOKEN, CHANNEL, UPLOADER_API_KEY, RENDER_DIR
except ModuleNotFoundError:
    print("Could not find config.\nFollow the readme")
    exit(1)

class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, command_prefix="", **kwargs)

        self.messagelist = {}
        self.filelist = {}
        self.uploader = SulUploader(key=UPLOADER_API_KEY)

        self.rg = RoomGen()

    @tasks.loop(seconds=15.0)
    async def postRenders(self):
        channel = self.get_channel(CHANNEL)
        self.rg.generate()

        RENDERS = [f for f in listdir(RENDER_DIR) if f.endswith(".png")]

        messagekeys = list(self.messagelist.keys())
        for k in messagekeys:
            if not k in [RENDER_DIR + "/" + k for k in RENDERS]:
                await self.messagelist[k]["message"].delete()
                del self.messagelist[k]

        for rawfilename in RENDERS:
            filename = RENDER_DIR + "/" + rawfilename
            mtime = getmtime(filename)

            if filename in self.messagelist:
                if mtime > self.messagelist[filename]["mtime"]:
                    # edit message to have new message
                    ret = self.uploader.delete(self.messagelist[filename]["file_id"])
                    if not ret:
                        print("Got status {0} while deleting {1}. Ignoring.".format(ret, self.messagelist[filename]["file_id"]))

                    url, self.messagelist[filename]["file_id"] = self.uploader.uploadFile(filename)

                    embed = discord.Embed(title="Join", url=JOIN_URL.format(rawfilename.removesuffix(".png")))
                    embed.set_image(url=url)

                    await self.messagelist[filename]["message"].edit(embed=embed)

            else:
                url, fid = self.uploader.uploadFile(filename)

                embed = discord.Embed(title="Join", url=JOIN_URL.format(rawfilename.removesuffix(".png")))
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

bot.run(BOT_TOKEN)
