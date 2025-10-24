# 🎬 NicCageBot

A feature-rich Discord bot built with discord.py that combines Nicolas Cage movie quotes, AI interactions, and intelligent YouTube video tracking for Discord communities.

## 📖 Project Overview

NicCageBot started as a joke but evolved into a comprehensive Discord bot with multiple features:

- **Nicolas Cage quotes and audio clips** - Send random quotes from Nic Cage movies with audio playback in voice channels
- **YouTube duplicate detection** - Monitors channels for repeated video posts and notifies users
- **Weekly video winner tracking** - Automatically calculates the best video of the week based on reactions
- **AI integrations** - Ask questions and generate images using OpenAI (ChatGPT) and Google Gemini
- **Cookie tracking system** - Fun leaderboard system for tracking cookie consumption
- **YouTube playlist integration** - Automatically adds winning videos to a YouTube playlist

Inspiration: [movieboys.us](https://movieboys.us/)

## ✨ Key Features

### 🎭 Nicolas Cage Commands
- `/speak` - Random Nic Cage quote with audio (if in voice channel)
- `/vampire` - Specific vampire quote from Vampire's Kiss
- `/face` - Specific face quote
- `/gif` - Random Nicolas Cage GIF
- `/join` / `/qjoin` - Bot joins voice channel (with/without sound effect)
- `/leave` / `/qleave` - Bot leaves voice channel (with/without sound effect)

### 🔗 YouTube Link Tracking
- **Automatic duplicate detection** - Notifies users when they post a previously shared YouTube link
- **Smart scanning** - On startup, performs soft scan to build database without excessive API calls
- **Database persistence** - SQLite database tracks all links with author, timestamp, and deletion status
- **Fast deletion checking** - Periodic checks mark deleted messages to avoid false duplicate warnings
- **Supports multiple URL formats**:
  - Desktop: `youtube.com/watch?v=...`
  - Mobile: `youtu.be/...`
  - Shorts: `youtube.com/shorts/...`

### 🏆 Winner System
- `/winner` - Manually calculate best video of the week
- **Automatic weekly calculation** - Runs every Monday at 2:00 PM UTC
- **Reaction-based voting** - Counts all reactions on video posts
- **YouTube playlist integration** - Automatically adds winners to a YouTube playlist (optional)
- **Multi-winner support** - Handles ties gracefully

### 🤖 AI Features
- `/ask_openai` - Ask ChatGPT questions (as Nicolas Cage)
- `/create_openai` - Generate images with DALL-E
- `/ask_gemini` - Ask Google Gemini questions (as Nicolas Cage)
- `/create_gemini` - Generate images with Google Imagen

### 🍪 Cookie Tracking
- `/cookie` - Log cookies eaten
- `/mycookies` - Check your total cookie count
- `/leaderboard` - See who's eaten the most cookies

### 🔧 Admin Commands
- `/kill` - Shut down the bot (admin only)
- `/test_youtube` - Test YouTube playlist integration

## 📋 Prerequisites

- **Python 3.8+**
- **Discord Bot** with proper intents enabled
- **FFmpeg** (for audio playback)
- **Optional**: OpenAI API key
- **Optional**: Google Gemini API key
- **Optional**: YouTube Data API credentials

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kabalzo/NicCageBot.git
cd NicCageBot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 4. Set Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a New Application
3. Navigate to the **Bot** tab
4. Click **Add Bot**
5. Enable these **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Copy your bot token

### 5. Invite Bot to Server

Generate an invite URL with these permissions:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=3165184&scope=bot%20applications.commands
```

**Required Permissions:**
- Read Messages/View Channels
- Send Messages
- Read Message History
- Add Reactions
- Connect (voice)
- Speak (voice)
- Use Slash Commands

## ⚙️ Configuration

### 1. Create Configuration Files

Create a `.env` file in the root directory:

```bash
# Discord
DISCORD_TOKEN=your_discord_bot_token_here

# Admin User ID (your Discord user ID)
ADMIN_USER=your_discord_user_id

# AI Services (optional)
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# YouTube API (optional - for video titles and playlist features)
YOUTUBE_API_KEY=your_youtube_api_key
```

**Getting your API keys:**
- **Discord Token:** [Discord Developer Portal](https://discord.com/developers/applications) → Your App → Bot → Token
- **Admin User ID:** Enable Developer Mode in Discord → Right-click your username → Copy ID
- **OpenAI API Key:** [OpenAI Platform](https://platform.openai.com/api-keys)
- **Gemini API Key:** [Google AI Studio](https://makersuite.google.com/app/apikey)
- **YouTube API Key:** [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials

### 2. Configure config.yaml

The `config/config.yaml` file controls all bot behavior. Here's the structure with explanations:

```yaml
bot:
  token: "${DISCORD_TOKEN}"              # Bot token from .env
  prefix: "!"                            # Command prefix (legacy, not used with slash commands)
  admin_user_id: "${ADMIN_USER}"        # Your Discord user ID from .env
  mode: "test"                          # Default mode: "prod" or "test"
  auto_winner: true                     # Enable automatic weekly winner calculation
  deletion_check_interval: 3600         # Check for deleted messages every hour (in seconds)

winner:
  schedule: "monday-14:00"              # When to announce winners (day-HH:MM in UTC)
  add_to_playlist: true                 # Automatically add winners to YouTube playlist

channels:
  prod:
    monitor: 123456789012345678         # Production channel to monitor for links
    send: 123456789012345678            # Production channel for notifications
  test:
    monitor: 987654321098765432         # Test channel to monitor
    send: 987654321098765432            # Test channel for notifications

playlists:
  prod: "PLxxxxxxxxxxxxxxxxxxxxxx"      # Production YouTube playlist ID
  test: "PLyyyyyyyyyyyyyyyyyyyyyy"      # Test YouTube playlist ID

apis:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-3.5-turbo"              # ChatGPT model to use
    image_model: "dall-e-3"             # DALL-E model for images
  gemini:
    api_key: "${GEMINI_API_KEY}"
    model: "gemini-2.0-flash"           # Gemini model to use
    image_model: "imagen-3.0-generate-002"  # Imagen model for images
  youtube:
    api_key: "${YOUTUBE_API_KEY}"

youtube:
  scopes: ["https://www.googleapis.com/auth/youtube.force-ssl"]
  service_name: "youtube"
  version: "v3"

constants:
  date_format: "%a, %b %d %Y"           # Format for displaying dates
  empty_winner_gif: "https://tenor.com/view/100-gif-27642217"  # GIF when no votes
  winner_alert_hours: 4                 # Hours before winner announcement to alert

gifs:
  - "https://tenor.com/view/nicholas-cage-you-pointing-smoke-gif-14538102"
  - "https://tenor.com/view/nicolas-cage-the-rock-smile-windy-handsome-gif-15812740"
  - "https://tenor.com/view/woo-nick-cage-nicolas-cage-the-unbearable-weight-of-massive-talent-lets-go-gif-25135470"
  - "https://tenor.com/view/national-treasure-benjamin-gates-nicolas-cage-declaration-of-independence-steal-gif-4752081"
```

**Getting Channel IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click any channel → Copy ID
3. Paste the ID into config.yaml

**Getting YouTube Playlist ID:**
1. Go to your YouTube playlist
2. Look at the URL: `https://www.youtube.com/playlist?list=PLxxxxxx`
3. Copy the part after `list=` (starts with `PL`)
4. Paste into config.yaml

### 3. Add Quotes and Audio

Create `data/quotes.txt` with this format:
```
Quote text here; audio_file.mp3
I could eat a peach for hours; peach.mp3
NOT THE BEES!; bees.mp3
```

Place corresponding audio files in `sounds/` directory.

### 4. YouTube OAuth (Optional)

For YouTube playlist integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to root directory
6. First run will prompt for authentication

## 🎮 Running the Bot

### Production Mode
```bash
python3 main.py --mode prod
```

### Test Mode
```bash
python3 main.py --mode test
```

### Without Mode Argument (uses config.yaml default)
```bash
python3 main.py
```

## 🖥️ Running on Ubuntu Server with Screen

The bot is designed to run persistently on Ubuntu Server using `screen` sessions.

### Initial Setup on Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install screen if not already installed
sudo apt install screen -y

# Clone and setup the bot
git clone https://github.com/kabalzo/NicCageBot.git
cd NicCageBot
pip3 install -r requirements.txt
```

### Running in Screen

Create a persistent screen session:

```bash
# Start a new screen session named 'nicbot'
screen -S nicbot

# Inside the screen session, run the bot
python3 main.py --mode prod

# Detach from screen (bot keeps running)
# Press: Ctrl+A, then D
```

### Managing the Screen Session

```bash
# List all screen sessions
screen -ls

# Reattach to the nicbot screen
screen -r nicbot

# Kill the screen session (stops the bot)
screen -X -S nicbot quit

# Or reattach and use Ctrl+C to stop, then exit
screen -r nicbot
# Ctrl+C to stop bot
# Type 'exit' or Ctrl+D to close screen
```

### Auto-Start Script

Create `start_bot.sh` for easy launching:

```bash
#!/bin/bash
cd /path/to/NicCageBot
screen -dmS nicbot python3 main.py --mode prod
echo "NicCageBot started in screen session 'nicbot'"
echo "Use 'screen -r nicbot' to attach"
```

Make it executable:
```bash
chmod +x start_bot.sh
./start_bot.sh
```

### Systemd Service (Alternative to Screen)

For automatic restarts and boot-on-startup, create `/etc/systemd/system/nicbot.service`:

```ini
[Unit]
Description=Nicolas Cage Discord Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/NicCageBot
ExecStart=/usr/bin/python3 /path/to/NicCageBot/main.py --mode prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nicbot.service
sudo systemctl start nicbot.service

# Check status
sudo systemctl status nicbot.service

# View logs
sudo journalctl -u nicbot.service -f
```

### Viewing Bot Logs

When running in screen:
```bash
# Reattach to see live output
screen -r nicbot
```

When running as systemd service:
```bash
# Follow logs in real-time
sudo journalctl -u nicbot.service -f

# View recent logs
sudo journalctl -u nicbot.service -n 100
```

### Monitoring Bot Health

Create a simple health check script `check_bot.sh`:

```bash
#!/bin/bash
if screen -list | grep -q "nicbot"; then
    echo "✅ Bot is running"
else
    echo "❌ Bot is not running"
    echo "Starting bot..."
    cd /path/to/NicCageBot
    screen -dmS nicbot python3 main.py --mode prod
fi
```

Add to crontab for automatic monitoring:
```bash
crontab -e
# Add this line to check every 5 minutes:
*/5 * * * * /path/to/check_bot.sh
```

## 📊 Database Structure

The bot uses SQLite databases (separate for prod/test):

### Link Tracking Database
- `link_tracker_prod.db` / `link_tracker_test.db`
- Tracks YouTube videos with author, timestamp, deletion status
- Indexes for fast lookups

### Cookie Database
- `cookie_info_prod.db` / `cookie_info_test.db`
- Tracks cookie consumption per user

## 🛠️ Customization Guide

### Adding New Quotes

Edit `data/quotes.txt`:
```
Your new quote here; your_audio.mp3
```

Add `your_audio.mp3` to `sounds/` directory.

### Adding New GIFs

Edit `config/config.yaml`:
```yaml
gifs:
  - "https://your.gif.url/here.gif"
  - "https://another.gif.url/here.gif"
```

### Creating Custom Commands

Add to `bot/commands.py`:

```python
@app_commands.command(name="mycommand", description="My custom command")
async def mycommand(self, interaction: discord.Interaction):
    await interaction.response.send_message("Custom response!")
```

### Modifying Winner Schedule

Edit `config/config.yaml`:

```yaml
winner:
  schedule: "friday-18:00"  # Change to Friday at 6:00 PM UTC
  # schedule: "monday-08:00"  # Monday at 8:00 AM UTC (2:00 AM CST)
  add_to_playlist: true
```

**Time Zone Notes:**
- All times in config are UTC
- To convert from your local time zone:
  - CST (UTC-6): Add 6 hours to your desired time
  - EST (UTC-5): Add 5 hours to your desired time
  - PST (UTC-8): Add 8 hours to your desired time
- Example: For 2:00 PM CST, use `20:00` (14:00 + 6 hours)

**Schedule Format:** `day-HH:MM`
- Days: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`
- Time: 24-hour format (00:00 - 23:59)

### Adding New Link Patterns

Edit `data/file_handlers.py`:

```python
class LinkPatterns:
    CUSTOM_PAT = r"your_regex_pattern_here"
    PATTERNS = [DEFAULT_PAT_1, DEFAULT_PAT_2, ..., CUSTOM_PAT]
```

### Customizing AI Personalities

Edit `services/ai_service.py`:

```python
# For OpenAI (line ~16)
async def ask_question(self, prompt):
    full_prompt = "You are Nicolas Cage the famous actor. Keep responses somewhat succinct, but still with flair. " + prompt
    # Change to:
    # full_prompt = "You are a helpful assistant who speaks like Nicolas Cage. " + prompt

# For Gemini (line ~50)
async def ask_question(self, prompt):
    full_prompt = "You are Nicolas Cage the famous actor. Keep responses somewhat succinct, but still with flair. " + prompt
    # Change to your custom personality
```

### Adjusting Deletion Check Frequency

Edit `config/config.yaml`:

```yaml
bot:
  deletion_check_interval: 3600  # seconds (default: 1 hour)
  # deletion_check_interval: 1800  # 30 minutes
  # deletion_check_interval: 7200  # 2 hours
```

This controls how often the bot checks for deleted messages in the monitored channel.

### Environment-Specific Behavior

The bot supports `prod` and `test` modes with separate:
- Channel configurations
- Databases
- YouTube playlists

Switch modes with `--mode` flag or in `config.yaml`.

## 🔍 How It Works

### Startup Process
1. Load configuration from `config.yaml` and `.env`
2. Initialize Discord bot with required intents
3. Connect to SQLite databases (mode-specific)
4. Build message cache from recent Discord history
5. Perform soft scan: scan backwards until finding tracked messages
6. Check for deleted messages (marks them in database)
7. Start periodic deletion checks (hourly)
8. Start winner calculation service (if enabled)
9. Begin listening for new messages and commands

### Link Duplicate Detection Flow
1. User posts YouTube link in monitored channel
2. Bot extracts video ID using regex patterns
3. Queries database for existing entry
4. If found (and not deleted), notifies poster with original author and date
5. If new, adds to database with message metadata
6. Continues monitoring in real-time

### Soft Scan Optimization
Instead of scanning entire channel history on every startup:
- Scans backwards from newest messages
- Stops when reaching previously tracked message
- Only processes new messages since last run
- Dramatically reduces startup time for active channels

### Winner Calculation Process
1. Scans monitored channel backwards until finding previous "Winner:" announcement
2. Counts all reactions on each video link
3. Determines video(s) with most reactions
4. Fetches video titles using YouTube API (or web scraping fallback)
5. Optionally adds winners to YouTube playlist
6. Posts announcement in channel with winner details

## 🐛 Troubleshooting

### Bot Won't Start on Ubuntu Server
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check if all dependencies installed
pip3 list

# Check for errors
python3 main.py --mode test
```

### FFmpeg Issues
```bash
# Verify FFmpeg installed
ffmpeg -version

# If missing, install
sudo apt install ffmpeg -y
```

### Screen Session Issues
```bash
# List all screen sessions
screen -ls

# Kill zombie screens
screen -wipe

# Force detach if stuck
screen -d nicbot
```

### Database Locked Errors
```bash
# Stop all bot instances
screen -X -S nicbot quit

# Check for lingering processes
ps aux | grep python3

# Kill if necessary
kill -9 <PID>

# Restart bot
screen -dmS nicbot python3 main.py --mode prod
```

### YouTube Authentication Fails
```bash
# Remove old token
rm token.pickle

# Restart bot and follow OAuth flow
python3 main.py --mode prod
```

### Permission Denied Errors
```bash
# Make sure user owns the directory
sudo chown -R $USER:$USER /path/to/NicCageBot

# Fix permissions
chmod -R 755 /path/to/NicCageBot
chmod 600 .env  # Keep credentials secure
```

### Bot Not Responding to Commands
- Verify bot has proper Discord permissions
- Check Message Content Intent is enabled
- Ensure bot is online in Discord
- Reattach to screen to see error logs: `screen -r nicbot`

## 📁 Project Structure

```
NicCageBot/
├── bot/
│   ├── __init__.py
│   ├── bot.py              # Main bot class and setup
│   ├── commands.py         # All slash commands
│   ├── events.py           # Event listeners (messages, reactions)
│   └── utils.py            # Utility functions (scanning, checking)
├── config/
│   ├── config.yaml         # Main configuration file
│   └── config.py           # Config loader class
├── data/
│   ├── __init__.py
│   ├── database.py         # SQLite database handlers
│   ├── file_handlers.py    # Quote manager, regex patterns
│   ├── quotes.txt          # Nic Cage quotes list
│   ├── cookie_info_*.db    # Cookie tracking databases
│   └── link_tracker_*.db   # YouTube link databases
├── services/
│   ├── __init__.py
│   ├── ai_service.py       # OpenAI and Gemini integrations
│   ├── winner_service.py   # Weekly winner calculation
│   └── youtube_service.py  # YouTube API integration
├── sounds/
│   └── *.mp3               # Audio clips for quotes
├── .env                    # Environment variables (not committed)
├── .gitignore             # Git ignore rules
├── credentials.json        # YouTube OAuth credentials (not committed)
├── token.pickle           # YouTube OAuth token (not committed)
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔒 Security Best Practices

### On Ubuntu Server

1. **Protect sensitive files:**
```bash
chmod 600 .env
chmod 600 credentials.json
chmod 600 token.pickle
```

2. **Use environment variables:**
Never commit API keys or tokens to Git

3. **Run as non-root user:**
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash nicbot
sudo su - nicbot
```

4. **Firewall configuration:**
```bash
# Only if bot needs to expose ports (usually not needed)
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable
```

5. **Keep dependencies updated:**
```bash
pip3 install --upgrade -r requirements.txt
```

## 🔄 Updating the Bot

```bash
# Reattach to screen
screen -r nicbot

# Stop bot with Ctrl+C
# Detach with Ctrl+A, D

# Pull latest changes
git pull origin main

# Install any new dependencies
pip3 install -r requirements.txt

# Restart bot
screen -dmS nicbot python3 main.py --mode prod
```

## 💡 Tips and Tricks

### Multiple Bot Instances
Run prod and test simultaneously:
```bash
screen -dmS nicbot-prod python3 main.py --mode prod
screen -dmS nicbot-test python3 main.py --mode test
```

### Debug Mode
Add verbose logging:
```python
# In bot/bot.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Backup Databases
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp data/*.db backups/backup_$DATE/
```

### Quick Restart Alias
Add to `~/.bashrc`:
```bash
alias restart-nicbot='screen -X -S nicbot quit && screen -dmS nicbot python3 /path/to/NicCageBot/main.py --mode prod'
```

## 📞 Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/kabalzo/NicCageBot/issues)
- **Project Website:** [movieboys.us](https://movieboys.us/)

## 📜 License

Check the repository for license information.

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by movie watching sessions with friends
- Nicolas Cage for being Nicolas Cage

---

**"I'm a vampire! I'm a vampire! I'm a vampire!"** - Nicolas Cage, Vampire's Kiss

⭐ **If you enjoy this bot, please leave a star on [GitHub](https://github.com/kabalzo/NicCageBot)!**