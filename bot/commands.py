import discord
from discord import app_commands
from discord.ext import commands
import random
import time
import os
import asyncio
from data.file_handlers import QuoteManager, LinkPatterns
from services.ai_service import OpenAIService, GeminiService
from data.database import CookieDatabase

class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quote_manager = QuoteManager("data/quotes.txt")
        self.last_int = -1
        self.openai_service = OpenAIService()
        self.gemini_service = GeminiService()
        # Pass the bot mode to the cookie database
        self.cookie_db = CookieDatabase(mode=bot.config.mode)
        
########################################################################################################################################################
    @app_commands.command(name="help", description="Get the bot commands")
    async def help(self, interaction: discord.Interaction):
        commands_list = [
            "/movieboys", "/winner", "/speak", "/join", "/qjoin", "/leave",
            "/qleave", "/ask_openai", "/ask_gemini", "/create_openai", 
            "/create_gemini", "/vampire", "/face", "/gif", "/kill", "/cookie", "/leaderboard", "/mycookies"
        ]
        await interaction.response.send_message("`" + "\n".join(commands_list) + "`")
    
########################################################################################################################################################
    @app_commands.command(name="movieboys", description="Displays movieboys.us link")
    async def movieboys(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://movieboys.us")
    
########################################################################################################################################################
    @app_commands.command(name="speak", description="Sends a random Nic Cage quote")
    async def speak(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client if interaction.guild else None
        my_random_int = self.quote_manager.get_random_quote_index(self.last_int)
        self.last_int = my_random_int
        
        quote, sound_file = self.quote_manager.get_quote(my_random_int)
        
        if voice_client and voice_client.is_connected():
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegPCMAudio(f'./sounds/{sound_file}'))
                await interaction.followup.send(quote)
            else:
                await interaction.followup.send("I'm already playing audio!")
        else:
            await interaction.followup.send(quote)
    
########################################################################################################################################################
    @app_commands.command(name="vampire", description="Sends the vampire Nic Cage quote")
    async def vampire(self, interaction: discord.Interaction):
        await self._play_specific_quote(interaction, 1)
    
########################################################################################################################################################
    @app_commands.command(name="face", description="Sends the face Nic Cage quote")
    async def face(self, interaction: discord.Interaction):
        await self._play_specific_quote(interaction, 20)
########################################################################################################################################################   
    async def _play_specific_quote(self, interaction: discord.Interaction, quote_index: int):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client if interaction.guild else None
        quote, sound_file = self.quote_manager.get_quote(quote_index)
        
        if voice_client and voice_client.is_connected():
            # Check if bot is in the same voice channel as user
            if interaction.user.voice and interaction.user.voice.channel != voice_client.channel:
                await interaction.followup.send("I'm already in another voice channel!")
                return
                
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegPCMAudio(f'./sounds/{sound_file}'))
                await interaction.followup.send(quote)
            else:
                await interaction.followup.send("I'm already playing audio!")
        else:
            await interaction.followup.send(quote)
    
########################################################################################################################################################
    @app_commands.command(name="gif", description="Sends a random Nicolas Cage GIF")
    async def gif(self, interaction: discord.Interaction):
        random_gif = random.choice(self.bot.config.gifs)
        await interaction.response.send_message(random_gif)
    
########################################################################################################################################################
    @app_commands.command(name="join", description="Nic Cage bot joins your active voice channel")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            if interaction.guild.voice_client:
                await interaction.response.send_message("I'm already in a voice channel!", ephemeral=True)
                return
            
            await interaction.response.defer()
            voice_channel = interaction.user.voice.channel
            voice_client = await voice_channel.connect()
            
            time.sleep(5)
            voice_client.play(discord.FFmpegPCMAudio('./sounds/woo.mp3'))
            await interaction.followup.send("Nic is here to party, woo!")
        else:
            await interaction.response.send_message("You must be in a voice channel to use this command")
    
########################################################################################################################################################
    @app_commands.command(name="qjoin", description="Nic Cage bot SILENTLY joins your active voice channel")
    async def qjoin(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            if interaction.guild.voice_client:
                await interaction.response.send_message("I'm already in a voice channel!", ephemeral=True)
                return
            
            await interaction.response.defer()
            voice_channel = interaction.user.voice.channel
            await voice_channel.connect()
            await interaction.followup.send("Nic is here to party, woo!")
        else:
            await interaction.response.send_message("You must be in a voice channel to use this command!")
    
########################################################################################################################################################
    @app_commands.command(name="leave", description="Nic Cage bot leaves your active voice channel")
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client and voice_client.is_connected():
            await interaction.response.defer()
            voice_client.play(discord.FFmpegPCMAudio('./sounds/silence.mp3'))
            await interaction.followup.send("Hurray for the sounds of fucking silence")
            time.sleep(5)
            await voice_client.disconnect()
        else:
            await interaction.response.send_message("I'm not in a voice channel!")
    
########################################################################################################################################################
    @app_commands.command(name="qleave", description="Nic Cage bot SILENTLY leaves your active voice channel")
    async def qleave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client and voice_client.is_connected():
            await interaction.response.defer()
            await interaction.followup.send("Hurray for the sounds of fucking silence")
            time.sleep(5)
            await voice_client.disconnect()
        else:
            await interaction.response.send_message("I'm not in a voice channel!")

########################################################################################################################################################
    @app_commands.command(name="winner", description="Calculate best video of the week")

    async def winner(self, interaction: discord.Interaction):
        try:
            # Acknowledge immediately to prevent timeout
            await interaction.response.send_message("Calculating winner...", ephemeral=True)
            
            if hasattr(self.bot, 'winner_service') and self.bot.winner_service:
                winners = await self.bot.winner_service.calculate_winners()
                
                if winners:
                    # Add to playlist if YouTube service is available and authenticated
                    if (self.bot.config.get('winner.add_to_playlist', False) and 
                        hasattr(self.bot, 'youtube_service') and 
                        self.bot.youtube_service and 
                        self.bot.youtube_service.is_authenticated()):
                        
                        print(f"Manual winner: Attempting to add {len(winners)} winner(s) to YouTube playlist...")
                        await self.bot.winner_service._add_winners_to_playlist(winners)
                    
                    # Send announcement
                    await self.bot.winner_service._send_winner_announcement(winners)
                    await interaction.edit_original_response(content="✅ Winner announced in the video channel!")
                else:
                    await interaction.edit_original_response(
                        content=f"**No votes found.**\n{self.bot.config.get('constants.empty_winner_gif')}"
                    )
            else:
                await interaction.edit_original_response(content="❌ Winner service is not available")
                
        except Exception as e:
            print(f"Error in winner command: {e}")
            try:
                await interaction.edit_original_response(content="❌ Error calculating winner")
            except:
                # If we can't edit, try sending a new message
                try:
                    await interaction.followup.send("Error calculating winner", ephemeral=True)
                except:
                    pass
    
########################################################################################################################################################
    @app_commands.command(name="ask_openai", description="Responds to a prompt using OpenAI (ChatGPT)")
    async def ask_openai(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        try:
            response = await self.openai_service.ask_question(question)
            # Split long responses to avoid Discord character limit
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(response)
        except Exception as e:
            print(f"OpenAI error: {e}")
            await interaction.followup.send("I can't answer that right now. Try again later.")
    
########################################################################################################################################################
    @app_commands.command(name="create_openai", description="Creates images from a prompt using OpenAI (ChatGPT)")
    async def create_openai(self, interaction: discord.Interaction, user_prompt: str):
        await interaction.response.defer()
        try:
            image_url = await self.openai_service.create_image(user_prompt)
            await interaction.followup.send(image_url)
        except Exception as e:
            print(f"OpenAI image creation error: {e}")
            await interaction.followup.send("I can't create that image right now. Try again later.")

########################################################################################################################################################
    @app_commands.command(name="ask_gemini", description="Responds to a prompt using Google Gemini")
    async def ask_gemini(self, interaction: discord.Interaction, prompt: str):
        print(f"/ask_gemini command triggered by {interaction.user}")
        print(f"Prompt: {prompt}")
        
        await interaction.response.defer()
        
        try:
            print("Processing with Gemini service...")
            response = await self.gemini_service.ask_question(prompt)
            
            print(f"Preparing to send response ({len(response)} characters)")
            
            # Split long responses to avoid Discord character limit
            if len(response) > 2000:
                print("✂️esponse too long, splitting into chunks...")
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                print(f"Split into {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks):
                    await interaction.followup.send(chunk)
                    print(f"Sent chunk {i+1}/{len(chunks)}")
            else:
                await interaction.followup.send(response)
                print("✅ Response sent successfully")
                
            print("/ask_gemini command completed successfully")
                
        except Exception as e:
            print(f"Error in /ask_gemini: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()  # This will print the full stack trace
            
            try:
                await interaction.followup.send("I couldn't process your request with Gemini. Please try again later.")
                print("Sent error message to user")
            except Exception as followup_error:
                print(f"Could not send error message to Discord: {followup_error}")    
    
########################################################################################################################################################
    @app_commands.command(name="create_gemini", description="Creates images from a prompt using Google Gemini")
    async def create_gemini(self, interaction: discord.Interaction, user_prompt: str):
        await interaction.response.defer()
        try:
            images = await self.gemini_service.create_images(user_prompt)
            await interaction.followup.send(files=images)
        except Exception as e:
            print(f"Gemini image creation error: {e}")
            await interaction.followup.send("I can't create those images right now. Try again later.")
    
########################################################################################################################################################
    @app_commands.command(name="cookie", description="Track your cookies")
    async def cookie(self, interaction: discord.Interaction, cookies: str):
        try:
            # Acknowledge immediately to prevent timeout
            await interaction.response.send_message("Tracking cookies...", ephemeral=False)
            
            num_cookies = int(cookies)
            if num_cookies < 0:
                await interaction.edit_original_response(content="You can't un-eat cookies! Well, maybe you can, but I don't want to know about it.")
                return
                
            total_cookies = self.cookie_db.add_cookies(interaction.user.id, num_cookies)
            
            # Create fun responses based on cookie count
            if num_cookies == 0:
                message = f"**{interaction.user}** is watching their figure. Zero cookies consumed. Total: {total_cookies}"
            elif num_cookies == 1:
                message = f"**{interaction.user}** had a single cookie. Moderation is key! Total: {total_cookies}"
            elif num_cookies <= 3:
                message = f"**{interaction.user}** enjoyed {num_cookies} cookies. A nice snack! Total: {total_cookies}"
            elif num_cookies <= 6:
                message = f"**{interaction.user}** gobbled {num_cookies} cookies. Someone's hungry! Total: {total_cookies}"
            elif num_cookies <= 10:
                message = f"**{interaction.user}** demolished {num_cookies} cookies. Cookie monster alert! Total: {total_cookies}"
            elif num_cookies <= 20:
                message = f"**{interaction.user}** crushed {num_cookies} cookies. Cookie :ocean: tsunami :ocean: Total: {total_cookies}"
            elif num_cookies <= 50:
                message = f"**{interaction.user}** consumed {num_cookies} cookies! 🚨 COOKIE EMERGENCY 🚨 Total: {total_cookies}"
            else:
                message = f"**{interaction.user}** gorged on {num_cookies} cookies...save some for the rest of us...Total: {total_cookies}"
            
            embed = discord.Embed(
                title=":cookie: Cookie Counter :cookie:",
                description=message,
                color=discord.Color.gold()
            )
            await interaction.edit_original_response(content=None, embed=embed)
            
        except ValueError:
            await interaction.edit_original_response(content="Please enter a valid number of cookies.")
        except Exception as e:
            print(f"Cookie tracking error: {e}")
            await interaction.edit_original_response(content="Something went wrong with cookie tracking. Try again.")
    
########################################################################################################################################################
    @app_commands.command(name="leaderboard", description="Who's eaten the most cookies?")
    async def leaderboard(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Fetching cookie leaderboard...", ephemeral=False)
            
            # Handle DMs - leaderboard requires a guild context
            if interaction.guild is None:
                await interaction.edit_original_response(content="The cookie leaderboard is only available in server channels since it shows server members.")
                return
            
            leaderboard_data = self.cookie_db.get_leaderboard(interaction.guild)
            
            if not leaderboard_data:
                embed = discord.Embed(
                    title=":cookie: Cookie Leaderboard :cookie:",
                    description="No cookies have been eaten yet! Someone grab a snack!",
                    color=discord.Color.gold()
                )
                await interaction.edit_original_response(content=None, embed=embed)
                return
            
            leaderboard_display = []
            for i, (user_id, total) in enumerate(leaderboard_data, 1):
                member = interaction.guild.get_member(int(user_id))
                name = member.display_name if member else f"User ID {user_id}"
                
                # Add emoji based on rank
                if i == 1:
                    rank_emoji = "👑"
                elif i == 2:
                    rank_emoji = "🥈"
                elif i == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = "🍪"
                    
                leaderboard_display.append(f"{rank_emoji} **{name}**: {total} cookies")
            
            embed = discord.Embed(
                title=":cookie: Cookie Leaderboard :cookie:",
                description="\n".join(leaderboard_display),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Keep eating those cookies!")
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            print(f"Leaderboard error: {e}")
            await interaction.edit_original_response(content="Couldn't fetch the leaderboard right now. Try again later.")

########################################################################################################################################################
    @app_commands.command(name="mycookies", description="Check how many cookies you've eaten")
    async def mycookies(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Checking your cookies...", ephemeral=True)
            
            conn = self.cookie_db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(num_cookies) FROM cookies WHERE user_id = ?", (interaction.user.id,))
            total_cookies = cursor.fetchone()[0] or 0
            conn.close()
            
            # Fun messages based on total cookies
            if total_cookies == 0:
                message = "You haven't eaten any cookies yet! What are you waiting for?"
            elif total_cookies <= 10:
                message = f"You've eaten {total_cookies} cookies. A good start!"
            elif total_cookies <= 50:
                message = f"You've consumed {total_cookies} cookies. You're getting there!"
            elif total_cookies <= 100:
                message = f"Wow! {total_cookies} cookies! You really love your snacks!"
            elif total_cookies <= 200:
                message = f"Amazing! {total_cookies} cookies! You're a cookie connoisseur!"
            else:
                message = f"INCREDIBLE! {total_cookies} cookies! You are the Cookie Master! 🍪👑"
            
            embed = discord.Embed(
                title=f"{interaction.user.display_name}'s Cookie Stats",
                description=message,
                color=discord.Color.gold()
            )
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            print(f"MyCookies error: {e}")
            await interaction.edit_original_response(content="Couldn't fetch your cookie stats. Try again later.")

########################################################################################################################################################
    @app_commands.command(name="test_poll", description="Test poll integration")
    async def test_poll(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Trying to make the poll...", ephemeral=True)
            await self.bot.poll_service._send_poll()
            await interaction.edit_original_response(content="✅ Poll sent successfully!")
            print("Poll sent successfully")
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Failed to make the poll: {e}")
            print(f"Failed to send poll: {e}")

########################################################################################################################################################
    @app_commands.command(name="test_youtube", description="Test YouTube playlist integration")
    async def test_youtube(self, interaction: discord.Interaction, video_url: str):
        """Test if YouTube playlist integration is working"""
        await interaction.response.send_message("Testing YouTube integration...", ephemeral=True)
        
        if not hasattr(self.bot, 'youtube_service') or not self.bot.youtube_service:
            await interaction.edit_original_response(content="❌ YouTube service not available")
            return
            
        if not self.bot.youtube_service.is_authenticated():
            await interaction.edit_original_response(content="❌ YouTube not authenticated")
            return
            
        # Extract video ID from URL
        video_id = LinkPatterns.extract_video_id(video_url)
        if not video_id:
            await interaction.edit_original_response(content="❌ Invalid YouTube URL")
            return
            
        try:
            # Try to add the video to playlist
            self.bot.youtube_service.add_video_to_playlist(video_id)
            await interaction.edit_original_response(content=f"✅ Successfully added video to playlist!\nVideo ID: {video_id}")
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Failed to add video: {str(e)}")

########################################################################################################################################################
    @app_commands.command(name="force_sync", description="Force sync commands (admin only)")
    async def force_sync(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.bot.config.admin_user_id:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
    
        await interaction.response.defer(ephemeral=True)
        synced = await self.bot.tree.sync()
        await interaction.followup.send(f"✅ Synced {len(synced)} commands!")

########################################################################################################################################################
    async def _shutdown_bot(self):
        """Helper method to shutdown the bot gracefully"""
        await asyncio.sleep(2)  # Give time for the response to send
        await self.bot.close()
########################################################################################################################################################
async def setup(bot):
    await bot.add_cog(BotCommands(bot))
