#!/bin/bash
# Final pass: loudness to -14 LUFS, h264 delivery encode, render gate + contact sheet.
#   ./finalize.sh [render.mp4] [OutputName]
set -euo pipefail
cd "$(dirname "$0")"
src=${1:-edit/renders/meli.mp4}; name=${2:-Meli_InglesDesdeCero}
mkdir -p output work
ffmpeg -v error -y -i "$src" -c:v libx264 -preset slow -crf 17 -maxrate 12M -bufsize 20M -r 30 -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "output/$name.mp4"
node ../.claude/skills/video-editing/scripts/verify-render.mjs "output/$name.mp4"
ffmpeg -v error -y -i "output/$name.mp4" -vf "fps=1/2,scale=216:-1,tile=6x3" -frames:v 1 "work/${name}_sheet.png"
