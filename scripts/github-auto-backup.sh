#!/usr/bin/env bash
set -euo pipefail

REPO="/home/tomoyuki/.openclaw/workspace"
LOG_DIR="$REPO/backups"
LOG_FILE="$LOG_DIR/github-auto-backup.log"

mkdir -p "$LOG_DIR"

{
  echo "[$(date '+%F %T')] start github auto backup"
  cd "$REPO"

  # If git repo is unavailable, just log and exit without failing cron loop.
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "not a git repository: $REPO"
    exit 0
  fi

  # Stage all workspace changes
  git add -A

  # Nothing to commit -> done
  if git diff --cached --quiet; then
    echo "no changes"
    exit 0
  fi

  BRANCH="$(git branch --show-current || echo main)"
  TS="$(date '+%F %T %z')"
  git commit -m "chore(backup): auto backup ${TS}" >/dev/null
  git push origin "$BRANCH"
  echo "pushed to origin/${BRANCH}"
} >> "$LOG_FILE" 2>&1
