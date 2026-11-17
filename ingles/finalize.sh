#!/bin/bash
# Final pass for an "Inglés Reel": take the HyperFrames render, put the master voice+SFX track on it,
# loudness to -14 LUFS, bitrate cap, render gate + contact sheet. No grain (clean talking-head look).
#   ./finalize.sh <reel-dir>
set -euo pipefail
cd "$(dirname "$0")"
dir=${1%/}
name=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['output'])" "$dir/reel.json")
dur=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['duration'])" "$dir/timeline.json")
src=$(ls -t "$dir"/renders/*.mp4 | head -1)
mkdir -p output "$dir/work"
ffmpeg -v error -y -i "$src" -i "$dir/master.wav" -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 19 -maxrate 7M -bufsize 12M -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k \
  -t "$dur" -movflags +faststart "output/$name.mp4"
node ../.claude/skills/video-editing/scripts/verify-render.mjs "output/$name.mp4" --duration "$dur" --tolerance 0.2
ffmpeg -v error -y -i "output/$name.mp4" -vf "fps=1,scale=216:-1,tile=9x5" -frames:v 1 "$dir/work/${name}_sheet.png"
ffmpeg -hide_banner -i "output/$name.mp4" -af ebur128=framelog=quiet -f null - 2>&1 | grep -E "^\s+(I|True peak|Peak):" || true
echo "-> output/$name.mp4"
