################################################################################################################################################
'''This is my Nic Cage bot, enjoy'''
################################################################################################################################################
import random
import time
import re
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import datetime
import requests
from bs4 import BeautifulSoup
import threading
import asyncio
from async_timeout import timeout
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import openai
from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

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
# Define your API key and the necessary parameters
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

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
DEFAULT_PAT_1 = r"https://www.youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)"
DEFAULT_PAT_2 = r"https://youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)[\&].*"
MOBILE_PAT_1 = r"https://youtu.be/([a-zA-Z0-9\_\-]+)\?.+"
MOBILE_PAT_2 = r"https://youtu.be/([a-zA-Z0-9\_\-]+)"
SHORTS_PAT_1 = r"https://www.youtube.com/shorts/([a-zA-Z0-9\_\-]+)"
SHORTS_PAT_2 = r"https://youtube.com/shorts/([a-zA-Z0-9\_\-]+)\?.*"

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
#KEY = os.getenv("YOUTUBE_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
#bot.tree = app_commands.CommandTree(bot)
intents.message_content = True
#GUILD_ID = 456511756605587476

lastInt = -1
vids = {}
link_count = 1
rePatterns = [DEFAULT_PAT_1, DEFAULT_PAT_2, MOBILE_PAT_1, MOBILE_PAT_2, SHORTS_PAT_1, SHORTS_PAT_2]

#Channel that we're monitoring for repeat posts
getID = 0
#Channel we send messages to
sendID = 0

#Playlist to update, this works when it's hard coded here, but fails when the playlist ID is read from a file (for some reason)
PLAYLIST_ID = ""
#Best Video of the Day - Talith
PLAYLIST_ID_PROD = 'PLSLlIlXQSsqmKbKSstCSoS4RLoSo2awoX'
#Movie Boys - 4-Saken(me)
PLAYLIST_ID_TEST = 'PLl58uFKfuzLU-HfruEVohMJOC4Ag1DThy'

#These are for the menu
#For me only, [0:1] is prod [2:3] is test
getIDprod = int(channelIDs[0])
getIDtest = int(channelIDs[2])

#Channel that we send the repeat noticication message to, check ref.txt
sendIDprod = int(channelIDs[1])
sendIDtest = int(channelIDs[3])

#Playlist to add the best video to
#PLAYLIST_ID_PROD = channelIDs[4]
#PLAYLIST_ID_TEST = channelIDs[5]

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
        PLAYLIST_ID = PLAYLIST_ID_PROD
        print("Starting bot in main channels")
        break
    elif user_input == 2:
        getID = getIDtest
        sendID = sendIDtest
        PLAYLIST_ID = PLAYLIST_ID_TEST
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
def add_video_to_playlist(credentials, video_id, playlist_id):
    print("start add")
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Add video to playlist
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )

    response = request.execute()
    print(BEG_GREEN + f'Video {video_id} added to playlist {playlist_id}' + END_GREEN)

async def get_authenticated_service():
    print(BEG_YELLOW + "Youtube authentication started" + END_YELLOW)
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            try:
                creds = pickle.load(token)
            except EOFError:
                pass
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print(BEG_YELLOW + "Youtube authentication completed" + END_YELLOW)
    return creds

################################################################################################################################################
#Play a random clip each time !speak is called
def getRandomInt():
     i = random.randint(0, len(NicCageQuotes)-1)
     return i
     
################################################################################################################################################
#TODO: This is the slowest part of the whole bot, the GET request takes way too long
def getTitleFromURL(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    link = soup.find_all(name="title")[0]
    title = str(link)
    title = link.text
    #print(title)
    return title
    
async def calculateTimeToWinner(credentials):
    sendTo = bot.get_channel(sendID)
    myTime = datetime.datetime.today()
    day = myTime.weekday()

    #Following the days of the week in order should cascade from 7 down to 1
    #TODO: Turn this into a for loop
    #Alerts on Sunday
    #daysReference = [[0, 6, "Monday"], [1, 4, "Tuesday"], [2, 2, "Wednesday"], [3, 0, "Thursday"], [4, -2, "Friday"], [5, -4, "Saturday"], [6, 1, "Sunday"]]
    #Alerts on Monday
    daysReference = [[0, 7, "Monday"], [1, 5, "Tuesday"], [2, 3, "Wednesday"], [3, 1, "Thursday"], [4, -1, "Friday"], [5, -3, "Saturday"], [6, -5, "Sunday"]]
    #Alerts on Tuesday
    #daysReference = [[0, 1, "Monday"], [1, 6, "Tuesday"], [2, 4, "Wednesday"], [3, 2, "Thursday"], [4, 0, "Friday"], [5, -2, "Saturday"], [6, -4, "Sunday"]]
    #Alerts on Wednesday
    #daysReference = [[0, 2, "Monday"], [1, 0, "Tuesday"], [2, 5, "Wednesday"], [3, 3, "Thursday"], [4, 1, "Friday"], [5, -1, "Saturday"], [6, -3, "Sunday"]]
    #Alerts on Thursday
    #daysReference = [[0, 3, "Monday"], [1, 1, "Tuesday"], [2, -1, "Wednesday"], [3, 4, "Thursday"], [4, 2, "Friday"], [5, 0, "Saturday"], [6, -2, "Sunday"]]
    #Alerts on Friday
    #daysReference = [[0, 4, "Monday"], [1, 2, "Tuesday"], [2, 0, "Wednesday"], [3, -2, "Thursday"], [4, 3, "Friday"], [5, 1, "Saturday"], [6, -1, "Sunday"]]
    #Alerts on Saturday
    #daysReference = [[0, 5, "Monday"], [1, 3, "Tuesday"], [2, 1, "Wednesday"], [3, -1, "Thursday"], [4, -3, "Friday"], [5, 2, "Saturday"], [6, 0, "Sunday"]]
            
    for ref in daysReference:
        if day == ref[0]:
            day += ref[1]
            print(f'Today is {ref[2]}')
            break
            
    for ref in daysReference:
        if ref[0] + ref[1] == 7:
            print(f'Winners announced on {ref[2]}')
    
    #Will alert at 1am on whatever day in daysReference where indeces 0 and 1 add up to 7
    warning_time = (day*86400) - (myTime.hour*3600) - (myTime.minute*60) + 3600 - 14400
    totalTime = warning_time + 14400
    print(f'Waiting {warning_time/3600.00:.2f} hours until winner warning')
    print(f'Waiting {totalTime/3600.00:.2f} hours until next winner announced')

    await asyncio.sleep(warning_time)
    #This is for testing
    #await asyncio.sleep(20)
    print(BEG_YELLOW + "Sending reminder to vote for best vid of the week" + END_YELLOW)
    await sendTo.send("Get your votes in now for **Best Video of the Week**\nWinner(s) will be announced in 4 hours")

    #First wait the warning time and send warning, then wait another 8 hours and pick winner
    await asyncio.sleep(14400)
    #This is for testing
    #await asyncio.sleep(20)
    print(BEG_YELLOW + "Announcing best video of the week" + END_YELLOW)

    #Call to calculate the winners and send messages to discord channels
    ctx = bot.get_context
    winners = await winner(ctx)

    #This block for adding the winners to the playlist
    winner_IDs = []
    for win in winners:
        vidID = ""
        for pattern in rePatterns:
            checkPattern = re.findall(pattern, win[0])
            if (len(checkPattern) != 0):
                vidID = checkPattern[0]
                winner_IDs.append(vidID)
                break
                
    for vid in winner_IDs:
        try:
            print(f'Trying to add {vid} to playlist')
            add_video_to_playlist(credentials, vid, PLAYLIST_ID)
        except:
            print(BEG_RED + f'Failed to add video {vid} to playlist {PLAYLIST_ID}' + END_RED) 
                
    #Recurse and start calculate/sleep process over
    await calculateTimeToWinner(credentials)
    
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
    await bot.tree.sync()
    #await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
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

    #TODO: Commented out below because Google auth doesn't work without a browser
    #credentials = await get_authenticated_service()

    #await asyncio.wait_for(calculateTimeToWinner(credentials), timeout=604801)

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
    repeat = False
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
                repeat = checkLink(info)
                break
       
    if repeat == True:
        og_info = vids[vidID]
        await sendTo.send(f'<@{author_id}> {newLink} was posted by <@{og_info[2]}> on {og_info[3]}')

    await bot.process_commands(ctx)
    
################################################################################################################################################
'''All the commands to run from within discord chat below'''
################################################################################################################################################
'''
@bot.command()
async def test(ctx):
    await ctx.send('```md#Hello```')
'''
################################################################################################################################################
@bot.tree.command(name="vampire", description="Sends the vampire Nic Cage quote")
#@bot.command()
async def vampire(ctx):    
    _myQuote = NicCageQuotes[1]
    myQuote = _myQuote.split("; ")
    print("Channel Name: " + str(ctx.channel.name) + ", Channel ID: " + str(ctx.channel.id))
    await ctx.reply(myQuote[0])
    print('Quote: ' + BEG_GREEN + myQuote[0] + END_GREEN)
    try:
        voice = ctx.voice_client.play(discord.FFmpegPCMAudio(str('./sounds/' + myQuote[1].strip())))
    except:
        print(BEG_RED + "No active voice channel - Clip not played" + END_RED)
################################################################################################################################################
@bot.tree.command(name="face", description="Sends the face Nic Cage quote")
#@bot.command()
async def face(ctx):
    _myQuote = NicCageQuotes[20]
    myQuote = _myQuote.split("; ")
    print("Channel Name: " + str(ctx.channel.name) + ", Channel ID: " + str(ctx.channel.id))
    await ctx.reply(myQuote[0])
    print('Quote: ' + BEG_GREEN + myQuote[0] + END_GREEN)
    try:
        voice = ctx.voice_client.play(discord.FFmpegPCMAudio(str('./sounds/' + myQuote[1].strip())))
    except:
        print(BEG_RED + "No active voice channel - Clip not played" + END_RED)
################################################################################################################################################
@bot.tree.command(name="speak", description="Sends a random Nic Cage quote")
#@bot.command()
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
'''
@bot.tree.command(name="vampire", description="Sends a random Nicolas Cage quote.")
@bot.command()
async def helpme(ctx):
       await ctx.reply("Commands: !join !qjoin !leave !qleave !speak !helpme !gif")
'''
################################################################################################################################################
@bot.tree.command(name="gif", description="Sends a random Nicolas Cage GIF")
#@bot.command()
async def gif(interaction: discord.Interaction,):
    randomGif = random.randint(0,3)
    await interaction.response.send_message(gifs[randomGif])
################################################################################################################################################
@bot.tree.command(name="join", description="Nic Cage bot joins youra active voice channel")
#@bot.command()
async def join(ctx):
    try:
        voice = await ctx.author.voice.channel.connect()
        await ctx.reply("Nic is here to party, woo!")
        voice.play(discord.FFmpegPCMAudio('./sounds/woo.mp3'))
    except:
        print(BEG_RED + "No members active in voice channel - Channel not joined" + END_RED)
        await ctx.reply("I can't join a voice channel without any active members")
################################################################################################################################################
@bot.tree.command(name="qjoin", description="Nic Cage bot SILENTLY joins your active voice channel")
#@bot.command()
async def qjoin(ctx):
    try:
        voice = await ctx.author.voice.channel.connect()
        await ctx.reply("Nic is here to party, woo!")
    except:
        print(BEG_RED + "No members active in voice channel - Channel not joined" + END_RED)
        await ctx.reply("I can't join a voice channel without any active members")
################################################################################################################################################
@bot.tree.command(name="leave", description="Nic Cage bot leaves your active voice channel")
#@bot.command()
async def leave(ctx):
    try:
        voice = ctx.voice_client.play(discord.FFmpegPCMAudio('./sounds/silence.mp3'))
        await ctx.reply("Hurray for the sounds of fucking silence")
        time.sleep(5)
        voice = await ctx.voice_client.disconnect()
    except:
        await ctx.reply("I'm not in any channels genious")
################################################################################################################################################
@bot.tree.command(name="qleave", description="Nic Cage bot SILENTLY joins your active voice channel ")
#@bot.command()
async def qleave(ctx):
    try:
        await ctx.reply("Hurray for the sounds of fucking silence")
        time.sleep(5)
        voice = await ctx.voice_client.disconnect()
    except:
        await ctx.reply("I'm not in any channels genious")
################################################################################################################################################
@bot.tree.command(name="winner", description="Auto-picks best video of the week (currently broken)")
#@bot.command()
async def winner(interaction: discord.Interaction):
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
                    #print(reactions)
                    #print(type(reactions[0]))
                    #print(reactions[0].count)
                    reactionCount += reaction.count

                if reactionCount > mostReactions:
                    #print("Found winner with higher total count. Winners reset.")
                    winners = []

                if reactionCount >= mostReactions:
                    #print(f'Reaction count {reactionCount} Most reactions {mostReactions}')
                    mostReactions = reactionCount
                    title = getTitleFromURL(newMessage)
                    title = title.split(" - YouTube")[0]
                    winners.append([newMessage, title, reactionCount, author_id])
                    #print(f'Video added to winner. There are {reactionCount} reactions for {title}')

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

        print(f'Winning video(s): {winningTitles}')
        #if  not ctx.channel.id == getID:
            #await ctx.reply(f'**Winner:**\n\n{winningTitles}\n\n{winningAuthors}')
        await channel.send(f'**Winner:**\n\n{winningTitles}\n\n{winningAuthors}')

    else:
        print(BEG_RED + "No reactions found - Unable to calculate winner" + END_RED)
        await sendTo.send(f'**No votes found. Trigger a manual winner with the !winner command**\n{EMPTY_WINNER}')

    end_time = time.time()
    log_time = end_time - start_time

    if isWinner == True:
        print("\n" + BEG_BLUE +f'Winner of best video of the week computed in {log_time:.2f}s' + END_BLUE)

    return winners
################################################################################################################################################
@bot.tree.command(name="ask_openai", description="Responds to a prompt using OpenAI (ChatGPT)")
#@bot.command()
async def ask_openai(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    try:
        print(BEG_YELLOW + f"Working on question: {question}" + END_YELLOW)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Nicolas Cage the famous actor and you're a little bit wacky."},
            {"role": "user", "content": question}
        ])

        answer = response.choices[0].message.content
        print(BEG_GREEN + f'ChatGPT: {answer}' + END_GREEN)
        await interaction.followup.send(answer)

    except:
        print(BEG_RED + "I can't answer that" + END_RED)
        await interaction.followup.send("I can't answer that")
################################################################################################################################################               
@bot.tree.command(name="create_openai", description="Creates images from a prompt using OpenAI (ChatGPT)")
#@bot.command()
async def create_openai(interaction: discord.Interaction, user_prompt: str):
    await interaction.response.defer()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #image_model = "dall-e-2"
    image_model = "dall-e-3"

    try:
        print(BEG_YELLOW + f"Working on request: {user_prompt}" + END_YELLOW)
        #Interaction has already been responded to error
        #await interaction.response.send_message("I'll see what I can do")
        my_response = client.images.generate(
            model = image_model,
            prompt = user_prompt,
            size = "1024x1024",
            quality = "hd",
            n = 1,
            style = "natural"
        )
        image_url = my_response.data[0].url
        #embed = discord.Embed(title=user_prompt)
        #embed.set_image(url="image_url")
        print(BEG_GREEN + image_url + END_GREEN)
        #myPrompt = "`" + user_prompt + "`" 
        await interaction.followup.send(image_url)

    except openai.BadRequestError as e:
        print(BEG_RED + f"Caught 'Bad Request Error':\n {e}" + END_RED)
        await interaction.followup.send("I can't do that")
################################################################################################################################################
@bot.tree.command(name="ask_gemini", description="Responds to a prompt using using Google Gemini")
#@bot.command()
async def ask_gemini(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    my_role = "You are Nicolas Cage the famous actor. Keep responses somewhat succinct, but still with flair."
    my_model = "gemini-2.0-flash"
    #my_model = "gemini-1.5-flash"

    try:
        print(BEG_YELLOW + f"Working on question: {prompt}" + END_YELLOW)
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        full_prompt = my_role + prompt #Concatenate the role and prompt.

        response = client.models.generate_content(model=my_model, contents=full_prompt)

        print(BEG_YELLOW + f"Gemini response: {response.text}" + END_YELLOW)
        await interaction.followup.send(response.text)
        #await ctx.reply(response.text)

    except Exception as e:
        print(BEG_RED + f"An error occurred: {e}" + END_RED)
        await interaction.followup.send("An error occurred while processing your request.")
        #await ctx.reply("An error occurred while processing your request.") 
################################################################################################################################################
@bot.tree.command(name="create_gemini", description="Creates images from a prompt using Google Gemini")
#@bot.command()
async def create_gemini(interaction: discord.Interaction, user_prompt: str):
    await interaction.response.defer()
    directory = "images"
    names = ["one", "two", "three", "four"]
    images = []
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    try:
        print(BEG_YELLOW + f"Working on prompt: {user_prompt}" + END_YELLOW)
        #Interaction has already been responded to error
        #await interaction.response.send_message("I'll see what I can do")
        my_response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=user_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=4,
            )
        )

        for name, generated_image in zip(names, my_response.generated_images):
            file_name = f"output_image_{name}.png"
            file_path = os.path.join(directory, file_name)
            image = Image.open(BytesIO(generated_image.image.image_bytes))

            with open(file_path, "wb") as file:
                image.save(file_path)
            print(f"Image saved as {file_name}")

            if os.path.exists(file_path):
                with open(file_path, 'rb') as fp:
                    image_bytes = fp.read()
                    image_io = BytesIO(image_bytes)
                    images.append(discord.File(image_io, filename=os.path.basename(file_path)))
            else:
                print("Image not found")

        if images:
            print(BEG_GREEN + f"Completed prompt: {user_prompt}" + END_GREEN)
            await interaction.followup.send(files=images)

    except:
        print(BEG_RED + "I can't do that" + END_RED)
        await interaction.followup.send("I can't do that")
###############################################################################################################################################
@bot.tree.command(name="kill", description="Turn off the bot with a command")
#@bot.command()
async def kill(interaction: discord.Interaction,):
    await interaction.response.send_message("Goodbye cruel world")
    print("Attempting to shut down program")
    quit()
################################################################################################################################################
bot.run(TOKEN)
