# Error Logs (Friendly)

Simple explanations of common errors, why they happen, and how to fix them.

---

## 1) Pinecone: INVALID_ARGUMENT — Index name format
- Symptom
  - HTTP 400 with message like: "Name must consist of lower case alphanumeric characters or '-'".
- Why it happens
  - Pinecone index names must be lowercase letters, numbers, or hyphens only. No uppercase, underscores, or spaces.
- Fix
  - Use a compliant name. We now use: `friendly-app`.
  - Set it in `.env`: `PINECONE_INDEX_NAME=friendly-app`.

---

## 2) Pinecone: INVALID_ARGUMENT — Region not supported by plan
- Symptom
  - HTTP 400 with message like:
    - "Your free plan does not support indexes in the us-west-2 region of aws."
    - or "...does not support indexes in the us-central1 region of gcp."
- Why it happens
  - Each Pinecone plan allows only some serverless regions. If you try to create an index in a region your plan doesn't support, Pinecone rejects it.
- Fix
  - Pick an allowed serverless location for your plan. Common free-tier option: `aws / us-east-1`.
  - Set in `.env` (repo root):
    - `PINECONE_CLOUD=aws`
    - `PINECONE_REGION=us-east-1`
  - Re-run the test. If you still see the old region in the error:
    - Ensure `.env` is loaded (our Node test shows a dotenv message when it loads).
    - Confirm `process.env.PINECONE_REGION` and `PINECONE_CLOUD` at runtime.
    - Make sure you're running from the repo root (our driver sets `cwd` accordingly).

---

## 3) Pinecone: top_k exceeds limit
- Symptom
  - HTTP 400: "top_k exceeds limit" (or similar).
- Why it happens
  - Your plan enforces a maximum `top_k` (max number of results per query).
- Fix
  - Lower `top_k` (e.g., 100–1,000), or segment queries by metadata (language/region) and merge results.
  - Consider upgrading the plan for larger `top_k`.

---

## 4) Missing environment variables / Unauthorized
- Symptom
  - Our Node driver prints: "Missing environment variables: ..."; or API calls fail with 401/403.
- Why it happens
  - Required keys are not in `.env`, or are invalid/expired.
- Fix
  - Set these in `.env` at the repo root:
    - `TOGETHER_API_KEY=<your_key>`
    - `PINECONE_API_KEY=<your_key>`
    - `PINECONE_INDEX_NAME=friendly-app`
    - `PINECONE_CLOUD=aws` and `PINECONE_REGION=us-east-1` (or your allowed region)
  - Re-run the driver. Do not commit real keys.

---

## 5) Python import error: relative import without package
- Symptom
  - "attempted relative import with no known parent package" if you run the script directly.
- Why it happens
  - `ml-service` uses relative imports. Running the file directly bypasses package context.
- Fix
  - Run as a module from the repo root: `python -m ml-service.process_story`.
  - Our Node driver already does this correctly.

---

## 6) Embedding generation errors (Together API)
- Symptom
  - "Failed to generate embedding" or SDK/network error.
- Why it happens
  - Bad/expired API key, network issue, rate limits, or the story is too long for the model.
- Fix
  - Verify `TOGETHER_API_KEY`. Add retry/backoff if needed.
  - Truncate or chunk very long stories.

---

## 7) Pinecone upsert payload invalid
- Symptom
  - HTTP 400 complaining about vectors format.
- Why it happens
  - Payload must be a list of dicts with `id`, `values`, and optional `metadata`.
- Fix
  - We upsert with `{ id, values, metadata }` already. If editing, keep that shape.

---

## 8) No matches found
- Symptom
  - Query returns an empty list; not an error.
- Why it happens
  - Empty index or low similarity.
- Fix
  - Ensure data is ingested, relax filters, or lower similarity threshold.

---

## 9) Region changes don't seem to apply
- Symptom
  - Error message still mentions an old region after updating `.env`.
- Why it happens
  - The process isn't reading the updated env, or `.env` path is wrong.
- Fix
  - Our Node driver loads `..\.env` and prints a dotenv banner.
  - Confirm values at runtime (temporary debug): print `process.env.PINECONE_REGION`.
  - Restart the terminal/session if variables are cached elsewhere.

---

## Quick tips
- Keep index names lowercase with hyphens.
- Use an allowed serverless region for your Pinecone plan.
- Validate env is loaded before running tests.
- Expect empty results when the index is empty.

If a new error appears, paste the full message here with the steps you ran so we can add a clear entry and fix.
