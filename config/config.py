import os
import yaml
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path="config/config.yaml", mode_override=None):
        with open(config_path, 'r') as file:
            self.data = yaml.safe_load(file)
        
        # Replace environment variables
        self._replace_env_vars(self.data)
        
        # Ensure channel IDs are integers
        self._ensure_channel_ids_are_int()
        
        # Override mode from command line if provided
        if mode_override:
            self.data['bot']['mode'] = mode_override
            logger.info(f"Mode overridden to: {mode_override}")
    
    def _replace_env_vars(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    obj[key] = os.getenv(env_var, value)
                else:
                    self._replace_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                    env_var = item[2:-1]
                    obj[i] = os.getenv(env_var, item)
                else:
                    self._replace_env_vars(item)
    
    def _ensure_channel_ids_are_int(self):
        """Ensure all channel IDs are stored as integers"""
        for mode in ['prod', 'test']:
            if mode in self.data['channels']:
                for channel_type in ['monitor', 'send']:
                    if channel_type in self.data['channels'][mode]:
                        self.data['channels'][mode][channel_type] = int(
                            self.data['channels'][mode][channel_type]
                        )
    
    @property
    def token(self):
        return self.data['bot']['token']
    
    @property
    def mode(self):
        return self.data['bot']['mode']
    
    @property
    def channels(self):
        mode = self.mode
        return self.data['channels'][mode]
    
    @property
    def playlist_id(self):
        mode = self.mode
        return self.data['playlists'][mode]
    
    @property
    def admin_user_id(self):
        return self.data['bot']['admin_user_id']
    
    @property
    def gifs(self):
        return self.data['gifs']
    
    def get(self, path, default=None):
        keys = path.split('.')
        value = self.data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, {})
            else:
                return default
        return value if value != {} else default
