import random
import re

class QuoteManager:
    def __init__(self, quotes_file):
        self.quotes = self._load_quotes(quotes_file)
    
    def _load_quotes(self, file_path):
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    def get_random_quote_index(self, last_index=-1):
        while True:
            i = random.randint(0, len(self.quotes)-1)
            if i != last_index:
                return i
    
    def get_quote(self, index):
        quote_data = self.quotes[index].split("; ")
        return quote_data[0], quote_data[1].strip()

class LinkPatterns:
    DEFAULT_PAT_1 = r"https://www.youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)"
    DEFAULT_PAT_2 = r"https://youtube.com/watch\?[a-zA-Z]\=([a-zA-Z0-9\_\-]+)[\&].*"
    MOBILE_PAT_1 = r"https://youtu.be/([a-zA-Z0-9\_\-]+)\?.+"
    MOBILE_PAT_2 = r"https://youtu.be/([a-zA-Z0-9\_\-]+)"
    SHORTS_PAT_1 = r"https://www.youtube.com/shorts/([a-zA-Z0-9\_\-]+)"
    SHORTS_PAT_2 = r"https://youtube.com/shorts/([a-zA-Z0-9\_\-]+)\?.*"
    
    PATTERNS = [DEFAULT_PAT_1, DEFAULT_PAT_2, MOBILE_PAT_1, MOBILE_PAT_2, SHORTS_PAT_1, SHORTS_PAT_2]
    
    @classmethod
    def extract_video_id(cls, url):
        for pattern in cls.PATTERNS:
            match = re.findall(pattern, url)
            if match:
                return match[0]
        return None
