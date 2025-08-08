"""Process a story: generate embedding and upsert to Pinecone.

Reads a JSON object from stdin with fields:
  - story_id (string)
  - story_text (string)
  - user_id (string)
  - chunk_index (int, optional)
  - language (string, optional)
  - created_at (ISO string or epoch, optional)
Prints a single JSON line to stdout.
"""

import sys
import json
from .embedding_generator import generate_embedding
from .pinecone_service import init_pinecone, upsert_embedding, delete_user_vectors


def main():
    input_data = sys.stdin.read()
    try:
        data = json.loads(input_data)
        story_id = data.get("story_id")
        story_text = data.get("story_text")
        user_id = data.get("user_id")
        chunk_index = data.get("chunk_index")
        language = data.get("language")
        created_at = data.get("created_at")

        if not story_id or not story_text:
            raise ValueError("Missing 'story_id' or 'story_text' in input JSON.")
        if not user_id:
            raise ValueError("Missing 'user_id' for single-story-per-user enforcement.")

        # 1) Generate embedding
        embedding = generate_embedding(story_text)
        if embedding is None:
            raise RuntimeError("Failed to generate embedding.")

        # 2) Initialize Pinecone and construct vector id
        pinecone_index = init_pinecone()
        vector_id = (
            f"user:{user_id}"
            if chunk_index is None
            else f"user:{user_id}:chunk:{chunk_index}"
        )

        metadata = {
            k: v
            for k, v in {
                "userId": user_id,
                "storyId": story_id,
                "chunkIndex": chunk_index,
                "language": language,
                "createdAt": created_at,
            }.items()
            if v is not None
        }

        # 3) Enforce one-story-per-user: delete previous, then upsert
        delete_user_vectors(pinecone_index, user_id)
        upsert_embedding(pinecone_index, vector_id, embedding, metadata)

        print(
            json.dumps(
                {
                    "status": "success",
                    "user_id": user_id,
                    "story_id": story_id,
                    "vector_id": vector_id,
                }
            )
        )
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON input."}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))


if __name__ == "__main__":
    main()
