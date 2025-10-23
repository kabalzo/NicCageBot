import sqlite3
import datetime
import os
from datetime import timezone

class CookieDatabase:
    def __init__(self, db_path=None, mode="prod"):
        if db_path is None:
            # Use mode-specific database file
            db_path = f"data/cookie_info_{mode}.db"
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cookies(
                id INTEGER PRIMARY KEY, 
                user_id INTEGER, 
                num_cookies INTEGER, 
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_cookies(self, user_id, num_cookies):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        current_date = str(datetime.datetime.now())
        cursor.execute(
            "INSERT INTO cookies (user_id, num_cookies, date) VALUES (?, ?, ?)",
            (user_id, num_cookies, current_date)
        )
        
        cursor.execute(
            "SELECT SUM(num_cookies) FROM cookies WHERE user_id = ?", 
            (user_id,)
        )
        total_cookies = cursor.fetchone()[0] or 0
        
        conn.commit()
        conn.close()
        return total_cookies
    
    def get_leaderboard(self, guild):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, SUM(num_cookies) AS total_cookies
            FROM cookies
            GROUP BY user_id
            ORDER BY total_cookies DESC
        """)
        leaderboard = cursor.fetchall()
        conn.close()
        
        return leaderboard

class LinkDatabase:
    def __init__(self, db_path=None, mode="prod"):
        if db_path is None:
            # Use mode-specific database file
            db_path = f"data/link_tracker_{mode}.db"
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_links(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                author_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                discord_created_at TIMESTAMP NOT NULL,  -- Store Discord message timestamp
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When record was added to DB
                deleted BOOLEAN DEFAULT FALSE,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_id ON youtube_links(video_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_id ON youtube_links(message_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON youtube_links(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_deleted ON youtube_links(channel_id, deleted)")
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def add_or_update_link(self, video_id, author_id, author_name, message_id, channel_id, discord_created_at):
        """Add new link or update existing one if it was previously deleted"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO youtube_links 
                (video_id, author_id, author_name, message_id, channel_id, discord_created_at, deleted, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, FALSE, CURRENT_TIMESTAMP)
                ON CONFLICT(video_id) DO UPDATE SET
                message_id = excluded.message_id,
                author_id = excluded.author_id,
                author_name = excluded.author_name,
                channel_id = excluded.channel_id,
                discord_created_at = excluded.discord_created_at,
                deleted = FALSE,
                last_seen = CURRENT_TIMESTAMP
            """, (video_id, author_id, author_name, message_id, channel_id, discord_created_at))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error in add_or_update_link: {e}")
            return False
        finally:
            conn.close()
    
    def get_link_info(self, video_id):
        """Get information about a video link"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT video_id, author_id, author_name, message_id, channel_id, discord_created_at, deleted
            FROM youtube_links 
            WHERE video_id = ? AND deleted = FALSE
        """, (video_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'video_id': result[0],
                'author_id': result[1],
                'author_name': result[2],
                'message_id': result[3],
                'channel_id': result[4],
                'discord_created_at': result[5],  # This is the actual Discord message timestamp
                'deleted': result[6]
            }
        return None
    
    def mark_link_deleted(self, message_id):
        """Mark a link as deleted"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE youtube_links 
            SET deleted = TRUE 
            WHERE message_id = ?
        """, (message_id,))
        
        conn.commit()
        conn.close()
    
    def get_latest_tracked_message(self, channel_id):
        """Get the most recent message ID we've tracked for a channel"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message_id 
            FROM youtube_links 
            WHERE channel_id = ? AND deleted = FALSE 
            ORDER BY message_id DESC 
            LIMIT 1
        """, (channel_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def is_video_posted(self, video_id):
        """Check if a video has been posted before (and not deleted)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM youtube_links 
            WHERE video_id = ? AND deleted = FALSE
        """, (video_id,))
        
        result = cursor.fetchone() is not None
        conn.close()
        return result