#This is my Nic Cage bot, enjoy
import random
import time
import re
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime

#Channel IDs of the two channels in our discord that I use to implement this bot
f = open("channels.txt", "r")
channelIDs = f.readlines()
f.seek(0)
f.close()

#This is where the quotes and references to the sound clips live
f = open("quotes.txt", "r")
NicCageQuotes = f.readlines()
f.seek(0)
f.close()

#Colors for shell print statements
BEG_GREEN = '\33[32m'
END_GREEN = '\33[0m'
BEG_YELLOW = '\33[33m'
END_YELLOW = '\33[0m'
BEG_RED = '\33[31m'
END_RED = '\33[0m'
BEG_BLUE = '\33[44m'
END_BLUE = '\33[0m'
BEG_FLASH = '\33[5m'
END_FLASH = '\33[0m'

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True

lastInt = -1
vids = {}
link_count = 1
defaultPattern1 = "https://www.youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)"
defaultPattern2 = "https://youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)[\&].*"
mobilePattern1 = "https://youtu.be/([a-zA-Z0-9\_\-]+)\?.+"
mobilePattern2 = "https://youtu.be/([a-zA-Z0-9\_\-]+)"
shortsPattern1 = "https://www.youtube.com/shorts/([a-zA-Z0-9\_\-]+)"
shortsPattern2 = "https://youtube.com/shorts/([a-zA-Z0-9\_\-]+)\?.*"
rePatterns = [defaultPattern1, defaultPattern2, mobilePattern1, mobilePattern2, shortsPattern1, shortsPattern2]
date_format = "%a, %b %d %Y"

#TODO: change this
gifs = [
        "https://tenor.com/view/nicholas-cage-you-pointing-smoke-gif-14538102",
        "https://tenor.com/view/nicolas-cage-the-rock-smile-windy-handsome-gif-15812740",
        "https://tenor.com/view/woo-nick-cage-nicolas-cage-the-unbearable-weight-of-massive-talent-lets-go-gif-25135470",
        "https://tenor.com/view/national-treasure-benjamin-gates-nicolas-cage-declaration-of-independence-steal-gif-4752081"
        ]

#Channel that we're monitoring for repeat posts
getID = 0
sendID = 0

#These are for the menu
#For me only, [0:1] is prod [2:3] is test
getIDprod = int(channelIDs[0])
getIDtest = int(channelIDs[2])

#Channel that we send the repeat noticication message to, check ref.txt
sendIDprod = int(channelIDs[1])
sendIDtest = int(channelIDs[3])

#Menu to launch program from shell
while True:
    user_input = input("Run bot in PROD [1] or Run bot in TEST [2] Exit the program [0]: ")
    try:
        user_input = int(user_input)
    except:
        print(BEG_RED + 'Invalid selection. Try again.' + END_RED)
        continue
    
    if user_input == 1:
        getID = getIDprod
        sendID = sendIDprod
        print("Starting bot in main channels")
        break
    elif user_input == 2:
        getID = getIDtest
        sendID = sendIDtest
        print("Starting bot in test channels")
        break
    elif user_input == 0:
        print("Goodbye")
        time.sleep(5)
        quit()
    else:
        print(BEG_RED + 'Invalid selection. Try again.' + END_RED)
        
#For use with start/stop.sh files instead of starting via shell
#Will not work with menu block
'''pid = os.getpid()
f = open("pid.txt", "w")
f.write(str(pid))
f.seek(0)
f.close()'''

################################################################################################################################################
def calculateTimeToWinner():
    myTime = datetime.datetime.today()
    day = myTime.weekday()
    daysReference = [[0, 6, "Monday"], [1, 4, "Tuesday"], [2, 2, "Wednesday"], [3, 0, "Thursday"], [4, -2, "Friday"], [5, -4, "Saturday"], [6, 1, "Sunday"]]
    
    for ref in daysReference:
        if day == ref[0]:
            day += ref[1]
            #print(f'It\'s {ref[2]} - {day}')
            break
    
    #Will alert at 1am Sundays
    winner_time = (day*86400) - (myTime.hour*3600) - (myTime.minute*60) + 3600
    
    print(f'Waiting {winner_time}s until next winner announced')
    #print("Bot startup time: " + str(hour) + " " + str(minute) + " " + str(day))
    
    
@bot.event
async def on_ready():
    calculateTimeToWinner()
    #Get the channel from which to monitor repeat posts
    start_time = time.time()
    channel = bot.get_channel(getID)
    global date_format
    global link_count
    
    print("User name: " + bot.user.name)
    print("User id: " + str(bot.user.id))
    print('We have logged in as {0.user}\n'.format(bot))
    print(BEG_BLUE + "Starting link history log..." + END_BLUE + "\n")
    
    async for message in channel.history(limit=None):
        newMessage = message.content
        author_name = message.author
        author_id = message.author.id
        creation_date = message.created_at.strftime(date_format)
        reactions = message.reactions
        reactionCount = 0
        if len(reactions) != 0:
            for reaction in reactions:
                #print(reactions)
                #print(type(reactions[0]))
                #print(reactions[0].count)
                reactionCount += reaction.count
        isGoodLink = False
        
        if (newMessage is not None and newMessage.startswith("https")):
            for pattern in rePatterns:
                vidID  = re.findall(pattern, newMessage)
                #print(pattern)
                
                if (len(vidID) == 1):
                    isGoodLink = True
                    log_item = [link_count, author_name, author_id, creation_date]
                    vids.update({vidID[0] : log_item})
                    link_count += 1
                    #Uncomment this line to see print out of how messages were handled
                    #print(BEG_GREEN + f'Link logged{END_GREEN} - ID: {vidID[0]} - AUTHOR: {author_name} - DATE: {creation_date} - REACTIONS: {reactionCount}')
                    break
                        
            if isGoodLink == False:
                print(BEG_RED + f'Unsupported link type {newMessage}' + END_RED)
                
    end_time = time.time()
    log_time = end_time - start_time
    print("\n" + BEG_BLUE +f'Finished logging {link_count} links in {log_time:.2f}s' + END_BLUE)
    print(BEG_FLASH + f'Listening for new links\n' + END_FLASH)
################################################################################################################################################
def checkLink(info):
    global link_count
    global sendTo
    vidID = info[0]
    author_name = info[1]
    author_id = info[2]
    creation_date = info[3]
    print(f"New link with unique ID: '{vidID}' detected")
    sendTo = bot.get_channel(sendID)

    #Video was posted before, notify poster
    if (vidID in vids):
        print(BEG_YELLOW + "Repeat link detected" + END_YELLOW) #yellow text
        return True
    #Video not posted before, add video to log
    else:
        link_count += 1
        log_item = [link_count, author_name, author_id, creation_date]
        vids.update({vidID : log_item})
        print(f"New link: '{vidID}' has been logged")
        return False
        
@bot.event
async def on_message(ctx):
    global date_format
    newLink = ctx.content
    author_id = ctx.author.id
    author_name = ctx.author
    creation_date = ctx.created_at.strftime(date_format)
    #alertMessage = f'<@{author_id}> {newLink} has been posted previously'
    #Message is from correct channel we want to monitor
    if ctx.channel.id == getID:
        vidID = ""
        for pattern in rePatterns:
            checkPattern = re.findall(pattern, newLink)
            if (len(checkPattern) != 0):
                vidID = checkPattern[0]
                info = [vidID, author_name, author_id, creation_date]
                break
       
        repeat = checkLink(info)
        if repeat == True:
            og_info = vids[vidID]
            await sendTo.send(f'<@{author_id}> {newLink} was posted by <@{og_info[2]}> on {og_info[3]}')
    
    await bot.process_commands(ctx)
    
################################################################################################################################################
'''All the commands to run from within discord chat below'''
################################################################################################################################################

@bot.command()
async def test(ctx, arg):
    await ctx.send("Test command - CORRECT WAY " + arg)
################################################################################################################################################
#Play a random clip each time !speak is called
def getRandomInt():
     i = random.randint(0, len(NicCageQuotes)-1)
     return i

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
    


