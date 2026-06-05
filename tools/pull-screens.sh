#!/usr/bin/env bash
# Copy the iOS 26 screenshot-test baselines this site needs into docs/assets/raw/
# under stable, slug-friendly names. Makes the articles repo reproducible: rerun
# after regenerating baselines in the mobile worktree.
#
# Usage: tools/pull-screens.sh [path-to-docusketch-mobile-worktree]
set -uo pipefail

MOBILE="${1:-$HOME/Developer/docusketch-mobile-help-screens}"
SRC="$MOBILE/KMP/Screenshots/ios26"
DST="$(cd "$(dirname "$0")/.." && pwd)/docs/assets/raw"
mkdir -p "$DST"

missing=0
copy() { # copy "<module>/<baseline>.png" "<dest>.png"
  if [[ -f "$SRC/$1" ]]; then
    cp "$SRC/$1" "$DST/$2"; echo "  ok   $2"
  else
    echo "  MISS $1" >&2; missing=1
  fi
}

echo "Pulling baselines from $SRC"
copy "presentation-features-camera/CameraSelectionScreenshotTests - Camera selection Insta360.png" "camera-selection-insta360.png"
copy "presentation-features-camera/CameraScreenshotTests - Camera connected Insta360.png"          "camera-connected-insta360.png"
copy "presentation-features-project/ProjectActionsScreenshotTests - Project actions uploaded.png"   "project-actions-uploaded.png"
copy "presentation-features-project/CreateOrEditProjectScreenshotTests - Create timeline empty.png" "create-timeline-empty.png"
copy "presentation-features-timeline/TimelineRoomListScreenshotTests - Timeline room list populated.png" "timeline-room-list.png"
copy "presentation-features-sketch/InteriorSketchRequestScreenshotTests - InteriorSketchRequest form.png" "sketch-request-form.png"

if [[ $missing -ne 0 ]]; then
  echo "Some baselines are missing — regenerate them in the mobile worktree, then rerun." >&2
  exit 1
fi
echo "Done -> $DST"
