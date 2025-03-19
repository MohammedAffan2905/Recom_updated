# import asyncio
# from elasticsearch import AsyncElasticsearch
# from database import AsyncSessionLocal
# from models import VenueFeedback
# from sqlalchemy.future import select

# es = AsyncElasticsearch(["http://localhost:9200"])
# ES_INDEX = "venue_feedback"

# async def index_data():
#     """Fetch PostgreSQL data and index it into Elasticsearch"""
#     async with AsyncSessionLocal() as session:
#         query = select(VenueFeedback)
#         result = await session.execute(query)
#         feedbacks = result.scalars().all()

#         for feedback in feedbacks:
#             doc = {
#                 "user_id": feedback.user_id,
#                 "location": feedback.location,
#                 "sport": feedback.sport,
#                 "venue_name": feedback.venue_name,
#                 "rating": feedback.rating,
#                 "review": feedback.review
#             }
#             await es.index(index=ES_INDEX, document=doc)

#     print("Data indexed successfully!")

# asyncio.run(index_data())

import asyncio
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(["http://localhost:9200"])
ES_INDEX = "venue_feedback"

async def index_feedback():
    feedback_data = [
        {"user_id": 1, "location": "New York", "sport": "Basketball", "venue_name": "Madison Square Garden", "rating": 4.8, "review": "Amazing experience!"},
        {"user_id": 2, "location": "Los Angeles", "sport": "Soccer", "venue_name": "Banc of California Stadium", "rating": 4.5, "review": "Great atmosphere."},
        {"user_id": 3, "location": "Chicago", "sport": "Tennis", "venue_name": "Chicago Tennis Club", "rating": 4.2, "review": "Nice courts but expensive."}
    ]

    for feedback in feedback_data:
        await es.index(index=ES_INDEX, document=feedback)

    print("Sample feedback indexed successfully!")

async def main():
    await index_feedback()

if __name__ == "__main__":
    asyncio.run(main())
