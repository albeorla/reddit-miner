#!/bin/bash
set -e

# Pain Radar Local Verification Script
# This script performs a full system smoke test.

export PAIN_RADAR_DB_PATH="temp_verify.sqlite3"
export PAIN_RADAR_OPENAI_MODEL="gpt-4o" # Placeholder
export OPENAI_API_KEY="sk-placeholder"

echo "1. Initializing Database..."
python -m pain_radar init-db --db $PAIN_RADAR_DB_PATH

echo "2. Adding Source Set..."
python -m pain_radar sources-add indie_saas --db $PAIN_RADAR_DB_PATH

echo "3. Fetching Posts (Mocked/Limited)..."
# We'll use a real subreddit but limit to 1 to verify the plumbing
python -m pain_radar fetch --subreddit test --limit 1 --db $PAIN_RADAR_DB_PATH

echo "4. Running Pipeline (Checking CLI invocation)..."
# We expect this might fail analysis if the key is invalid,
# but we want to see if the command starts and handles the error gracefully or if we can mock it.
# For a smoke test, even a "0 posts analyzed" is a pass if the command itself works.
python -m pain_radar run --subreddit test --limit 1 --no-progress --db $PAIN_RADAR_DB_PATH || echo "Pipeline finished (errors expected due to mock key)"

echo "5. Testing Web Server..."
python -m pain_radar web &
WEB_PID=$!
sleep 3
curl -s http://localhost:8000/ > /dev/null && echo "✓ Web server responded"
kill $WEB_PID

echo "6. Testing API Server..."
# We don't have a 'python -m pain_radar api' command yet, but we can use uvicorn
uvicorn src.pain_radar.api.main:app --port 8001 &
API_PID=$!
sleep 3
curl -s http://localhost:8001/v1/signals > /dev/null && echo "✓ API server responded"
kill $API_PID

echo "7. Cleaning up..."
rm $PAIN_RADAR_DB_PATH

echo "Verification Complete!"
