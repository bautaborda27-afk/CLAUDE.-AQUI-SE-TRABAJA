#!/bin/bash
# Final pass: film layer + HyperFrames text layers (RGBA png sequences at their
# mount times) + film grain over everything + master audio, 2-pass H.264 sized
# to stay under GitHub's 100 MB file limit. Then the render gate + contact sheet.
#   ./finalize.sh [OutputName]
set -euo pipefail
cd "$(dirname "$0")"
name=${1:-Corto_Transiciones_Efectos}
mkdir -p output work
ov=($(python3 -c "
import json
for o in json.load(open('edit/overlays.json')):
    print('-itsoffset', o['start'], '-framerate', 30, '-i', 'work/overlay/%s/frame_%%06d.png' % o['id'], end=' ')
"))
fc="[0:v][1:v]overlay=eof_action=pass[a];[a][2:v]overlay=eof_action=pass[b];[b][3:v]overlay=eof_action=pass,"
fc+="noise=alls=9:allf=t,format=yuv420p[v]"
common=(-i work/film_fx.mp4 "${ov[@]}" -i work/master.m4a -filter_complex "$fc" -map "[v]"
        -c:v libx264 -preset slow -tune film -b:v 2700k -maxrate 5000k -bufsize 8000k -r 30)
ffmpeg -v error -y "${common[@]}" -pass 1 -passlogfile work/x264 -an -f null /dev/null
ffmpeg -v error -y "${common[@]}" -pass 2 -passlogfile work/x264 -map 4:a -c:a aac -b:a 192k \
  -shortest -movflags +faststart "output/$name.mp4"
node ../.claude/skills/video-editing/scripts/verify-render.mjs "output/$name.mp4" \
  --width 1920 --height 1080 --duration 258.5 | grep -E 'FAIL|GATE|PASS'
ffmpeg -v error -y -i "output/$name.mp4" -vf "fps=1/6,scale=320:-1,tile=8x6" -frames:v 1 "work/${name}_sheet.jpg"
ls -la "output/$name.mp4"
