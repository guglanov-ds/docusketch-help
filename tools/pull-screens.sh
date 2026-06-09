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

# --- how-to-add-a-timeline (full 7-step reproduction) ---
copy "presentation-features-project/ProjectListScreenshotTests - Project list populated.png"        "project-list.png"
copy "presentation-features-project/ProjectListScreenshotTests - Project list with timelines.png"   "project-list-timelines.png"
copy "presentation-features-project/ProjectActionsScreenshotTests - Project actions local only.png" "project-actions-local.png"
copy "presentation-features-camera/Camera360ShotsScreenshotTests - Camera 360 shots connected time shift.png" "shoot-360.png"
copy "presentation-features-viewer360/Viewer360ScreenshotTests - Viewer360 bottom content collapsed.png" "viewer-360.png"
copy "presentation-features-room/RoomListScreenshotTests - Room list populated.png"                 "room-list.png"
copy "presentation-features-project/UploadProjectScreenshotTests - Upload project not started.png"  "upload-progress.png"
copy "presentation-features-timeline/TimelineRoomActionsScreenshotTests - Timeline room actions default.png" "timeline-room-actions.png"
copy "presentation-features-project/UploadAlertScreenshotTests - Upload timeline parent required alert.png" "upload-alert.png"
copy "presentation-features-viewer360/Viewer360ScreenshotTests - Viewer360 image.png"                "viewer-360-close.png"
copy "presentation-features-timeline/TimelineRoomListScreenshotTests - Timeline room list all captured.png" "timeline-room-all-captured.png"

# --- notification-alert-that-the-camera-storage-is-full (tut3) ---
# INSTA360 renders as "DocuSketch° DS1", so the generic storage-low shot is the DS1 frame.
copy "presentation-features-camera/CameraScreenshotTests - Camera connected storage low.png"            "camera-ds1-storage-low.png"
copy "presentation-features-camera/CameraScreenshotTests - Camera connected Ricoh storage low.png"      "camera-ricoh-storage-low.png"
copy "presentation-features-camera/CameraScreenshotTests - Camera connected Mi storage low.png"         "camera-mi-storage-low.png"
copy "presentation-features-camera/CameraStorageFullAlertScreenshotTests - Camera storage full alert.png" "camera-storage-full-alert.png"

# --- how-to-reshoot-360-images-in-a-project (tut4) --- (project-list/room-list already pulled)
copy "presentation-features-project/ProjectOverviewScreenshotTests - Project overview populated.png" "project-overview.png"
copy "presentation-features-room/RoomDetailScreenshotTests - Room detail with panorama.png"          "room-detail-reshoot.png"

# --- update-project-information (tut12) + simultaneous (tut11) ---
copy "presentation-features-project/CreateOrEditProjectScreenshotTests - Edit project populated.png" "edit-project.png"
copy "presentation-features-project/ProjectOverviewScreenshotTests - Project overview no rooms.png"  "project-overview-empty.png"

if [[ $missing -ne 0 ]]; then
  echo "Some baselines are missing — regenerate them in the mobile worktree, then rerun." >&2
  exit 1
fi
echo "Done -> $DST"
