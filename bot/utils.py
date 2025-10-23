import asyncio
import discord
from data.file_handlers import LinkPatterns

async def soft_scan_channel(channel, link_db):
    """Perform soft scan: go backwards until we find already tracked messages"""
    print(f"Starting soft scan for channel {channel.id}...")
    
    latest_tracked_id = link_db.get_latest_tracked_message(channel.id)
    scanned_count = 0
    new_links = 0
    
    async for message in channel.history(limit=None, oldest_first=False):
        # Stop if we reach a message we've already tracked
        if latest_tracked_id and message.id <= latest_tracked_id:
            print(f"Reached already tracked message {latest_tracked_id}, soft scan complete")
            break
        
        if message.content and message.content.startswith("https"):
            video_id = LinkPatterns.extract_video_id(message.content)
            if video_id:
                scanned_count += 1
                
                # Check if this is a new link
                existing = link_db.get_link_info(video_id)
                if not existing:
                    # New link found during scan
                    success = link_db.add_or_update_link(
                        video_id=video_id,
                        author_id=message.author.id,
                        author_name=str(message.author),
                        message_id=message.id,
                        channel_id=channel.id,
                        discord_created_at=message.created_at  # Add this line
                    )
                    if success:
                        new_links += 1
                        print(f"Soft scan found new link: {video_id} from {message.author}")
    
    print(f"Soft scan complete: scanned {scanned_count} messages, found {new_links} new links")
    return new_links

async def check_deleted_messages_fast(channel, link_db, message_cache):
    """Ultra-fast deletion check using message cache"""
    print(f"Fast deletion check for channel {channel.id}...")
    
    # Get all active message IDs from database that might be in our cache range
    conn = link_db._get_connection()
    cursor = conn.cursor()
    
    # Only check messages that are likely to be in our cache (recent messages)
    if message_cache:
        # Get the oldest message ID in cache as a reference point
        oldest_cached = min(message_cache)
        cursor.execute("""
            SELECT message_id, video_id, author_name 
            FROM youtube_links 
            WHERE channel_id = ? AND deleted = FALSE AND message_id >= ?
        """, (channel.id, oldest_cached))
    else:
        # If no cache, check recent messages only (last 5000)
        cursor.execute("""
            SELECT message_id, video_id, author_name 
            FROM youtube_links 
            WHERE channel_id = ? AND deleted = FALSE 
            ORDER BY message_id DESC 
            LIMIT 5000
        """, (channel.id,))
    
    active_messages = cursor.fetchall()
    conn.close()
    
    if not active_messages:
        print("No active messages to check in cache range")
        return 0
    
    print(f"Checking {len(active_messages)} messages against cache...")
    deleted_count = 0
    
    for message_id, video_id, author_name in active_messages:
        if message_id not in message_cache:
            link_db.mark_link_deleted(message_id)
            deleted_count += 1
            print(f"Marked message {message_id} (video: {video_id}) as deleted")
    
    print(f"Fast deletion check complete: marked {deleted_count} messages as deleted")
    return deleted_count

async def check_link_realtime(message, link_db):
    """Check link in real-time when a new message is posted"""
    video_id = LinkPatterns.extract_video_id(message.content)
    if not video_id:
        return None
    
    # Check if this video was posted before and not deleted
    existing = link_db.get_link_info(video_id)
    
    if existing:
        return existing
    else:
        # Add new link to database
        success = link_db.add_or_update_link(
            video_id=video_id,
            author_id=message.author.id,
            author_name=str(message.author),
            message_id=message.id,
            channel_id=message.channel.id,
            discord_created_at=message.created_at  # Add this line
        )
        if success:
            print(f"New link logged to DB: {video_id} from {message.author}")
        return None