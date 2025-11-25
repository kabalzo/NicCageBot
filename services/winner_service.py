import asyncio
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from data.file_handlers import LinkPatterns

class WinnerService:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.is_running = False
        
    async def start(self):
        """Start the winner calculation service"""
        self.is_running = True

        # Start the background task
        asyncio.create_task(self.calculate_time_to_winner())
        print("Winner service started successfully")
        
    async def stop(self):
        """Stop the winner calculation service"""
        self.is_running = False
        
    async def calculate_time_to_winner(self):
        """Calculate when to announce winners and run on schedule"""
        while self.is_running:
            try:
                now = datetime.datetime.now()
            
                # Parse schedule from config (e.g., "monday-14:00")
                schedule = self.config.get('winner.schedule', 'monday-14:00')
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
                
                print(f"Next winner calculation scheduled for: {next_announcement}")
                print(f"Waiting {wait_seconds/3600:.2f} hours until next winner announcement")
                
                # Wait until next Monday 2PM
                await asyncio.sleep(wait_seconds)
                
                # Calculate and announce winners
                await self._announce_winners()
                
            except Exception as e:
                print(f"Error in winner service: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _announce_winners(self):
        """Calculate and announce the winners"""
        print("Automatically announcing best video of the week...")
        
        winners = await self.calculate_winners()
        
        # Check if playlist addition is enabled and possible
        should_add_to_playlist = (
            winners and 
            self.config.get('winner.add_to_playlist', False) and 
            hasattr(self.bot, 'youtube_service') and 
            self.bot.youtube_service
        )
        
        if should_add_to_playlist:
            # Check authentication status WITHOUT triggering new auth
            if self.bot.youtube_service.is_authenticated():
                print(f"Attempting to add {len(winners)} winner(s) to YouTube playlist...")
                try:
                    await self._add_winners_to_playlist(winners)
                except Exception as e:
                    print(f"❌ Failed to add winners to playlist: {e}")
                    print("Continuing with winner announcement anyway...")
            else:
                print("⚠️  YouTube OAuth not authenticated - skipping playlist addition")
                print("To enable playlist integration:")
                print("1. Run the manual OAuth flow on a machine with a browser")
                print("2. Copy the token.pickle file to this server")
                print("3. Restart the bot or use /test_youtube to verify")
        elif winners:
            print(f"Found {len(winners)} winner(s) but playlist integration is not enabled")
        
        # ALWAYS send announcement regardless of playlist status
        await self._send_winner_announcement(winners)
        print("Winner announcement completed")
    
    async def calculate_winners(self, ctx=None):
        """Calculate the winners based on reaction counts"""
        print("Determining winner...")
        start_time = time.time()
        channel = self.bot.get_monitor_channel()
        
        if not channel:
            print("Error: Could not find monitor channel")
            return []
            
        winners = []
        most_reactions = 0
        
        async for message in channel.history(limit=None):
            if (message.content and 
                (message.content.startswith("Winner:") or 
                 message.content.startswith("**Winner:"))):
                break
                
            elif (message.content and message.content.startswith("https")):
                video_id = LinkPatterns.extract_video_id(message.content)
                if video_id:
                    reaction_count = self._count_reactions(message)
                    
                    if reaction_count > most_reactions:
                        winners = []
                        most_reactions = reaction_count
                    
                    if reaction_count >= most_reactions and reaction_count > 0:
                        title = await self._get_video_title(message.content)
                        winners.append({
                            'url': message.content,
                            'title': title,
                            'reaction_count': reaction_count,
                            'author_id': message.author.id,
                            'message': message
                        })
        
        end_time = time.time()
        log_time = end_time - start_time
        
        if winners:
            print(f'Winner of best video of the week computed in {log_time:.2f}s')
            print(f'Found {len(winners)} winner(s) with {most_reactions} reactions each')
        else:
            print("No reactions found - Unable to calculate winner")
            
        return winners
    
    def _count_reactions(self, message):
        """Count total reactions on a message"""
        reaction_count = 0
        for reaction in message.reactions:
            reaction_count += reaction.count
        return reaction_count
    
    async def _get_video_title(self, url):
        """Get video title from URL"""
        try:
            # Try using YouTube API first if available
            if hasattr(self.bot, 'youtube_service') and self.bot.youtube_service:
                video_id = LinkPatterns.extract_video_id(url)
                if video_id:
                    title = self.bot.youtube_service.get_video_title(video_id)
                    if title:
                        return title
            
            # Fallback to web scraping
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, features="lxml")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.split(" - YouTube")[0]
                return title
                
        except Exception as e:
            print(f"Error getting video title: {e}")
            
        return "Unknown Title"
    
    async def _add_winners_to_playlist(self, winners):
        """Add winning videos to YouTube playlist"""
        if not hasattr(self.bot, 'youtube_service'):
            print("YouTube service not available for playlist addition")
            return
        
        # DON'T authenticate here - just check if already authenticated
        if not self.bot.youtube_service.is_authenticated():
            print("YouTube not authenticated - cannot add to playlist")
            return
            
        winner_ids = []
        for winner in winners:
            video_id = LinkPatterns.extract_video_id(winner['url'])
            if video_id:
                winner_ids.append(video_id)
        
        print(f"Attempting to add {len(winner_ids)} videos to playlist: {winner_ids}")
        
        successful_adds = 0
        for video_id in winner_ids:
            try:
                print(f'Trying to add {video_id} to playlist...')
                self.bot.youtube_service.add_video_to_playlist(video_id)
                successful_adds += 1
                print(f'✅ Successfully added {video_id} to playlist')
            except Exception as e:
                print(f'❌ Failed to add video {video_id} to playlist: {e}')
        
        if successful_adds > 0:
            print(f"Successfully added {successful_adds}/{len(winner_ids)} videos to playlist")
        else:
            print(f"Failed to add any videos to playlist")
    
    async def _send_winner_announcement(self, winners):
        """Send winner announcement to Discord"""
        send_channel = self.bot.get_send_channel()
        monitor_channel = self.bot.get_monitor_channel()
        
        if not winners:
            print("No winners to announce")
            await send_channel.send(
                f'**No votes found. Trigger a manual winner with the /winner command**\n'
                f'{self.config.get("constants.empty_winner_gif")}'
            )
            return
        
        winning_titles = []
        winning_authors = []
        
        for winner in winners:
            winning_titles.append(f"`{winner['title']}`")
            winning_authors.append(f"<@{winner['author_id']}>")
        
        winning_titles_text = "\n".join(winning_titles)
        winning_authors_text = " & ".join(winning_authors)
        
        announcement = (
            f'**Winner:**\n\n{winning_titles_text}\n\n'
            f'Congrats on winning best vid of the week: {winning_authors_text}'
        )
        
        await monitor_channel.send(announcement)
        print(f'Winning video(s) announced: {winning_titles_text}')