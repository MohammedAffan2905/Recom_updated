import asyncio
import random
from datetime import datetime
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(["http://localhost:9200"])
ES_INDEX = "venue_feedback"

async def index_feedback():
    feedback_data = [
        {"user_id": random.randint(4, 100), "location": "Miami", "sport": "Basketball", "venue_name": "Heat Arena", "rating": round(random.uniform(3.5, 5.0), 1), "review": "Loved the crowd!", "timestamp": datetime.utcnow().isoformat()},
        {"user_id": random.randint(4, 100), "location": "Dallas", "sport": "Baseball", "venue_name": "Globe Life Field", "rating": round(random.uniform(3.5, 5.0), 1), "review": "Good experience.", "timestamp": datetime.utcnow().isoformat()},
    ]

    for feedback in feedback_data:
        await es.index(index=ES_INDEX, document=feedback)

    print("New feedback indexed!")

async def run_periodically():
    while True:
        await index_feedback()
        await asyncio.sleep(10)  # Insert new feedback every 10 seconds

if __name__ == "__main__":
    asyncio.run(run_periodically())
