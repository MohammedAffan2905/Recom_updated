from sentence_transformers import SentenceTransformer

# Load model once globally
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(user_id, location, sport, venue_name, rating, review):
    context_text = f"User {user_id} played {sport} at {venue_name} in {location} and rated it {rating} stars. Review: {review}"
    return embedding_model.encode(context_text, normalize_embeddings=True).tolist()
