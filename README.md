# 🎬 NicCageBot

A feature-rich Discord bot that combines Nicolas Cage movie quotes, AI interactions, YouTube video tracking, and automated movie night polling.

<div style="display: flex; gap: 10px; align-items: center;">
  <img src="https://github.com/user-attachments/assets/7d64bff8-f3e9-4c04-b724-4708b6c2a9d1" width="400" height="120" alt="image" />
  <img src="https://github.com/user-attachments/assets/3e9f4894-1136-4271-aa17-283a07b364d0" width="281" height="215" alt="image" />
  <img src="https://github.com/user-attachments/assets/cd20327c-b770-42b6-adf7-b8bc131a3da4" width="318" height="215" alt="image" />
</div>

## ✨ Features

### 🎭 Nicolas Cage Commands
- `/speak` - Random Nic Cage quote with audio (if in voice channel)
- `/vampire` / `/face` - Specific quotes
- `/gif` - Random Nicolas Cage GIF
- `/join` / `/leave` - Voice channel controls (with optional sound effects using `/qjoin` / `/qleave`)

### 🔗 YouTube Link Tracking
- **Duplicate detection** - Notifies users when posting previously shared videos
- **Smart scanning** - Efficient startup with soft scan (only processes new messages)
- **Database persistence** - SQLite tracks all links with metadata
- **Auto-cleanup** - Periodic checks mark deleted messages

### 🏆 Winner System
- `/winner` - Manually calculate best video of the week
- **Automatic weekly winners** - Scheduled announcement based on reaction counts
- **YouTube playlist integration** - Auto-adds winners to playlist (optional, requires OAuth)
- **Multi-winner support** - Handles ties gracefully

### 🎬 Movie Night Polls
- **Automated scheduling** - Weekly polls for movie night availability
- **Role-based notifications** - Pings designated role when poll opens
- **Multi-day selection** - Voters can pick multiple available days

### 🤖 AI Features
- `/ask_openai` - ChatGPT as Nicolas Cage
- `/create_openai` - DALL-E image generation
- `/ask_gemini` - Google Gemini as Nicolas Cage
- `/create_gemini` - Imagen image generation

### 🍪 Cookie Tracking
- `/cookie` - Log cookies eaten
- `/mycookies` - Check your total
- `/leaderboard` - Top cookie consumers

## 📋 Prerequisites

- **Python 3.8+**
- **FFmpeg** (for audio playback)
- **Discord Bot** with Message Content Intent enabled
- **Optional**: OpenAI API key, Gemini API key, YouTube API key/OAuth

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/kabalzo/NicCageBot.git
cd NicCageBot
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 3. Discord Bot Setup

1. Create bot at [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
3. Copy bot token
4. Invite with permissions: `Read Messages`, `Send Messages`, `Read History`, `Add Reactions`, `Connect`, `Speak`, `Use Slash Commands`

### 4. Configuration

Create `.env` file:

```bash
# Required
DISCORD_TOKEN=your_discord_bot_token
ADMIN_USER=your_discord_user_id

# Optional - AI Services
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Optional - YouTube
YOUTUBE_API_KEY=your_youtube_api_key
```

Create `config/config.yaml`:

```yaml
bot:
  token: "${DISCORD_TOKEN}"
  prefix: "!"
  admin_user_id: "${ADMIN_USER}"
  mode: "prod"  # or "test"
  auto_winner: true
  deletion_check_interval: 3600  # seconds

winner:
  schedule: "monday-14:00"  # day-HH:MM (UTC)
  add_to_playlist: true

movie_poll:
  schedule: "wednesday-18:00"  # day-HH:MM (UTC)
  window: 24  # hours poll stays open
  prod:
    movie_boys_role: 123456789012345678  # Discord role ID
  test:
    movie_boys_role: 987654321098765432

channels:
  prod:
    monitor: 123456789012345678  # Channel to watch for videos
    send: 123456789012345678     # Channel for notifications
    poll: 123456789012345678     # Channel for movie polls
  test:
    monitor: 987654321098765432
    send: 987654321098765432
    poll: 987654321098765432

playlists:
  prod: "PLxxxxxxxxxxxxxxxxxxxxxx"
  test: "PLyyyyyyyyyyyyyyyyyyyyyy"

apis:
  openai:
    api_key: "${OPENAI_API_KEY}"
  gemini:
    api_key: "${GEMINI_API_KEY}"
  youtube:
    api_key: "${YOUTUBE_API_KEY}"

youtube:
  scopes: ["https://www.googleapis.com/auth/youtube.force-ssl"]
  service_name: "youtube"
  version: "v3"

constants:
  date_format: "%a, %b %d %Y"
  empty_winner_gif: "https://tenor.com/view/100-gif-27642217"
  winner_alert_hours: 4

gifs:
  - "https://tenor.com/view/nicholas-cage-you-pointing-smoke-gif-14538102"
  - "https://tenor.com/view/nicolas-cage-the-rock-smile-windy-handsome-gif-15812740"
```

**Getting IDs:**
- **Channel IDs**: Enable Developer Mode in Discord → Right-click channel → Copy ID
- **Role IDs**: Right-click role → Copy ID
- **User ID**: Right-click your username → Copy ID
- **Playlist ID**: From YouTube URL `?list=PLxxxxxx` (copy the `PL...` part)

### 5. Add Quotes

Create `data/quotes.txt`:
```
I could eat a peach for hours; peach.mp3
NOT THE BEES!; bees.mp3
```

Place corresponding MP3 files in `sounds/` directory.

### 6. YouTube OAuth (Optional)

For playlist integration:
1. Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Download `credentials.json` to project root
4. First run will prompt for authentication
5. `token.pickle` will be created and auto-refreshed

## 🎮 Running the Bot

```bash
# Production mode
python3 main.py --mode prod

# Test mode
python3 main.py --mode test

# Use config.yaml default
python3 main.py
```

## 🖥️ Deployment on Ubuntu Server

### Using Screen (Simple)

```bash
# Start bot in detached screen
screen -dmS nicbot python3 main.py --mode prod

# Reattach to view logs
screen -r nicbot

# Detach: Ctrl+A, then D
# Kill session
screen -X -S nicbot quit
```

### Using Systemd (Production)

Create `/etc/systemd/system/nicbot.service`:

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
sudo systemctl enable nicbot
sudo systemctl start nicbot

# View logs
sudo journalctl -u nicbot -f
```

## 📊 Database Structure

SQLite databases (mode-specific):
- `link_tracker_{mode}.db` - YouTube video tracking
- `cookie_info_{mode}.db` - Cookie consumption data

## 🔧 Customization

### Adding Quotes
Edit `data/quotes.txt` and add audio to `sounds/`.

### Adding GIFs
Edit `gifs` list in `config/config.yaml`.

### Custom Commands
Add to `bot/commands.py`:

```python
@app_commands.command(name="mycommand", description="Description")
async def mycommand(self, interaction: discord.Interaction):
    await interaction.response.send_message("Response!")
```

### Schedule Changes
Edit `config/config.yaml`:

```yaml
winner:
  schedule: "friday-18:00"  # Friday 6 PM UTC
movie_poll:
  schedule: "wednesday-12:00"  # Wednesday noon UTC
```

**Note:** All times are UTC. Convert from your timezone:
- CST (UTC-6): Add 6 hours
- EST (UTC-5): Add 5 hours
- PST (UTC-8): Add 8 hours

### AI Personality
Edit `services/ai_service.py` (lines 18, 74):

```python
full_prompt = "You are Nicolas Cage the famous actor..."
# Change to your custom personality
```

## 🔍 How It Works

### Startup Process
1. Load config from `config.yaml` and `.env`
2. Connect to Discord and initialize services
3. Soft scan: Build message cache, scan backwards until finding tracked messages
4. Start periodic deletion checks
5. Start winner and poll services (if enabled)

### Link Detection
1. User posts YouTube link
2. Extract video ID via regex
3. Check database for duplicates
4. Notify if found, otherwise add to database

### Winner Calculation
1. Scan backwards until previous "Winner:" announcement
2. Count reactions on each video
3. Fetch titles via YouTube API (or web scraping fallback)
4. Add to playlist if OAuth authenticated
5. Post announcement

### Movie Poll
1. Schedule triggers at configured day/time
2. Create multi-answer poll with duration
3. Notify configured role
4. Poll auto-closes after window expires

## 🐛 Common Issues

**Bot won't start:**
```bash
# Check Python version (needs 3.8+)
python3 --version

# Verify dependencies
pip3 install -r requirements.txt

# Check config
cat config/config.yaml
```

**No audio playback:**
```bash
ffmpeg -version
sudo apt install ffmpeg  # if missing
```

**YouTube auth issues:**
```bash
# Remove old token and re-authenticate
rm token.pickle
python3 main.py --mode prod
```

**Database locked:**
```bash
# Stop all bot instances
screen -X -S nicbot quit
# Or: sudo systemctl stop nicbot

# Check for lingering processes
ps aux | grep python3
```

## 📁 Project Structure

```
NicCageBot/
├── bot/
│   ├── bot.py              # Main bot class
│   ├── commands.py         # Slash commands
│   ├── events.py           # Event handlers
│   └── utils.py            # Utilities
├── config/
│   ├── config.yaml         # Configuration (not committed)
│   └── config.py           # Config loader
├── data/
│   ├── database.py         # Database handlers
│   ├── file_handlers.py    # Quote/pattern managers
│   └── quotes.txt          # Nic Cage quotes
├── services/
│   ├── ai_service.py       # OpenAI & Gemini
│   ├── winner_service.py   # Winner calculation
│   ├── poll_service.py     # Movie polls
│   └── youtube_service.py  # YouTube API
├── sounds/                 # Audio clips
├── .env                    # Environment vars (not committed)
├── credentials.json        # YouTube OAuth (not committed)
├── main.py                 # Entry point
└── requirements.txt        # Dependencies
```

## 🔒 Security

```bash
# Protect sensitive files
chmod 600 .env credentials.json token.pickle

# Never commit secrets
# (already in .gitignore)

# Run as non-root user (recommended)
sudo useradd -m -s /bin/bash nicbot
sudo su - nicbot
```

## 🔄 Updating

```bash
# Stop bot
screen -r nicbot  # Ctrl+C, then Ctrl+A D
# Or: sudo systemctl stop nicbot

# Update code
git pull origin main
pip3 install -r requirements.txt

# Restart
screen -dmS nicbot python3 main.py --mode prod
# Or: sudo systemctl start nicbot
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kabalzo/NicCageBot/issues)
- **Inspiration**: [movieboys.us](https://movieboys.us/)

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by movie watching sessions with friends
- Nicolas Cage for being Nicolas Cage

---

**"I'm a vampire! I'm a vampire! I'm a vampire!"** - Nicolas Cage, Vampire's Kiss

⭐ **Star on [GitHub](https://github.com/kabalzo/NicCageBot) if you enjoy this bot!**
