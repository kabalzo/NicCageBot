import discord
from discord.ext import commands, tasks
from data.file_handlers import QuoteManager, LinkPatterns
from services.winner_service import WinnerService
from services.poll_service import PollService
from data.database import LinkDatabase
from bot.utils import soft_scan_channel, check_deleted_messages_fast, check_link_realtime
import asyncio

class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quote_manager = QuoteManager("data/quotes.txt")
        self.winner_service = WinnerService(bot)
        self.poll_service = PollService(bot)
        self.link_db = LinkDatabase(mode=bot.config.mode)
        self.message_cache = set()  # Cache of recent message IDs
        self.initial_scan_complete = False
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'User name: {self.bot.user.name} - ID: {str(self.bot.user.id)}')
        print('We have logged in as {0.user}\n'.format(self.bot))
        print(f'Using database: link_tracker_{self.bot.config.mode}.db')
        
        # Build message cache for fast deletion checks
        await self._build_message_cache()
        
        # Perform initial soft scan on startup (only once)
        channel = self.bot.get_monitor_channel()
        if channel and not self.initial_scan_complete:
            print("Performing initial soft scan...")
            await soft_scan_channel(channel, self.link_db)
            
            # Use fast deletion check with cache (only once)
            print("Performing initial deletion check...")
            await check_deleted_messages_fast(channel, self.link_db, self.message_cache)
            
            self.initial_scan_complete = True
            print("Initial startup scans completed")
        
        # Start periodic deletion checks (every hour) - won't run immediately
        self.periodic_deletion_check.start()
        print('Bot is now in listening state with periodic deletion checks enabled\n')

        # Start winner calculation service if enabled in config
        if self.bot.config.get('bot.auto_winner', False):
            try:
                await self.winner_service.start()
                print("Winner service started automatically")
            except Exception as e:
                print(f"Failed to start winner service: {e}")
        # Start poll message service if enabled in config
        if self.bot.config.get('bot.auto_poll', False):
            try:
                await self.bot.poll_service.start()
                print("Poll service started automatically")
            except Exception as e:
                print(f"Failed to start poll service: {e}")
    
    async def _build_message_cache(self):
        """Build a cache of recent message IDs for faster deletion checks"""
        print("Building message cache for faster deletion checks...")
        channel = self.bot.get_monitor_channel()
        if not channel:
            print("Could not find monitor channel for cache building")
            return
            
        self.message_cache.clear()
        cache_count = 0
        
        # Cache the most recent 5000 messages
        async for message in channel.history(limit=5000):
            self.message_cache.add(message.id)
            cache_count += 1
            
        print(f"Message cache built with {cache_count} messages")
    
    @tasks.loop(hours=1)
    async def periodic_deletion_check(self):
        """Check for deleted messages every hour (fast cache-based check)"""
        print("Running periodic deletion check...")
        channel = self.bot.get_monitor_channel()
        if channel:
            # Refresh cache with recent messages before checking
            await self._refresh_cache_recent()
            
            deleted_count = await check_deleted_messages_fast(channel, self.link_db, self.message_cache)
            if deleted_count > 0:
                print(f"Periodic check: Marked {deleted_count} messages as deleted")
            else:
                print("Periodic check: No new deletions found")
        else:
            print("Periodic check: Could not find monitor channel")
    
    async def _refresh_cache_recent(self):
        """Refresh cache with only the most recent messages"""
        channel = self.bot.get_monitor_channel()
        if not channel:
            return
            
        # Add only the most recent 100 messages to cache
        async for message in channel.history(limit=100):
            self.message_cache.add(message.id)
    
    @periodic_deletion_check.before_loop
    async def before_periodic_check(self):
        """Wait until the bot is ready and initial scan is complete before starting periodic tasks"""
        await self.bot.wait_until_ready()
        # Additional delay to ensure initial scan is complete
        await asyncio.sleep(10)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.channel.id == self.bot.config.channels['monitor']):
            # Add to cache
            self.message_cache.add(message.id)
            
            if message.content.startswith("https://"):
                print(f"New link detected: {message.content}")
                
                # Check for repeat links using database
                existing_link = await check_link_realtime(message, self.link_db)
                
                if existing_link:
                    print(f"Repeat link detected: {existing_link['video_id']}")
                    send_channel = self.bot.get_send_channel()
                    await send_channel.send(
                        f'<@{message.author.id}> {message.content} was posted by '
                        f'<@{existing_link["author_id"]}> on {existing_link["created_at"][:10]}'
                    )
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Handle message deletion to mark links as deleted"""
        if (message.channel.id == self.bot.config.channels['monitor']):
            # Remove from cache
            if message.id in self.message_cache:
                self.message_cache.remove(message.id)
            
            if message.content and message.content.startswith("https://"):
                print(f"Message deleted: {message.id}")
                self.link_db.mark_link_deleted(message.id)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Handle message edits (in case link is removed via edit)"""
        if (before.channel.id == self.bot.config.channels['monitor'] and 
            before.content and before.content.startswith("https://") and
            not after.content.startswith("https://")):
            
            print(f"Link removed via edit in message: {before.id}")
            self.link_db.mark_link_deleted(before.id)

async def setup(bot):
    await bot.add_cog(BotEvents(bot))
