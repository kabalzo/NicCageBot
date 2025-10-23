import discord
import os
from discord.ext import commands
from config.config import Config
from services.youtube_service import YouTubeService
from services.winner_service import WinnerService

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
        
    async def setup_hook(self):
        # Load extensions
        await self.load_extension('bot.events')
        await self.load_extension('bot.commands')
        
        # Sync commands globally
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        # Initialize YouTube service
        try:
            self.youtube_service = YouTubeService(self.config)
            self.youtube_service.initialize_api_key()
            print("YouTube service initialized with API key")
        except Exception as e:
            print(f"YouTube service initialization failed: {e}")
        
        # Initialize Winner service
        try:
            self.winner_service = WinnerService(self)
            print("Winner service initialized")
        except Exception as e:
            print(f"Winner service initialization failed: {e}")
        
    def get_monitor_channel(self):
        """Get the channel to monitor for links"""
        channel_id = self.config.channels['monitor']
        return self.get_channel(channel_id)
    
    def get_send_channel(self):
        """Get the channel to send notifications to"""
        channel_id = self.config.channels['send']
        return self.get_channel(channel_id)
    
    async def on_ready(self):
        """Custom on_ready event handler"""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is running in {self.config.mode} mode')
        print(f'Monitoring channel: {self.config.channels["monitor"]}')
        print(f'Sending to channel: {self.config.channels["send"]}')
        print(f'Playlist ID: {self.config.playlist_id}')

def create_bot(mode_override=None):
    """Factory function to create and configure the bot"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "config.yaml")
    config = Config(config_path, mode_override)
    return NicCageBot(config)
