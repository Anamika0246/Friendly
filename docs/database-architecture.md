# Database Architecture (Friendly)

This document explains the data model and how MongoDB (source of truth), Pinecone (vector search), and Cloudflare R2 (media storage) work together. It’s written to be simple and practical so you can build and evolve the system quickly.

## Components at a glance
- MongoDB Atlas (Document DB): users, story, friendships, conversations, messages, snaps, media references.
- Pinecone (Vector DB): stores only embeddings (vectors) for matching stories by meaning.
- Cloudflare R2 (Object Storage): stores media files (images/videos); MongoDB stores just their URLs/keys.
- Node.js Backend: orchestrates everything, exposes APIs, real-time via Socket.io, runs the ml-service.

## High-level rules
- One story per user: when a user updates their story, the previous embedding is replaced in Pinecone.
- Matching is by cosine similarity in Pinecone. You can filter by metadata (language/region/etc.) and then rerank.
- Media files are never stored in MongoDB; only references (URLs/keys) are stored.

---

## MongoDB (source of truth)

### users
- Fields:
  - _id (ObjectId)
  - handle (string, unique)
  - name (string)
  - avatarUrl (string)
  - bio (string)
  - createdAt (date)
  - updatedAt (date)
  - flags: { blocked: bool, verified: bool }
- Indexes:
  - handle unique
  - createdAt

### stories (one per user)
- Purpose: plain-text story and linkage to vector id in Pinecone.
- Fields:
  - _id (ObjectId)
  - userId (ObjectId, ref users)
  - text (string)
  - language (string, e.g., "en")
  - vectorId (string, e.g., "user:<userId>")
  - createdAt (date)
  - updatedAt (date)
- Indexes:
  - userId unique (enforce one-to-one)
  - createdAt

### matches (optional, cached suggestions)
- Purpose: store/reuse suggestion lists rather than querying Pinecone every time.
- Fields:
  - _id (ObjectId)
  - userId (ObjectId)
  - candidateUserId (ObjectId)
  - score (number)  // cosine similarity score from Pinecone
  - source (string) // e.g., "pinecone:query"
  - createdAt (date)
  - status (string) // 'suggested'|'hidden'
- Indexes:
  - userId
  - score desc (optional compound)
  - createdAt

### friendships
- Purpose: who is connected to whom, and in what state.
- Fields:
  - _id (ObjectId)
  - userA (ObjectId)
  - userB (ObjectId)
  - status (string): 'pending'|'accepted'|'blocked'
  - requestedBy (ObjectId)
  - createdAt (date)
  - updatedAt (date)
- Indexes:
  - Unique on pair (min(userA,userB), max(userA,userB))
  - status

### conversations
- Purpose: DM (1:1) and optional group chats.
- Fields:
  - _id (ObjectId)
  - memberIds ([ObjectId])
  - type (string): 'dm'|'group'
  - lastMessageAt (date)
  - createdAt (date)
- Indexes:
  - memberIds (multikey)
  - lastMessageAt desc

### messages
- Purpose: messages in a conversation.
- Fields:
  - _id (ObjectId)
  - conversationId (ObjectId)
  - senderId (ObjectId)
  - type (string): 'text'|'image'|'video'
  - text (string, optional)
  - mediaId (ObjectId, optional, ref mediaAssets)
  - mediaUrl (string, optional)
  - durationSec (number, optional)
  - viewedBy ([ObjectId])
  - deletedFor ([ObjectId])
  - createdAt (date)
- Indexes:
  - (conversationId, createdAt)
  - (senderId, createdAt)

### snaps (optional, ephemeral)
- Purpose: Snapchat-like 24h photos/videos.
- Fields:
  - _id (ObjectId)
  - senderId (ObjectId)
  - recipientIds ([ObjectId])
  - mediaId (ObjectId, ref mediaAssets)
  - mediaUrl (string)
  - durationSec (number)
  - createdAt (date)
  - expiresAt (date)
- Indexes:
  - TTL index on expiresAt (auto delete)
  - (senderId, createdAt)

### mediaAssets
- Purpose: metadata of uploaded files.
- Fields:
  - _id (ObjectId)
  - ownerId (ObjectId)
  - type (string): 'image'|'video'
  - r2Key (string) // R2 object key
  - url (string)   // Signed/public URL if applicable
  - sizeBytes (number)
  - mimeType (string)
  - width (number)
  - height (number)
  - durationSec (number, optional)
  - status (string): 'processing'|'ready'|'blocked'
  - createdAt (date)
- Indexes:
  - (ownerId, createdAt)
  - status

---

## Pinecone (vector search)
- Index name: `Friendly-App`
- Dimension: `1024` (BAAI/bge-large-en-v1.5)
- Metric: `cosine`
- Namespace: optional per environment (e.g., `prod`, `staging`)

Vector schema
- id (string): you provide — we use `user:<userId>`
- values (float[1024]): the embedding
- metadata (object):
  - userId (string)
  - storyId (string)
  - language (string, optional)
  - createdAt (string/number, optional)
  - chunkIndex (number, optional; only if chunking long stories)

Policies
- One vector per user: before upsert, delete existing vectors with filter `{ userId: <userId> }`.
- Query returns best→worst by default. Set `top_k` as needed; Pinecone may cap the max.

---

## Cloudflare R2 (object storage)
- Bucket: e.g., `friendly-media`
- Store raw files (images/videos). MongoDB stores only references.

Key structure (examples)
- `users/<userId>/images/<uuid>.jpg`
- `users/<userId>/videos/<uuid>.mp4`
- `snaps/<senderId>/<uuid>.(jpg|mp4)`

Access
- Use pre-signed URLs for upload (PUT) and limited-time download (GET).
- Optionally front with Cloudflare CDN for speed.

---

## Relationships (simple view)
```
users 1─1 stories
users 1─* friendships (pair: userA<>userB)
users 1─* conversations (via memberIds)
conversations 1─* messages
users 1─* snaps
users 1─* mediaAssets
stories 1─1 vectors (Pinecone) via stories.vectorId (user:<userId>)
```

---

## Core data flows

### 1) Story ingestion
1. Client → Backend: POST story text.
2. Backend writes/updates MongoDB `stories` (text, language, userId).
3. Backend calls `ml-service` with `{ user_id, story_id, story_text, ... }`.
4. ml-service generates embedding → deletes prior vectors for user → upserts vector `{ id: user:<userId>, values, metadata }` to Pinecone.
5. Backend updates `stories.vectorId`.

### 2) Matching
1. Generate (or reuse) the user’s embedding.
2. Pinecone query: set `top_k` (e.g., 1k–10k), `include_metadata=true`, optional filters (language/region).
3. Map vector ids → userIds via metadata; hydrate from MongoDB.
4. Filter (exclude self/friends/blocklist), apply min score, dedupe per user.
5. Optionally cache in `matches` for pagination.

### 3) Friendship & Messaging
- Friendship: create request, accept to connect.
- Conversation: on accept, create/find DM conversation (memberIds=[A,B]).
- Messages: write to `messages`, emit via Socket.io; media goes to R2 then reference saved in MongoDB.

### 4) Snaps (ephemeral)
- Upload media to R2 with pre-signed URL.
- Create `snaps` doc with `expiresAt`.
- TTL index removes after expiry; UI should hide viewed/expired snaps.

---

## Indexing & performance
- MongoDB indexes listed per collection; add as needed for queries.
- Pinecone: choose `top_k` wisely. If you need very large candidate sets, segment (by language/region) and union results, then rerank.
- Cache: store large candidate lists in `matches` and paginate.

---

## Security & privacy
- Never store blobs in MongoDB; only URLs/keys.
- Authorize access: users can only access their own conversations/media.
- Moderate stories/media before broad visibility (queue + status in `mediaAssets`).
- Keep secrets in `.env` (not in code or commits).

---

## Environment variables (examples)
- DATABASE_URL
- JWT_SECRET
- TOGETHER_API_KEY
- PINECONE_API_KEY
- PINECONE_INDEX_NAME=Friendly-App
- R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_ACCOUNT_ID / R2_BUCKET
- OPTIONAL: PINECONE_REGION/CLOUD, CDN base URL

---

## Notes on scale
- Use metadata filters to narrow candidate space (language/region/age).
- Query Pinecone with higher `top_k` (up to plan limits), then rerank.
- Precompute nearest-neighbor lists nightly or on updates; serve from cache.
- Paginate, don’t fetch thousands to the client in one go.

---

## Quick glossary
- Vector: numerical representation of a story.
- top_k: number of nearest neighbors to return.
- Metadata: small JSON you attach to vectors (used for filtering and traceability).

This architecture keeps MongoDB as the source of truth, Pinecone for fast semantic search, and R2 for scalable media—cleanly separated, easy to evolve.
