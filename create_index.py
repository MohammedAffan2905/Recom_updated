import asyncio
from elasticsearch import AsyncElasticsearch

ES_INDEX = "venue_feedback"

async def create_index():
    """Define mappings and settings for optimized search performance."""
    es = AsyncElasticsearch(["http://localhost:9200"])

    settings = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        "mappings": {
            "properties": {
                "user_id": {"type": "integer"},
                "location": {"type": "text", "analyzer": "standard"},
                "sport": {"type": "text", "analyzer": "standard"},
                "venue_name": {"type": "text", "analyzer": "standard"},
                "rating": {"type": "float"},
                "review": {"type": "text", "analyzer": "standard"}
            }
        }
    }

    try:
        exists = await es.indices.exists(index=ES_INDEX)
        if not exists:
            await es.indices.create(index=ES_INDEX, body=settings)
            print(f"✅ Index '{ES_INDEX}' created successfully!")
    finally:
        await es.close()  # 🔴 Ensure proper closure of Elasticsearch client

async def main():
    await create_index()

if __name__ == "__main__":
    asyncio.run(main())
