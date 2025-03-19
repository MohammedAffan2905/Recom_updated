# import redis
# import json

# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# FEEDBACK_STREAM = "venue_feedback_stream"

# def push_feedback_to_stream(feedback):
#     redis_client.xadd(FEEDBACK_STREAM, feedback)

# def get_feedback_from_stream():
#     feedbacks = redis_client.xread({FEEDBACK_STREAM: "0"}, count=10, block=5000)
#     return feedbacks

# --------------------------------------
# import redis.asyncio as redis
# import json

# REDIS_URL = "redis://localhost:6379" 

# FEEDBACK_STREAM = "venue_feedback_stream"

# # Create Redis connection
# redis = redis.from_url(REDIS_URL, decode_responses=True)

# async def push_feedback_to_stream(feedback):
#     """Push feedback to Redis Stream."""
#     await redis.xadd(FEEDBACK_STREAM, feedback)

# async def get_feedback_from_stream():
#     """Fetch new feedback entries from Redis Stream."""
#     messages = await redis.xread({FEEDBACK_STREAM: "$"}, count=10, block=5000)
#     return messages  # Returns latest unread messages

import redis.asyncio as redis

REDIS_URL = "redis://localhost:6379"
FEEDBACK_STREAM = "venue_feedback_stream"

async def get_redis_connection():
    """Create a Redis connection."""
    return await redis.from_url(REDIS_URL, decode_responses=True)

async def push_feedback_to_stream(feedback):
    """Push feedback to Redis Stream."""
    redis_conn = await get_redis_connection()
    await redis_conn.xadd(FEEDBACK_STREAM, feedback)
    await redis_conn.close()  # Explicitly close connection

async def get_feedback_from_stream():
    """Fetch new feedback entries from Redis Stream."""
    redis_conn = await get_redis_connection()
    messages = await redis_conn.xread({FEEDBACK_STREAM: "$"}, count=10, block=5000)
    await redis_conn.close()
    return messages  # Returns latest unread messages


