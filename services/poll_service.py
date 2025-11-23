import discord
import asyncio
import datetime
import time

class PollService:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.is_running = False
        
    async def start(self):
        """Start the movie poll service"""
        self.is_running = True
        
        # Start the background task
        asyncio.create_task(self.calculate_time_to_poll())
        print("Poll service started successfully")
        
    async def stop(self):
        """Stop the movie poll service"""
        self.is_running = False
        
    async def calculate_time_to_poll(self):
        """Calculate when to poll movieboys and run on schedule"""
        while self.is_running:
            try:
                now = datetime.datetime.now()
            
                # Parse schedule from config (e.g., "monday-14:00")
                schedule = self.config.get('movie_poll.schedule', 'wednesday-18:00')
                day_name, time_str = schedule.lower().split('-')
                hour, minute = map(int, time_str.split(':'))
            
                # Map day names to weekday numbers (0=Monday, 6=Sunday)
                day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                           'friday': 4, 'saturday': 5, 'sunday': 6}
                target_weekday = day_map[day_name]
            
                # Calculate days until target day
                days_ahead = (target_weekday - now.weekday()) % 7
                if days_ahead == 0 and (now.hour > hour or (now.hour == hour and now.minute >= minute)):
                    days_ahead = 7  # Already passed today, schedule for next week
            
                next_announcement = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + datetime.timedelta(days=days_ahead)
                
                wait_seconds = (next_announcement - now).total_seconds()
                
                print(f"Next movie  poll scheduled for: {next_announcement}")
                print(f"Waiting {wait_seconds/3600:.2f} hours until next poll announcement")
                
                # Wait until next Monday 2PM
                await asyncio.sleep(wait_seconds)

                await self._send_poll()
                
            except Exception as e:
                print(f"Error in schedule service: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
 
    async def _send_poll(self):
        """Send poll to Discord"""
        send_channel = self.bot.get_poll_channel()
        role_id = self.bot.get_movieboys_role_id()
        poll_window = self.bot.get_poll_window()

        #print(f"DEBUG: Poll Window = {poll_window}")  # Add this line
        #print(f"DEBUG: Role ID = {role_id}")  # Add this line
        #print(f"DEBUG: Bot mode = {self.bot.config.mode}")  # Add this too
    
        # Create a Poll object
        poll = discord.Poll(
            question="***Pick your days***?",
            duration=datetime.timedelta(hours=poll_window),  # Poll stays open for 24 hours
            multiple=True  # Allow multiple selections
        )
    
        # Add poll options
        poll.add_answer(text="Thursday", emoji="🍿")
        poll.add_answer(text="Friday", emoji="🍿")
        poll.add_answer(text="Saturday", emoji="🍿")
        poll.add_answer(text="Sunday", emoji="🍿")
    
        # Send the message with the poll
        await send_channel.send(
            content=f"<@&{role_id}> **It's Movie Time!**",
            poll=poll
        )
    
        print(f'Movie poll sent')