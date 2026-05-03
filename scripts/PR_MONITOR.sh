#!/bin/bash
# PR_MONITOR.sh — Monitor PRs for P2PCLAW ecosystem
# Run: bash PR_MONITOR.sh
# Cron: */30 * * * * bash /path/to/PR_MONITOR.sh

TOKEN="${GITHUB_TOKEN:-YOUR_TOKEN_HERE}"
LOG="/tmp/pr_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== PR Monitor — $DATE ===" >> "$LOG"

# PRs to monitor
PRS=(
  "RooCodeInc:Roo-Code:12258"
  "danny-avila:LibreChat:12918"
)

for pr in "${PRS[@]}"; do
  IFS=':' read -r owner repo number <<< "$pr"
  
  DATA=$(curl -s "https://api.github.com/repos/$owner/$repo/pulls/$number" \
    -H "Authorization: Bearer $TOKEN")
  
  STATE=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state','unknown'))")
  DRAFT=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('draft','unknown'))")
  TITLE=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title','unknown'))")
  
  echo "$owner/$repo#$number | $STATE | draft=$DRAFT | $TITLE" >> "$LOG"
  
  # Alert if closed
  if [ "$STATE" = "closed" ]; then
    echo "⚠️ ALERT: $owner/$repo#$number was CLOSED!" >> "$LOG"
  fi
done

echo "---" >> "$LOG"
