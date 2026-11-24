#!/usr/bin/env bash
# Scaffold a new video project folder.
# Usage: tools/new_project.sh <slug> [short|medium]
#   tools/new_project.sh ai-video-editor-build medium
set -euo pipefail
slug="${1:?usage: tools/new_project.sh <slug> [short|medium]}"
kind="${2:-short}"
root="$(cd "$(dirname "$0")/.." && pwd)"
dir="$root/projects/$(date +%Y-%m-%d)-$slug"
mkdir -p "$dir"/{raw,assets,edit,exports,thumbnails}
if [ ! -f "$dir/brief.md" ]; then
cat > "$dir/brief.md" <<EOF
# $slug

- **Format:** $kind
- **Pillar:** (AI builds | photography | videography | fitness | content creation)
- **Platforms:** (YouTube | YouTube Shorts | Instagram Reels | TikTok | LinkedIn)
- **Core idea (1 sentence):**
- **Hook (first 2 seconds):**
- **Payoff / takeaway:**
- **CTA:**
- **Must-keep moments / notes:**
EOF
fi
echo "$dir"
echo "Drop footage into: $dir/raw/"
