// Simple driver to test ml-service embedding + Pinecone upsert
// Usage: node server/test-ml-service.js [--user u_123] [--story s_456] [--text "your story..."]

import { spawn } from 'child_process';
import path from 'path';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from repo root
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// Parse CLI args (very minimal)
const args = process.argv.slice(2);
function getArg(flag, defVal) {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : defVal;
}

const userId = getArg('--user', 'u_demo');
const storyId = getArg('--story', 's_demo');
const storyText = getArg('--text', 'I moved to a new city and struggled to make friends but eventually found a great community.');
const language = getArg('--lang', 'en');
const createdAt = new Date().toISOString();

// Basic env validation
const requiredEnv = ['TOGETHER_API_KEY', 'PINECONE_API_KEY'];
const missing = requiredEnv.filter((k) => !process.env[k]);
if (missing.length) {
  console.error('Missing environment variables:', missing.join(', '));
  console.error('Ensure you have a .env at the repo root with these keys set.');
  process.exit(1);
}

// Build the payload expected by ml-service/process_story.py
const payload = {
  user_id: userId,
  story_id: storyId,
  story_text: storyText,
  language,
  created_at: createdAt,
};

console.log('Running ml-service with payload:', JSON.stringify(payload));

// Run Python module: ml-service.process_story
const child = spawn('python', ['-m', 'ml-service.process_story'], {
  cwd: path.join(__dirname, '..'), // repo root
  env: process.env, // pass through env (.env loaded above if dotenv present)
  stdio: ['pipe', 'pipe', 'pipe'],
});

let stdout = '';
let stderr = '';

child.stdout.on('data', (d) => (stdout += d.toString()));
child.stderr.on('data', (d) => (stderr += d.toString()));

child.on('close', (code) => {
  if (stderr.trim()) {
    console.error('\n[ml-service stderr]\n' + stderr);
  }
  console.log('\n[ml-service exit code]', code);
  const out = stdout.trim();
  if (!out) {
    console.error('No output received from ml-service.');
    process.exit(code || 1);
  }
  try {
    const json = JSON.parse(out);
    console.log('\n[ml-service result]\n', JSON.stringify(json, null, 2));
    if (json.status !== 'success') process.exit(1);
    process.exit(0);
  } catch (e) {
    console.log('\n[ml-service raw stdout]\n' + out);
    console.error('Failed to parse JSON output:', e.message);
    process.exit(code || 1);
  }
});

// Write the JSON payload to stdin and end
child.stdin.write(JSON.stringify(payload));
child.stdin.end();
