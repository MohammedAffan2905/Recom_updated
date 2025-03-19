from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from elasticsearch import AsyncElasticsearch

app = FastAPI()
es = AsyncElasticsearch(["http://localhost:9200"])
ES_INDEX = "venue_feedback"

# Pydantic model for input validation
class Feedback(BaseModel):
    user_id: int
    location: str
    sport: str
    venue_name: str
    rating: float
    review: str

@app.post("/feedback")
async def post_feedback(feedback: Feedback):
    doc = feedback.dict()
    doc["timestamp"] = datetime.utcnow().isoformat()

    # Insert feedback into Elasticsearch
    res = await es.index(index=ES_INDEX, document=doc)
    return {"message": "Feedback stored successfully!", "id": res["_id"]}

@app.get("/")
async def home():
    return {"message": "Welcome to the Sports Venue Feedback API!"}
