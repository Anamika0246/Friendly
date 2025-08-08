# ml-service

A small Python service that turns a user’s story into a vector embedding and stores it in Pinecone for similarity matching.

It enforces “one story per user”: whenever a new story arrives for a user, any previous vectors from that user are deleted and replaced.

## What it does
- Reads a single JSON payload from stdin.
- Generates a 1024‑dim embedding using Together API (BGE large v1.5 via OpenAI-compatible SDK).
- Ensures the Pinecone index exists (name: `Friendly-App`, cosine, dim 1024).
- Deletes any existing vectors for that `user_id` (single-story-per-user policy).
- Upserts a vector with:
  - id: `user:<user_id>` (or `user:<user_id>:chunk:<n>` if you later send chunks)
  - values: the 1024‑dim embedding
  - metadata: `{ userId, storyId, chunkIndex?, language?, createdAt? }`
- Prints a JSON result to stdout.

## Input it expects (stdin JSON)
Required
- `user_id` (string)
- `story_id` (string)
- `story_text` (string)

Optional
- `chunk_index` (integer, 0-based; only if you split long stories)
- `language` (string, e.g., "en")
- `created_at` (ISO 8601 or epoch)

Example
```json
{
  "user_id": "u_123",
  "story_id": "s_456",
  "story_text": "I moved to a new city and...",
  "language": "en",
  "created_at": "2025-08-08T10:00:00Z"
}
```

## Output it returns (stdout JSON)
Success
```json
{
  "status": "success",
  "user_id": "u_123",
  "story_id": "s_456",
  "vector_id": "user:u_123"
}
```

Error
```json
{
  "status": "error",
  "message": "<description>"
}
```

## Environment variables (.env)
Create a `.env` at the repo root (same level as `ml-service/`):

```
TOGETHER_API_KEY=<your_together_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
PINECONE_INDEX_NAME=Friendly-App
```

Notes
- Don’t commit real secrets. Rotate keys if they were ever exposed.
- `PINECONE_INDEX_NAME` defaults to `Friendly-App` if not set.

## How to run
Install dependencies (example):
```
pip install openai>=1.0.0 pinecone>=3.0.0 python-dotenv
```

Run the service with `.env` loaded (no shell-specific exports):
```
python -m dotenv -f .env run -- python -m ml-service.process_story
```
Then paste one JSON payload (single line) and end input (Ctrl+Z then Enter on Windows).

## Pinecone index
- Name: `Friendly-App`
- Dimension: `1024` (BAAI/bge-large-en-v1.5)
- Metric: `cosine`
- The service creates it on first use (serverless defaults in code).

## Single-story-per-user policy
- Before upsert, the service runs a Pinecone `delete` with filter `{ "userId": <user_id> }` to remove any prior vectors from that user.
- New vector id is `user:<user_id>` (and optional chunk suffix if you later adopt chunking).

## Where things live
- Embedding generation: `ml-service/embedding_generator.py`
- Pinecone operations: `ml-service/pinecone_service.py`
- Entry point (stdin → embed → upsert → stdout): `ml-service/process_story.py`
- Config (reads env): `ml-service/config.py`

## Troubleshooting
- "Invalid JSON input": ensure valid single-line JSON on stdin.
- "Failed to generate embedding": check `TOGETHER_API_KEY` and model availability.
- "An error occurred during upsert": verify `PINECONE_API_KEY`, index name/region, and that dimension=1024.
- Import errors: run as a module from the repo root: `python -m ml-service.process_story`.
