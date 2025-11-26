import discord
import os
import logging
from discord.ext import commands
from config.config import Config
from services.youtube_service import YouTubeService
from services.winner_service import WinnerService
from services.poll_service import PollService

logger = logging.getLogger(__name__)

class NicCageBot(commands.Bot):
    def __init__(self, config: Config):
        self.config = config
        intents = discord.Intents.all()
        intents.message_content = True
        
        super().__init__(
            command_prefix=config.get('bot.prefix', '!'),
            intents=intents
        )
        
        self.youtube_service = None
        self.winner_service = None
        self.poll_service = None
        
    async def setup_hook(self):
        # Load extensions
        await self.load_extension('bot.events')
        await self.load_extension('bot.commands')
        
        # Sync commands globally
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
        
        # Initialize YouTube service
        try:
            self.youtube_service = YouTubeService(self.config)
            self.youtube_service.initialize_api_key()
            logger.info("YouTube service initialized with API key")
        except Exception as e:
            logger.error(f"YouTube service initialization failed: {e}")
        
        # Initialize Winner service
        try:
            self.winner_service = WinnerService(self)
            logger.info("Winner service initialized")
        except Exception as e:
            logger.error(f"Winner service initialization failed: {e}")

        # Initialize Poll service
        try:
            self.poll_service = PollService(self)
            logger.info("Poll service initialized")
        except Exception as e:
            logger.error(f"Poll service initialization failed: {e}")
        
    def get_monitor_channel(self):
        """Get the channel to monitor for links"""
        channel_id = self.config.channels['monitor']
        return self.get_channel(channel_id)
    
    def get_send_channel(self):
        """Get the channel to send notifications to"""
        channel_id = self.config.channels['send']
        return self.get_channel(channel_id)

    def get_poll_channel(self):
        """Get the channel to poll"""
        channel_id = self.config.channels['poll']
        return self.get_channel(channel_id)

    def get_movieboys_role_id(self):
        """Get the discord role to notify"""
        mode = self.config.mode
        role_id = self.config.get(f'movie_poll.{mode}.movie_boys_role')
        return role_id

    def get_poll_window(self):
        """Get the window that the poll stays open"""
        mode = self.config.mode
        window = self.config.get(f'movie_poll.window')
        return window
    
    async def on_ready(self):
        """Custom on_ready event handler"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is running in {self.config.mode} mode')
        logger.info(f'Monitoring channel: {self.config.channels["monitor"]}')
        logger.info(f'Sending to channel: {self.config.channels["send"]}')
        logger.info(f'Playlist ID: {self.config.playlist_id}')

def create_bot(mode_override=None):
    """Factory function to create and configure the bot"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "config.yaml")
    config = Config(config_path, mode_override)
    return NicCageBot(config)
