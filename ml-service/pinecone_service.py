# pinecone_service.py
from pinecone import Pinecone, ServerlessSpec
from .config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_CLOUD, PINECONE_REGION

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
                cloud=PINECONE_CLOUD,
                region=PINECONE_REGION,
            ),
        )
        
    return pc.Index(PINECONE_INDEX_NAME)

def upsert_embedding(index, vector_id: str, embedding: list, metadata: dict = None):
    """
    Upserts an embedding into the Pinecone index with metadata.

    Expected vector schema:
      - id: string (vector_id)
      - values: float[1024]
      - metadata: JSON (userId, storyId, chunkIndex, language, createdAt)
    """
    if not vector_id or not embedding:
        raise ValueError("Vector ID and embedding are required.")

    try:
        vector = {
            "id": vector_id,
            "values": embedding,
            "metadata": metadata or {},
        }
        index.upsert(vectors=[vector])
        print(f"Successfully upserted vector: {vector_id}")
    except Exception as e:
        print(f"An error occurred during upsert: {e}")

def delete_user_vectors(index, user_id: str):
    """
    Deletes any existing vectors in the index for the given userId (via metadata filter).
    Useful to enforce a single-story-per-user policy.
    """
    if not user_id:
        raise ValueError("user_id is required to delete existing vectors.")
    try:
        index.delete(filter={"userId": user_id})
        print(f"Deleted existing vectors for userId: {user_id}")
    except Exception as e:
        print(f"An error occurred during delete: {e}")
    
def find_similar_stories(index, embedding: list, top_k: int = 400):
    """
    Finds stories with similar embeddings.
    """
    if not embedding:
        raise ValueError("Embedding is required to find similar stories.")
        
    try:
        return index.query(vector=embedding, top_k=top_k, include_metadata=True)
    except Exception as e:
        print(f"An error occurred during query: {e}")
        return None
    