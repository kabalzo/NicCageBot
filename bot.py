#This is my Nic Cage bot
import random
import time
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import os

f = open("channels.txt", "r")
channelIDs = f.readlines()
#Channel that we're monitoring for repeat posts, check ref.txt
#For me only, [0:1] is prod [2:3] is test
getID = int(channelIDs[2])

#Channel that we send the repeat noticication message to, check ref.txt
sendID = int(channelIDs[3])

f.seek(0)
f.close()

#For use with start/stop.sh files instead of starting via shell
pid = os.getpid()
f = open("pid", "w")
f.write(str(pid))
f.seek(0)
f.close()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.message_content = True
lastInt = -1

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
    print("User name: " + bot.user.name)
    print("User id: " + str(bot.user.id))
    print('We have logged in as {0.user}\n'.format(bot))
    
    #Clear out the previous history and rebuild it everytime the bot starts
    f = open("links.txt", "w")
    f.write("")
    f.seek(0)
    f.close()
    
    #Get the channel from which to monitor repeat posts
    channel = bot.get_channel(getID)
    
    print("Starting link history log...")
    async for message in channel.history(limit=None):
        # Check if message has content
        if (message.content is not None and message.content.startswith("https")):
            f = open("links.txt", "a")
            # Add message content to list
            #print(f'{message.content} - {message.created_at}')
            f.write(message.content+"\n")
            f.seek(0)
            f.close()
            
    print('\33[32m' + "Link history log complete" + '\33[0m')
    print("Listening for new links")
################################################################################################################################################
@bot.event
async def on_message(ctx):
    hasBeenPosted = False
    if not((ctx.content.startswith("https://www.youtube.com")) or (ctx.content.startswith("https://youtu.be"))):
        pass
    else:
        print("New link detected")
        sendTo = bot.get_channel(sendID)
        newLink = ctx.content
        try:
            if (ctx.channel.id == getID): 
                #print(f'Message from {ctx.author} with  channel ID {ctx.channel.id}: {newLink}')
                f = open("links.txt", "r")
                myLinks = f.readlines()
                f.seek(0)
                f.close()
                
                #Iterate through the saved links and search for repeats
                #Linear in time, should change to a quicksort or something
                for link in myLinks:
                    link = link.strip("\n")
                    #print(link)
                    if (link == newLink):
                        #print(f'{newLink} has previously been posted by {ctx.author.id}')
                        print("Repeat link detected")
                        await sendTo.send(f'<@{ctx.author.id}> {newLink} has been posted previously')
                        hasBeenPosted = True
                        break
                if (hasBeenPosted == False and newLink.startswith("https")):
                    f = open("links.txt", "a")
                    f.write(newLink+"\n")
                    f.seek(0)
                    f.close()
                    print("New link: " + newLink + " has been logged")
        except:
            print('\33[31m' + "Link history not created." + '\33[0m')
    await bot.process_commands(ctx)
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
            print('Quote: ' + '\33[32m' + myQuote[0] + '\33[0m')
            try:
                voice = ctx.voice_client.play(discord.FFmpegPCMAudio(str('./sounds/' + myQuote[1].strip())))
            except:
                print('\33[31m' + "No active voice channel - Clip not played" + '\33[0m')
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
        print('\33[31m' + "No members active in voice channel - Channel not joined" + '\33[0m')
        await ctx.reply("I can't join a voice channel without any active members")
################################################################################################################################################
@bot.command()
async def qjoin(ctx):
    try:
        voice = await ctx.author.voice.channel.connect()
        await ctx.reply("Nic is here to party, woo! (!helpme)")
    except:
        print('\33[31m' + "No members active in voice channel - Channel not joined" + '\33[0m')
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
    


