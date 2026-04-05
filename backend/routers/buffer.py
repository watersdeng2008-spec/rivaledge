"""
Buffer router — social media automation endpoints.

Allows scheduling, viewing, and managing social media posts via Buffer.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user
import services.buffer as buffer_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/channels")
def get_buffer_channels(current_user: dict = Depends(get_current_user)):
    """
    Get all connected Buffer channels (Twitter, LinkedIn, etc.)
    """
    try:
        channels = buffer_service.get_channels()
        return {"channels": channels}
    except Exception as e:
        logger.error(f"Failed to get Buffer channels: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channels: {str(e)}",
        )


@router.get("/posts")
def get_scheduled_posts(
    channel_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get scheduled posts from Buffer.
    
    Optionally filter by channel_id.
    """
    try:
        posts = buffer_service.get_scheduled_posts(channel_id)
        return {"posts": posts}
    except Exception as e:
        logger.error(f"Failed to get scheduled posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get posts: {str(e)}",
        )


@router.post("/schedule")
def schedule_post(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Schedule a post to Buffer.
    
    Body:
    {
        "channel_id": "buffer-channel-id",
        "text": "Post content",
        "due_at": "2026-04-05T13:00:00Z" (ISO format, UTC)
    }
    """
    channel_id = body.get("channel_id")
    text = body.get("text")
    due_at_str = body.get("due_at")
    
    if not channel_id or not text or not due_at_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="channel_id, text, and due_at are required",
        )
    
    try:
        due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid due_at format. Use ISO 8601 UTC format.",
        )
    
    try:
        post = buffer_service.schedule_post(channel_id, text, due_at)
        return {"success": True, "post": post}
    except Exception as e:
        logger.error(f"Failed to schedule post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule: {str(e)}",
        )


@router.post("/schedule-thread")
def schedule_thread(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Schedule a Twitter thread (multiple posts spaced 20 minutes apart).
    
    Body:
    {
        "channel_id": "twitter-channel-id",
        "tweets": ["Tweet 1", "Tweet 2", "Tweet 3"],
        "start_at": "2026-04-05T13:00:00Z" (optional, defaults to tomorrow 13:00 UTC)
    }
    """
    channel_id = body.get("channel_id")
    tweets = body.get("tweets", [])
    start_at_str = body.get("start_at")
    
    if not channel_id or not tweets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="channel_id and tweets are required",
        )
    
    # Parse start time or default to tomorrow 13:00 UTC
    if start_at_str:
        start_at = datetime.fromisoformat(start_at_str.replace("Z", "+00:00"))
    else:
        start_at = datetime.now(timezone.utc) + timedelta(days=1)
        start_at = start_at.replace(hour=13, minute=0, second=0, microsecond=0)
    
    scheduled = []
    errors = []
    
    for i, tweet in enumerate(tweets):
        due_at = start_at + timedelta(minutes=20 * i)
        
        try:
            post = buffer_service.schedule_post(channel_id, tweet, due_at)
            scheduled.append(post)
        except Exception as e:
            logger.error(f"Failed to schedule tweet {i+1}: {e}")
            errors.append({"index": i, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "scheduled": scheduled,
        "errors": errors,
        "count": len(scheduled),
    }


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a scheduled post."""
    try:
        success = buffer_service.delete_post(post_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to delete post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete: {str(e)}",
        )
