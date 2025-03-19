from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class VenueFeedback(Base):
    __tablename__ = "venue_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    sport = Column(String, nullable=False)
    venue_name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(String, nullable=False)
    embedding = Column(Vector(384))  # 384 is the embedding size of MiniLM
