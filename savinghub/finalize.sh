#!/bin/bash
# Final pass for a rendered reel: film grain over everything (text included; GRAIN=0 skips it),
# loudness to -14 LUFS, bitrate cap, render gate + contact sheet.
#   ./finalize.sh <edit-dir> <OutputName> [audio-file]   (audio-file replaces the render's audio)
set -euo pipefail
cd "$(dirname "$0")"
dir=$1; name=$2; audio=${3:-}
src=$(ls "$dir"/renders/*.mp4 | tail -1)
mkdir -p output work
amap=(); [ -n "$audio" ] && amap=(-i "$audio" -map 0:v -map 1:a)
grain=${GRAIN:-12}   # GRAIN=0 for the clean Savings Hub look
vf="format=yuv420p"; [ "$grain" != "0" ] && vf="noise=alls=$grain:allf=t+u,$vf"
ffmpeg -v error -y -i "$src" "${amap[@]}" -vf "$vf" \
  -c:v libx264 -preset slow -b:v 9M -maxrate 11M -bufsize 18M -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k \
  -movflags +faststart "output/$name.mp4"
node ../.claude/skills/video-editing/scripts/verify-render.mjs "output/$name.mp4" | grep -E 'FAIL|GATE'
ffmpeg -v error -y -i "output/$name.mp4" -vf "fps=1,scale=216:-1,tile=6x3" -frames:v 1 "work/${name}_sheet.png"
