################################################################################################################################################
'''This is my Nic Cage bot, enjoy'''
################################################################################################################################################
import random
import time
import re
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime
import requests
from bs4 import BeautifulSoup
import threading
import asyncio
from async_timeout import timeout

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

################################################################################################################################################
'''Constants'''
################################################################################################################################################
DATE_FORMAT = "%a, %b %d %Y"
EMPTY_WINNER = "https://tenor.com/view/100-gif-27642217"

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

#Regex patterns
DEFAULT_PAT_1 = "https://www.youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)"
DEFAULT_PAT_2 = "https://youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)[\&].*"
MOBILE_PAT_1 = "https://youtu.be/([a-zA-Z0-9\_\-]+)\?.+"
MOBILE_PAT_2 = "https://youtu.be/([a-zA-Z0-9\_\-]+)"
SHORTS_PAT_1 = "https://www.youtube.com/shorts/([a-zA-Z0-9\_\-]+)"
SHORTS_PAT_2 = "https://youtube.com/shorts/([a-zA-Z0-9\_\-]+)\?.*"

################################################################################################################################################
'''Setup'''
################################################################################################################################################ 
#TODO: change this
gifs = [
        "https://tenor.com/view/nicholas-cage-you-pointing-smoke-gif-14538102",
        "https://tenor.com/view/nicolas-cage-the-rock-smile-windy-handsome-gif-15812740",
        "https://tenor.com/view/woo-nick-cage-nicolas-cage-the-unbearable-weight-of-massive-talent-lets-go-gif-25135470",
        "https://tenor.com/view/national-treasure-benjamin-gates-nicolas-cage-declaration-of-independence-steal-gif-4752081"
        ]

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
KEY = os.getenv("YOUTUBE_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True

lastInt = -1
vids = {}
link_count = 1
rePatterns = [DEFAULT_PAT_1, DEFAULT_PAT_2, MOBILE_PAT_1, MOBILE_PAT_2, SHORTS_PAT_1, SHORTS_PAT_2]

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

################################################################################################################################################
'''Menu to launch program from shell'''
################################################################################################################################################
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
        
################################################################################################################################################
#For use with start/stop.sh files instead of starting via shell
#Will not work with menu block
'''pid = os.getpid()
f = open("pid.txt", "w")
f.write(str(pid))
f.seek(0)
f.close()'''

################################################################################################################################################
#Play a random clip each time !speak is called
def getRandomInt():
     i = random.randint(0, len(NicCageQuotes)-1)
     return i
     
################################################################################################################################################
def getTitleFromURL(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    link = soup.find_all(name="title")[0]
    title = str(link)
    title = link.text
    #print(title)
    return title
    
async def calculateTimeToWinner():
    sendTo = bot.get_channel(sendID)
    myTime = datetime.datetime.today()
    day = myTime.weekday()
    daysReference = [[0, 6, "Monday"], [1, 4, "Tuesday"], [2, 2, "Wednesday"], [3, 0, "Thursday"], [4, -2, "Friday"], [5, -4, "Saturday"], [6, 1, "Sunday"]]
    
    for ref in daysReference:
        if day == ref[0]:
            day += ref[1]
            #print(f'It\'s {ref[2]} - {day}')
            break
    
    #Will alert at 1am Sundays
    warning_time = (day*86400) - (myTime.hour*3600) - (myTime.minute*60) + 3600 - 28800
    totalTime = warning_time + 28800
    print(f'Waiting {totalTime}s until next winner announced')
    
    await asyncio.sleep(warning_time)
    #await asyncio.sleep(300)
    print(BEG_YELLOW + "Sending reminder to vote for best vid of the week" + END_YELLOW)
    await sendTo.send("@everyone\nRemember to vote for **Best Video of the Week**\nWinner(s) will be announced in 8 hours")
    
    #First wait the warning time and send warning, then wait another 8 hours and pick winner
    await asyncio.sleep(28800)
    #await asyncio.sleep(300)
    print(BEG_YELLOW + "Announcing best video of the week" + END_YELLOW)
    await sendTo.send("!winner")
    #Recurse and start calculate/sleep process over
    await calculateTimeToWinner()
    
async def logMessages(channel):
    global link_count
    
    async for message in channel.history(limit=None):
        isGoodLink = False
        newMessage = message.content
        
        if (newMessage is not None and newMessage.startswith("https")):
            author_name = message.author
            author_id = message.author.id
            creation_date = message.created_at.strftime(DATE_FORMAT)
            reactions = message.reactions
            reactionCount = 0
            
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
                
################################################################################################################################################
@bot.event
async def on_ready():
    start_time = time.time()
    #Get the channel from which to monitor repeat posts
    channel = bot.get_channel(getID)
    
    print(f'User name: {bot.user.name} - ID: {str(bot.user.id)}')
    print('We have logged in as {0.user}\n'.format(bot))
    print(BEG_BLUE + "Starting link history log..." + END_BLUE + "\n")
    
    await logMessages(channel)
                
    end_time = time.time()
    log_time = end_time - start_time
    print("\n" + BEG_BLUE +f'Finished logging {link_count} links in {log_time:.2f}s' + END_BLUE)
    print(BEG_FLASH + f'Listening for new links\n' + END_FLASH)
    
    await asyncio.wait_for(calculateTimeToWinner(), timeout=604801)
    
    #print("on_ready DONE")
    
################################################################################################################################################
def checkLink(info):
    global link_count
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
    sendTo = bot.get_channel(sendID)
    newLink = ctx.content
    author_id = ctx.author.id
    author_name = ctx.author
    creation_date = ctx.created_at.strftime(DATE_FORMAT)
    
    #alertMessage = f'<@{author_id}> {newLink} has been posted previously'
    #Message is from correct channel we want to monitor
    
    if ctx.channel.id == getID and newLink.startswith("https://"):
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
            
    elif ctx.channel.id == sendID and ctx.author == bot.user and newLink == "!winner":
        #time.sleep(60)
        await winner(ctx)
    
    await bot.process_commands(ctx)
    
################################################################################################################################################
'''All the commands to run from within discord chat below'''
################################################################################################################################################
@bot.command()
#(ctx, arg)?
async def test(ctx):
    await ctx.send('```md#Hello```')
    

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
@bot.command()
async def winner(ctx):
    print(BEG_YELLOW + "Determining winner..." + END_YELLOW)
    sendTo = bot.get_channel(sendID)
    start_time = time.time()
    channel = bot.get_channel(getID)
    winners = []
    mostReactions = 0
    isWinner = False
    
    async for message in channel.history(limit=None):
        isGoodLink = False
        newMessage = message.content
        
        if newMessage.startswith("Winner:") or newMessage.startswith("**Winner:"):
            break
            
        elif (newMessage is not None and newMessage.startswith("https")):
            author_name = message.author
            author_id = message.author.id
            creation_date = message.created_at.strftime(DATE_FORMAT)
            reactions = message.reactions
            reactionCount = 0
            
            if len(reactions) != 0:
                for reaction in reactions:
                    print(reactions)
                    print(type(reactions[0]))
                    print(reactions[0].count)
                    reactionCount += reaction.count
                    
                if reactionCount > mostReactions:
                    print("Found winner with higher total count. Winners reset.")
                    winners = []
                    
                if reactionCount >= mostReactions:
                    print(f'Reaction count {reactionCount} Most reactions {mostReactions}')
                    mostReactions = reactionCount
                    title = getTitleFromURL(newMessage)
                    title = title.split(" - YouTube")[0]
                    winners.append([newMessage, title, reactionCount, author_id])
                    print(f'Video added to winner. There are {reactionCount} reactions for {title}')
                    
    #print(winners)
    winningAuthors = "Congrats on winning best vid of the week: "
    numWinners = len(winners)
    winCount = 1
    
    if mostReactions != 0:
        isWinner = True
        winningTitles = ""
        for winner in winners: 
            winningTitles += "`" + winner[1] + "`"
            winningAuthors += f'<@{winner[3]}>'
            winCount += 1
            if winCount <= numWinners:
                winningTitles += "\n"
                winningAuthors += " & "
                
        print(f'Winning vidoe(s): {winningTitles}')
        if  not ctx.channel.id == getID:
            await ctx.reply(f'**Winner:**\n{winningTitles}\n{winningAuthors}')
        await channel.send(f'**Winner:**\n{winningTitles}\n{winningAuthors}')
            
    else:
        print(BEG_RED + "No reactions found - Unable to calculate winner" + END_RED)
        await ctx.reply(f'**Big, sad, empy bag of nothing**\n{EMPTY_WINNER}')
    
    end_time = time.time()
    log_time = end_time - start_time
    
    if isWinner == True:
        print("\n" + BEG_BLUE +f'Winner of best video of the week computed in {log_time:.2f}s' + END_BLUE)
        
@bot.command()
async def kill(ctx):
    await ctx.reply("Goodbye cruel world")
    print("Attempting to shut down program")
    exit()
################################################################################################################################################               
bot.run(TOKEN)


    


