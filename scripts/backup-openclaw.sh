#!/usr/bin/env bash
set -euo pipefail

BASE="/home/tomoyuki/.openclaw"
OUTDIR="$BASE/workspace/backups"
TS=$(date +%Y%m%d-%H%M%S)

mkdir -p "$OUTDIR"

WS="$OUTDIR/workspace-${TS}.tar.gz"
HOMEARC="$OUTDIR/openclaw-home-${TS}.tar.gz"

tar -czf "$WS" -C "$BASE" workspace
sha256sum "$WS" > "$WS.sha256"

tar --exclude='.openclaw/workspace/backups/*' -czf "$HOMEARC" -C /home/tomoyuki .openclaw
sha256sum "$HOMEARC" > "$HOMEARC.sha256"

# Keep latest 12 sets (~3 months if weekly)
ls -1t "$OUTDIR"/workspace-*.tar.gz 2>/dev/null | tail -n +13 | xargs -r rm -f
ls -1t "$OUTDIR"/workspace-*.tar.gz.sha256 2>/dev/null | tail -n +13 | xargs -r rm -f
ls -1t "$OUTDIR"/openclaw-home-*.tar.gz 2>/dev/null | tail -n +13 | xargs -r rm -f
ls -1t "$OUTDIR"/openclaw-home-*.tar.gz.sha256 2>/dev/null | tail -n +13 | xargs -r rm -f

echo "Backup complete: $TS"
