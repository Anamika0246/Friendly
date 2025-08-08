# pinecone_service.py
from pinecone import Pinecone, ServerlessSpec
from .config import PINECONE_API_KEY, PINECONE_INDEX_NAME

def init_pinecone():
    """
    Initializes Pinecone and returns the index object.
    Creates the index if it doesn't exist.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        # Adjust dimension based on the embedding model
        pc.create_index(
            name=PINECONE_INDEX_NAME, 
            dimension=1024, 
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-west-2'
            ) 
        )
        
    return pc.Index(PINECONE_INDEX_NAME)

def upsert_embedding(index, story_id: str, embedding: list):
    """
    Upserts a story embedding into the Pinecone index.
    """
    if not story_id or not embedding:
        raise ValueError("Story ID and embedding are required.")
        
    try:
        index.upsert(vectors=[(story_id, embedding)])
        print(f"Successfully upserted embedding for story ID: {story_id}")
    except Exception as e:
        print(f"An error occurred during upsert: {e}")
    
def find_similar_stories(index, embedding: list, top_k: int = 5):
    """
    Finds stories with similar embeddings.
    """
    if not embedding:
        raise ValueError("Embedding is required to find similar stories.")
        
    try:
        return index.query(vector=embedding, top_k=top_k, include_metadata=False)
    except Exception as e:
        print(f"An error occurred during query: {e}")
        return None
    