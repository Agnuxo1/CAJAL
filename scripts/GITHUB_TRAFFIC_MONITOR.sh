#!/bin/bash
# GITHUB_TRAFFIC_MONITOR.sh — Track repo traffic and stars
# Run manually or via cron
# Requires: GITHUB_TOKEN env variable

TOKEN="${GITHUB_TOKEN:-YOUR_TOKEN_HERE}"
REPOS=(
  "Agnuxo1/CAJAL"
  "Agnuxo1/OpenCLAW-P2P"
  "Agnuxo1/p2pclaw-unified"
  "Agnuxo1/EnigmAgent"
  "Agnuxo1/benchclaw"
)

LOG="/tmp/github_traffic.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== GitHub Traffic — $DATE ===" >> "$LOG"

for repo in "${REPOS[@]}"; do
  # Get star count
  STARS=$(curl -s "https://api.github.com/repos/$repo" \
    -H "Authorization: Bearer $TOKEN" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('stargazers_count',0))")
  
  # Get traffic (requires push access)
  VIEWS=$(curl -s "https://api.github.com/repos/$repo/traffic/views" \
    -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count',0) if 'count' in d else 'N/A')" 2>/dev/null || echo "N/A")
  
  echo "$repo | ⭐ $STARS | 👁️ $VIEWS" >> "$LOG"
done

echo "---" >> "$LOG"
cat "$LOG" | tail -20
