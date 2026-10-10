#!/usr/bin/env python3
"""Cut the source unboxing clips into a 1080x1920 / 30fps base video per reel.

Each reel is a list of (source_start, duration) shots. Shots are trimmed,
scaled/cropped to 9:16, lightly graded, and concatenated with their original
(ASMR) audio. The first shot gets a pixelated -> sharp reveal (hook).
source_start may also be a [from, to] range: that stretch of the source is
retimed to fill the shot (fast-forward, or a rewind when to < from).
A shot may also be a dict {"src": file, "at": start-or-[from, to], "zoom": z, "fy": f}
to pull it from another video; zoom > 1 punches in (fy = vertical focus, 0 top .. 1
bottom), e.g. to keep a source's burned-in titles out of frame.
Optional cfg keys: "grade" (ffmpeg eq chain), "pixel_reveal" (default True) and
"basename" (default "base"; e.g. "base_b" for a second, split-screen video).
Writes <reel>/base.mp4 and <reel>/shots.json (edit timeline for the composition).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REELS = {
    "edit-jeanlowe": {
        "src": "source/vid34.mp4",
        "shots": [
            (3.0, 1.8),    # box presented to camera (hook)
            (5.0, 1.6),    # box front close
            (15.0, 2.0),   # Maison Alhambra back label
            (27.0, 1.8),   # peeling the wrap
            (50.0, 1.9),   # inner box opening
            (66.0, 2.2),   # tube in hands
            (77.5, 1.8),   # tube lid off
            (84.5, 2.2),   # bottle reveal
            (95.0, 2.4),   # bottle close-up
            (102.5, 1.8),  # liquid tilt close
            (124.0, 2.6),  # bottle on base + SH logo (end card)
        ],
    },
    "edit-bharara": {
        "src": "source/vid31.mp4",
        "shots": [
            (3.5, 1.8),    # opening the black box (hook)
            (7.0, 1.6),    # box open, bottle visible
            (15.0, 1.6),   # bottle in hand
            (21.0, 1.5),   # bottle turning
            (40.0, 1.6),   # bottle placed on table
            (50.0, 1.8),   # pipette / prep
            (57.0, 2.4),   # syringe into the original
            (64.0, 2.0),   # drawing the juice
            (76.0, 2.0),   # filling the vial
            (86.0, 1.8),   # capping the vial
            (100.0, 1.8),  # spray head on
            (106.0, 2.6),  # final: bottle + decant (end card)
        ],
    },
}

GRADE = "eq=contrast=1.12:saturation=0.88:brightness=-0.01"
FIT = "scale=1080:1936:flags=lanczos,crop=1080:1920,setsar=1,fps=30"


def build(name, cfg):
    out_dir = ROOT / name
    out_dir.mkdir(exist_ok=True)
    src = str(ROOT / cfg["src"])
    grade = cfg.get("grade", GRADE)
    basename = cfg.get("basename", "base")
    # one seeked input per shot: shots out of source order would otherwise make
    # ffmpeg buffer every decoded frame between them
    inputs, parts, labels, timeline, t = [], [], [], [], 0.0
    for i, (ss, dur) in enumerate(cfg["shots"]):
        shot_src, fit = src, FIT
        if isinstance(ss, dict):
            shot_src = str(ROOT / ss["src"])
            z = ss.get("zoom", 1.0)
            if z != 1.0:
                w, h = round(1080 * z / 2) * 2, round(1936 * z / 2) * 2
                fit = (f"scale={w}:{h}:flags=lanczos,"
                       f"crop=1080:1920:(iw-1080)/2:(ih-1920)*{ss.get('fy', 0.5)},setsar=1,fps=30")
            ss = ss["at"]
        if isinstance(ss, (list, tuple)):
            a, b = ss
            lo, span = min(a, b), abs(b - a)
            # drop to 30 fps before reversing so `reverse` only buffers this shot's frames
            v = (f"[{i}:v]trim=duration={span},setpts=(PTS-STARTPTS)*{dur / span:.6f},"
                 f"fps=30{',reverse' if b < a else ''},tpad=stop_mode=clone:stop_duration=0.2,"
                 f"trim=duration={dur},{fit},{grade}")
        else:
            lo, span = ss, dur
            v = (f"[{i}:v]trim=duration={dur},setpts=PTS-STARTPTS,{fit},{grade}")
        inputs += ["-ss", f"{lo}", "-t", f"{max(span, dur) + 0.3:.3f}", "-i", shot_src]
        if i == 0 and cfg.get("pixel_reveal", True):
            # pixelated -> sharp reveal over the first 0.5s, three block sizes
            v += ",split=4[s0][p1][p2][p3];"
            v += "[p1]scale=27:48,scale=1080:1920:flags=neighbor[q1];"
            v += "[p2]scale=54:96,scale=1080:1920:flags=neighbor[q2];"
            v += "[p3]scale=135:240,scale=1080:1920:flags=neighbor[q3];"
            v += "[s0][q1]overlay=enable='lt(t,0.17)'[o1];"
            v += "[o1][q2]overlay=enable='between(t,0.17,0.33)'[o2];"
            v += f"[o2][q3]overlay=enable='between(t,0.33,0.5)'[v{i}]"
        else:
            v += f"[v{i}]"
        a = (f"[{i}:a]atrim=duration={dur},asetpts=PTS-STARTPTS,"
             f"aresample=48000,apad=whole_dur={dur},atrim=duration={dur},"
             f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.04:.2f}:d=0.04[a{i}]")
        parts += [v, a]
        labels.append(f"[v{i}][a{i}]")
        timeline.append({"start": round(t, 3), "duration": dur, "src": cfg["shots"][i][0]})
        t += dur
    n = len(cfg["shots"])
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={n}:v=1:a=1[v][a]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16",
           "-preset", "medium", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le",
           str(out_dir / f"{basename}.mkv")]
    subprocess.run(cmd, check=True)
    # video-only MP4 for the composition, audio as wav for the master mix
    mkv = out_dir / f"{basename}.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mkv),
                    "-an", "-c:v", "copy", "-movflags", "+faststart",
                    str(out_dir / f"{basename}.mp4")], check=True)
    (ROOT / "work").mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mkv),
                    "-vn", "-c:a", "pcm_s16le", "-ac", "2",
                    str(ROOT / "work" / f"{name}_{basename}_asmr.wav" if basename != "base"
                        else ROOT / "work" / f"{name}_asmr.wav")], check=True)
    mkv.unlink()
    (out_dir / ("shots.json" if basename == "base" else f"{basename}_shots.json")).write_text(json.dumps(
        {"duration": round(t, 3), "shots": timeline}, indent=2))
    print(f"{name}: {n} shots, {t:.2f}s")


if __name__ == "__main__":
    for name in sys.argv[1:] or REELS:
        build(name, REELS[name])
