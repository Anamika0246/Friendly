# embedding_generator.py
from openai import OpenAI
from .config import TOGETHER_API_KEY

client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)

def generate_embedding(story: str):
    """
    Generates an embedding for a single story using the BGE model.
    """
    if not story:
        raise ValueError("Input story cannot be empty.")

    try:
        response = client.embeddings.create(
            model="BAAI/bge-large-en-v1.5",
            input=[story]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"An error occurred while generating embedding: {e}")
        return None
