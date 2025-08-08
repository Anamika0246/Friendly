# config.py
import os

# It's recommended to use environment variables for security (no hardcoded defaults)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Allow overriding index name via env; default to 'friendly-app' (lowercase per Pinecone rules)
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "friendly-app")

# Pinecone Serverless location (make configurable to avoid plan/region restrictions)
# Defaults target a commonly available free-tier region; override in .env if needed
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "gcp")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-central1")
