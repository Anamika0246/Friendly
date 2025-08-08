# process_story.py
import sys
import json
from .embedding_generator import generate_embedding
from .pinecone_service import init_pinecone, upsert_embedding

def main():
    """
    Main function to process a story, generate its embedding,
    and upsert it to Pinecone.
    Expects a JSON string from stdin with "story_id" and "story_text".
    """
    # Read from stdin
    input_data = sys.stdin.read()
    try:
        data = json.loads(input_data)
        story_id = data.get("story_id")
        story_text = data.get("story_text")

        if not story_id or not story_text:
            raise ValueError("Missing 'story_id' or 'story_text' in input JSON.")

        # 1. Generate embedding
        embedding = generate_embedding(story_text)
        if embedding is None:
            raise Exception("Failed to generate embedding.")

        # 2. Initialize Pinecone and upsert
        pinecone_index = init_pinecone()
        upsert_embedding(pinecone_index, story_id, embedding)

        print(json.dumps({"status": "success", "story_id": story_id}))

    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON input."}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
