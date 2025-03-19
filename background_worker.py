# import asyncio
# import json
# from redis_client import get_feedback_from_stream
# from database import AsyncSessionLocal
# from models import VenueFeedback

# async def process_feedback():
#     while True:
#         feedbacks = get_feedback_from_stream()
        
#         if feedbacks:
#             async with AsyncSessionLocal() as session:
#                 for stream, entries in feedbacks:
#                     for entry in entries:
#                         feedback_data = entry[1]
                        
#                         feedback_entry = VenueFeedback(
#                             user_id=int(feedback_data["user_id"]),
#                             location=feedback_data["location"],
#                             sport=feedback_data["sport"],
#                             venue_name=feedback_data["venue_name"],
#                             rating=float(feedback_data["rating"]),
#                             review=feedback_data["review"]
#                         )
                        
#                         session.add(feedback_entry)
                
#                 await session.commit()
        
#         await asyncio.sleep(300)  # Run every 5 minutes

# # Run in a separate background thread
# asyncio.run(process_feedback())




# --------------------------------------------

# import asyncio
# import json
# from redis_client import get_feedback_from_stream
# from database import AsyncSessionLocal
# from models import VenueFeedback

# async def process_feedback():
#     while True:
#         feedbacks = await get_feedback_from_stream()  # Now correctly awaits async function

#         if feedbacks:
#             async with AsyncSessionLocal() as session:
#                 for stream, entries in feedbacks:
#                     for entry in entries:
#                         feedback_data = entry[1]
                        
#                         feedback_entry = VenueFeedback(
#                             user_id=int(feedback_data["user_id"]),
#                             location=feedback_data["location"],
#                             sport=feedback_data["sport"],
#                             venue_name=feedback_data["venue_name"],
#                             rating=float(feedback_data["rating"]),
#                             review=feedback_data["review"]
#                         )
                        
#                         session.add(feedback_entry)

#                 await session.commit()

#         await asyncio.sleep(5)  # Poll every 5 seconds (reduced from 5 min)

# if __name__ == "__main__":
#     asyncio.run(process_feedback())  # Proper async entry point

from elasticsearch import AsyncElasticsearch
import asyncio

es = AsyncElasticsearch("http://localhost:9200")

async def index_feedback_in_es(feedback):
    doc = {
        "user_id": feedback.user_id,
        "location": feedback.location,
        "sport": feedback.sport,
        "venue_name": feedback.venue_name,
        "rating": feedback.rating,
        "review": feedback.review
    }
    await es.index(index="venues", body=doc)
