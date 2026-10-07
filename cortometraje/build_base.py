#!/usr/bin/env python3
"""Upscale the short film to a 1920x1080 / 30 fps silent base for the composition.

The film keeps its own cut and pacing; transitions and effects are layered on
top by fx_film.py and the HyperFrames text layer in edit/. Also extracts the boundary stills used by the whip-pan
transitions (outgoing last frame + incoming first frame of each whip cut), so a
whip can travel a full frame-width without real handles.
Writes edit/base.mp4 and edit/assets/stills/*.jpg.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source/corto_original.mp4"
EDIT = ROOT / "edit"
FPS = 30
FIT = "scale=1920:1080:flags=lanczos,setsar=1,hue=s=0,unsharp=5:5:0.5:5:5:0"

# Hard cuts in the source (frame index at 30 fps), found with scdet and checked
# frame by frame. 5479 is a jump cut inside the "YA TE ENCONTRÉ" note shot.
CUTS = [773, 2255, 3120, 3529, 4299, 4732, 5479, 5627, 5953, 6476, 6896, 7232, 7465]
WHIPS = [3120, 5627, 6896, 7232]


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    (EDIT / "assets/stills").mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-an", "-vf", f"{FIT},fps={FPS}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-g", "30", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(EDIT / "base.mp4")])
    for f in WHIPS:
        for n, tag in ((f - 1, "a"), (f, "b")):
            run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-vf",
                 f"select=eq(n\\,{n}),{FIT}", "-frames:v", "1", "-q:v", "2",
                 str(EDIT / f"assets/stills/cut{f}_{tag}.jpg")])
    (EDIT / "cuts.json").write_text(json.dumps(
        {"fps": FPS, "cuts": [{"frame": f, "t": round(f / FPS, 4)} for f in CUTS]}, indent=1))


if __name__ == "__main__":
    main()
