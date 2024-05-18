#This is my Nic Cage bot, enjoy
import random
import time
import re
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

f = open("channels.txt", "r")
channelIDs = f.readlines()
#Channel that we're monitoring for repeat posts, check ref.txt
#For me only, [0:1] is prod [2:3] is test
#getID = int(channelIDs[0])
getID = int(channelIDs[2])

#Channel that we send the repeat noticication message to, check ref.txt
#sendID = int(channelIDs[1])
sendID = int(channelIDs[3])

f.seek(0)
f.close()

#For use with start/stop.sh files instead of starting via shell
pid = os.getpid()
f = open("pid.txt", "w")
f.write(str(pid))
f.seek(0)
f.close()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True
lastInt = -1
vids = {}
count = 1
youtubeDefaultPattern1 = "https://www.youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)"
youtubeDefaultPattern2 = "https://youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)[\&].*"
youtubeMobilePattern1 = "https://youtu.be/([a-zA-Z0-9\_\-]+)\?.+"
youtubeMobilePattern2 = "https://youtu.be/([a-zA-Z0-9\_\-]+)"
youtubeShortsPattern1 = "https://www.youtube.com/shorts/([a-zA-Z0-9\_\-]+)"
youtubeShortsPattern2 = "https://youtube.com/shorts/([a-zA-Z0-9\_\-]+)\?.*"
rePatterns = [youtubeDefaultPattern1, youtubeDefaultPattern2, youtubeMobilePattern1, youtubeMobilePattern2, youtubeShortsPattern1, youtubeShortsPattern2]

BEG_GREEN = '\33[32m'
END_GREEN = '\33[0m'
BEG_YELLOW = '\33[33m'
END_YELLOW = '\33[0m'
BEG_RED = '\33[31m'
END_RED = '\33[0m'

#This is where the quotes and references to the sound clips live
f = open("quotes.txt", "r")
NicCageQuotes = f.readlines()
f.seek(0)
f.close()

#TODO: change this
gifs = [
        "https://tenor.com/view/nicholas-cage-you-pointing-smoke-gif-14538102",
        "https://tenor.com/view/nicolas-cage-the-rock-smile-windy-handsome-gif-15812740",
        "https://tenor.com/view/woo-nick-cage-nicolas-cage-the-unbearable-weight-of-massive-talent-lets-go-gif-25135470",
        "https://tenor.com/view/national-treasure-benjamin-gates-nicolas-cage-declaration-of-independence-steal-gif-4752081"
        ]
################################################################################################################################################
#Play a random clip each time !speak is called
def getRandomInt():
     i = random.randint(0, len(NicCageQuotes)-1)
     return i
################################################################################################################################################
@bot.event
async def on_ready():
    #Get the channel from which to monitor repeat posts
    channel = bot.get_channel(getID)
    global count
    
    print("User name: " + bot.user.name)
    print("User id: " + str(bot.user.id))
    print('We have logged in as {0.user}\n'.format(bot))
    print("Starting link history log...")
    
    async for message in channel.history(limit=None):
        newMessage = message.content
        isGoodLink = False
        
        if (newMessage is not None and newMessage.startswith("https")):
            for pattern in rePatterns:
                vidID  = re.findall(pattern, newMessage)
                #print(pattern)
                
                if (len(vidID) == 1):
                    isGoodLink = True
                    vids.update({vidID[0] : count})
                    count += 1
                    print(BEG_GREEN + f'Logged {vidID[0]}' + END_GREEN)
                    break
                        
            if isGoodLink == False:
                print(BEG_RED + f'Unsupported link type {newMessage}' + END_RED)
            
    print("Link history log complete")
    print("Listening for new links")
################################################################################################################################################
def checkLink(vidID):
    global count
    global sendTo
    print(f"New link with unique ID: '{vidID}' detected")
    sendTo = bot.get_channel(sendID)

    #Video was posted before, notify poster
    if (vidID in vids):
        print(BEG_YELLOW + "Repeat link detected" + END_YELLOW) #yellow text
        return True
    #Video not posted before, add video to log
    else:
        count += 1
        vids.update({vidID : count})
        print(f"New link: '{vidID}' has been logged")
        return False
        
@bot.event
async def on_message(ctx):
    newLink = ctx.content
    author = ctx.author.id
    alertMessage = f'<@{author}> {newLink} has been posted previously'
    #Message is from correct channel we want to monitor
    if ctx.channel.id == getID:
        vidID = ""
        for pattern in rePatterns:
            checkPattern = re.findall(pattern, newLink)
            if (len(checkPattern) != 0):
                vidID = checkPattern[0]
                break
       
        repeat = checkLink(vidID)
        if repeat == True:
            await sendTo.send(alertMessage)
    
    await bot.process_commands(ctx)
    
################################################################################################################################################
'''All the commands to run from within discord chat below'''
################################################################################################################################################

@bot.command()
async def test(ctx, arg):
    await ctx.send("Test command - CORRECT WAY " + arg)
################################################################################################################################################
@bot.command()
async def speak(ctx):
    global lastInt
    #Prevent the same quote/clip from being played twice in a row
    myRandomInt = getRandomInt()
    while (True):
        if (myRandomInt == lastInt):
            myRandomInt = getRandomInt()
        else:
            lastInt = myRandomInt
            _myQuote = NicCageQuotes[myRandomInt]
            myQuote = _myQuote.split("; ")
            print("Channel Name: " + str(ctx.channel.name) + ", Channel ID: " + str(ctx.channel.id))
            await ctx.reply(myQuote[0])
            print('Quote: ' + BEG_GREEN + myQuote[0] + END_GREEN)
            try:
                voice = ctx.voice_client.play(discord.FFmpegPCMAudio(str('./sounds/' + myQuote[1].strip())))
            except:
                print(BEG_RED + "No active voice channel - Clip not played" + END_RED)
            break
################################################################################################################################################
@bot.command()
async def helpme(ctx):
       await ctx.reply("Commands: !join !qjoin !leave !qleave !speak !helpme !gif")
################################################################################################################################################
@bot.command()
async def gif(ctx):
    randomGif = random.randint(0,3)
    await ctx.reply(gifs[randomGif])
################################################################################################################################################
@bot.command()
async def join(ctx):
    try:
        voice = await ctx.author.voice.channel.connect()
        await ctx.reply("Nic is here to party, woo! (!helpme)")
        voice.play(discord.FFmpegPCMAudio('./sounds/woo.mp3'))
    except:
        print(BEG_RED + "No members active in voice channel - Channel not joined" + END_RED)
        await ctx.reply("I can't join a voice channel without any active members")
################################################################################################################################################
@bot.command()
async def qjoin(ctx):
    try:
        voice = await ctx.author.voice.channel.connect()
        await ctx.reply("Nic is here to party, woo! (!helpme)")
    except:
        print(BEG_RED + "No members active in voice channel - Channel not joined" + END_RED)
        await ctx.reply("I can't join a voice channel without any active members")
################################################################################################################################################
@bot.command()
async def leave(ctx):
    try:
        voice = ctx.voice_client.play(discord.FFmpegPCMAudio('./sounds/silence.mp3'))
        await ctx.reply("Hurray for the sounds of fucking silence")
        time.sleep(5)
        voice = await ctx.voice_client.disconnect()
    except:
        await ctx.reply("I'm not in any channels genious")
################################################################################################################################################
@bot.command()
async def qleave(ctx):
    try:
        await ctx.reply("Hurray for the sounds of fucking silence")
        time.sleep(5)
        voice = await ctx.voice_client.disconnect()
    except:
        await ctx.reply("I'm not in any channels genious")
################################################################################################################################################
bot.run(TOKEN)
    


