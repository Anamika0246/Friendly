# config.py
import os

# It's recommended to use environment variables for security (no hardcoded defaults)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Allow overriding index name via env; default to Friendly-App if not set
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "Friendly-App")
