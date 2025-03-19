# from fastapi import FastAPI, Depends, Query, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.sql import text
# from database import get_db
# from models import VenueFeedback
# from pydantic import BaseModel
# from utils.embeddings import generate_embedding  # Import embedding function

# import numpy as np

# app = FastAPI()

# # Pydantic Model for Input
# class FeedbackInput(BaseModel):
#     user_id: int
#     location: str
#     sport: str
#     venue_name: str
#     rating: float
#     review: str

# # Route to Store Feedback
# @app.post("/feedback")
# async def store_feedback(feedback: FeedbackInput, db: AsyncSession = Depends(get_db)):
#     # Generate embedding automatically
#     embedding = generate_embedding(feedback.user_id, feedback.location, feedback.sport, feedback.venue_name, feedback.rating, feedback.review)

#     feedback_entry = VenueFeedback(
#         user_id=feedback.user_id,
#         location=feedback.location,
#         sport=feedback.sport,
#         venue_name=feedback.venue_name,
#         rating=feedback.rating,
#         review=feedback.review,
#         embedding=embedding  # Store as pgvector
#     )
#     db.add(feedback_entry)
#     await db.commit()
#     return {"message": "Feedback stored successfully"}

# # Route to Get Recommendations (Vector Search)
# @app.get("/recommendations")
# async def get_recommendations(user_id: int = Query(..., description="User ID to fetch recommendations"),
#                               db: AsyncSession = Depends(get_db)):
#     # Step 1: Get all feedback of the user
#     query = select(VenueFeedback).where(VenueFeedback.user_id == user_id)
#     result = await db.execute(query)
#     user_feedbacks = result.scalars().all()

#     if not user_feedbacks:
#         raise HTTPException(status_code=404, detail="No feedback found for this user")

#     # Step 2: Filter positive feedbacks (e.g., rating >= 4)
#     positive_feedbacks = [feedback for feedback in user_feedbacks if feedback.rating >= 4]

#     if not positive_feedbacks:
#         raise HTTPException(status_code=404, detail="No positive feedback found for this user")

#     # Step 3: Extract embeddings from positive feedbacks
#     positive_embeddings = np.array([feedback.embedding for feedback in positive_feedbacks])

#     # Step 4: Calculate the average embedding of positive feedbacks
#     avg_embedding = np.mean(positive_embeddings, axis=0)

#     # Step 5: Perform vector search to find similar venues
#     query = select(VenueFeedback).order_by(VenueFeedback.embedding.l2_distance(avg_embedding)).limit(5)
#     result = await db.execute(query)
#     recommendations = result.scalars().all()

#     # Step 6: Return recommended venue names
#     return {"recommendations": [rec.venue_name for rec in recommendations]}


# # Route to Get All Feedbacks
# @app.get("/feedbacks")
# async def get_all_feedback(db: AsyncSession = Depends(get_db)):
#     query = select(VenueFeedback)
#     result = await db.execute(query)
#     feedbacks = result.scalars().all()
    
#     return [
#         {
#             "feedback_id": feedback.id,
#             "user_id": feedback.user_id,
#             "location": feedback.location,
#             "sport": feedback.sport,
#             "venue_name": feedback.venue_name,
#             "rating": feedback.rating,
#             "review": feedback.review
#         }
#         for feedback in feedbacks
#     ]


# @app.delete("/feedback/{feedback_id}")
# async def delete_feedback(feedback_id: int, db: AsyncSession = Depends(get_db)):
#     # Fetch the specific feedback record
#     query = select(VenueFeedback).where(VenueFeedback.id == feedback_id)
#     result = await db.execute(query)
#     feedback = result.scalar_one_or_none()

#     # If the feedback is not found, return a 404 error
#     if feedback is None:
#         raise HTTPException(status_code=404, detail="Feedback not found")

#     # Delete only the specific feedback entry
#     await db.delete(feedback)
#     await db.commit()

#     return {"message": f"Feedback with ID {feedback_id} deleted successfully"}

from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy.future import select
from database import get_db
from models import VenueFeedback
from utils.embeddings import generate_embedding
from elasticsearch import AsyncElasticsearch
import numpy as np
import redis.asyncio as redis
import json
import asyncio

app = FastAPI()

# Initialize Redis client
REDIS_URL = "redis://localhost:6379"
redis = redis.from_url(REDIS_URL, decode_responses=True)

# Stream Name
REDIS_STREAM = "feedback_stream"






# Pydantic Model for Input
class FeedbackInput(BaseModel):
    user_id: int
    location: str
    sport: str
    venue_name: str
    rating: float
    review: str


# Route to Store Feedback (with Redis Streaming)
@app.post("/feedback")
async def store_feedback(feedback: FeedbackInput, db: AsyncSession = Depends(get_db)):
    # Generate embedding
    embedding = generate_embedding(feedback.user_id, feedback.location, feedback.sport, feedback.venue_name, feedback.rating, feedback.review)

    # Store in PostgreSQL
    feedback_entry = VenueFeedback(
        user_id=feedback.user_id,
        location=feedback.location,
        sport=feedback.sport,
        venue_name=feedback.venue_name,
        rating=feedback.rating,
        review=feedback.review,
        embedding=embedding  # Store as pgvector
    )
    db.add(feedback_entry)
    await db.commit()

    # Publish feedback to Redis Stream
    feedback_data = {
        "user_id": feedback.user_id,
        "location": feedback.location,
        "sport": feedback.sport,
        "venue_name": feedback.venue_name,
        "rating": feedback.rating,
        "review": feedback.review,
        "embedding": json.dumps(embedding)  # Store embedding as JSON string
    }
    await redis.xadd(REDIS_STREAM, feedback_data)

    return {"message": "Feedback stored successfully and sent to Redis stream"}


# Route to Get Recommendations (with Redis Cache)
@app.get("/recommendations")
async def get_recommendations(user_id: int = Query(..., description="User ID to fetch recommendations"),
                              db: AsyncSession = Depends(get_db)):

    redis_key = f"recommendations:{user_id}"
    cached_recommendations = await redis.get(redis_key)

    if cached_recommendations:
        return {"recommendations": json.loads(cached_recommendations)}

    # Fetch user feedback from PostgreSQL
    query = select(VenueFeedback).where(VenueFeedback.user_id == user_id)
    result = await db.execute(query)
    user_feedbacks = result.scalars().all()

    if not user_feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found for this user")

    positive_feedbacks = [feedback for feedback in user_feedbacks if feedback.rating >= 4]

    if not positive_feedbacks:
        raise HTTPException(status_code=404, detail="No positive feedback found for this user")

    positive_embeddings = np.array([feedback.embedding for feedback in positive_feedbacks])
    avg_embedding = np.mean(positive_embeddings, axis=0)

    query = select(VenueFeedback).order_by(VenueFeedback.embedding.l2_distance(avg_embedding)).limit(5)
    result = await db.execute(query)
    recommendations = result.scalars().all()

    recommendations_list = [rec.venue_name for rec in recommendations]

    # Cache recommendations in Redis for faster access
    await redis.set(redis_key, json.dumps(recommendations_list), ex=3600)  # Cache for 1 hour

    return {"recommendations": recommendations_list}



# Initialize Elasticsearch client
ES_HOST = "http://localhost:9200"
es = AsyncElasticsearch([ES_HOST])

# Elasticsearch Index Name
ES_INDEX = "venue_feedback"

@app.get("/search_venue")
async def search_venue(query: str):
    """Perform fuzzy search on venue names using Elasticsearch"""
    response = await es.search(
        index=ES_INDEX,
        body={
            "query": {
                "fuzzy": {
                    "venue_name": {
                        "value": query,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
    )

from fastapi import FastAPI, Query
from elasticsearch import AsyncElasticsearch

app = FastAPI()
es = AsyncElasticsearch(["http://localhost:9200"])
ES_INDEX = "venue_feedback"

@app.get("/search")
async def search_venues(query: str = Query(..., description="Search venues")):
    """Perform fast venue search with Elasticsearch."""
    response = await es.search(
        index=ES_INDEX,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["venue_name^3", "location^2", "sport", "review"],
                    "fuzziness": "AUTO"
                }
            }
        }
    )
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    return {"results": results}


    results = [hit["_source"] for hit in response["hits"]["hits"]]
    return {"results": results}



# Background Task to Process Redis Stream
async def consume_feedback_stream():
    while True:
        messages = await redis.xread({REDIS_STREAM: "$"}, count=10, block=5000)

        for _, entries in messages:
            for entry in entries:
                feedback_data = entry[1]
                print("Processing Feedback:", feedback_data)

        await asyncio.sleep(2)  # Prevents high CPU usage

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_feedback_stream())  # Correct method for background tasks


