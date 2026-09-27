#!/usr/bin/env python3
"""Synthesize rights-free SFX and mix them with each reel's ASMR track into
one master audio file (<reel>/master.m4a), per the video-editing skill."""
import json
import subprocess
from pathlib import Path

from build_comp import REELS

ROOT = Path(__file__).resolve().parent
SFX = ROOT / "sfx"
SR = 48000


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def make_sfx():
    SFX.mkdir(exist_ok=True)
    ff("-f", "lavfi", "-i", f"anoisesrc=duration=0.35:color=pink:sample_rate={SR}:amplitude=0.6:seed=7",
       "-af", "afade=t=in:st=0:d=0.04,afade=t=out:st=0.1:d=0.25,highpass=f=400,lowpass=f=7000",
       str(SFX / "whoosh.wav"))
    ff("-f", "lavfi", "-i", f"sine=frequency=62:duration=0.6:sample_rate={SR}",
       "-f", "lavfi", "-i", f"anoisesrc=duration=0.12:color=brown:sample_rate={SR}:amplitude=0.8:seed=3",
       "-filter_complex",
       "[0]volume=1.4,afade=t=out:st=0.03:d=0.55[b];[1]lowpass=f=900,afade=t=out:st=0.02:d=0.1[n];"
       "[b][n]amix=inputs=2:normalize=0,alimiter=limit=0.9",
       str(SFX / "impact.wav"))
    ff("-f", "lavfi", "-i", f"sine=frequency=1900:duration=0.035:sample_rate={SR}",
       "-af", "afade=t=out:st=0.008:d=0.027", str(SFX / "click.wav"))
    ff("-f", "lavfi", "-i",
       f"aevalsrc='0.35*sin(2*PI*(200*t+900*t*t))':s={SR}:d=0.8",
       "-f", "lavfi", "-i", f"anoisesrc=duration=0.8:color=white:sample_rate={SR}:amplitude=0.25:seed=11",
       "-filter_complex",
       "[1]highpass=f=2500[n];[0][n]amix=inputs=2:normalize=0,afade=t=in:st=0:d=0.7,afade=t=out:st=0.74:d=0.06",
       str(SFX / "riser.wav"))


def mix(name, cfg):
    out = ROOT / name
    shots = json.loads((out / "shots.json").read_text())
    dur = shots["duration"]
    events = []  # (file, time, volume)
    for s in shots["shots"][1:]:
        events.append(("whoosh", s["start"] - 0.06, 0.22))
    for p in cfg["punch"]:
        events.append(("impact", p, 0.55))
    for ph in cfg["phrases"]:
        events.append(("click", ph["t"], 0.18))
    end_t = cfg["end"]["t"]
    events += [("riser", end_t - 0.8, 0.28), ("impact", end_t + 0.1, 0.5),
               ("click", end_t + 1.25, 0.2)]
    for extra in cfg.get("risers", []):
        events.append(("riser", extra - 0.8, 0.25))

    inputs = ["-i", str(ROOT / "work" / f"{name}_asmr.wav")]
    chains = ["[0]acompressor=threshold=-30dB:ratio=4:attack=5:release=120:makeup=8,"
              "loudnorm=I=-17:TP=-2:LRA=9,aresample=48000[asmr]"]
    labels = ["[asmr]"]
    for i, (f, t, vol) in enumerate(events, start=1):
        inputs += ["-i", str(SFX / f"{f}.wav")]
        ms = max(0, int(round(t * 1000)))
        chains.append(f"[{i}]aresample=48000,adelay={ms}|{ms},volume={vol}[e{i}]")
        labels.append(f"[e{i}]")
    fc = ";".join(chains) + ";" + "".join(labels) + \
        f"amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.95," \
        f"apad,atrim=0:{dur},afade=t=out:st={dur - 0.4}:d=0.4[mix]"
    ff(*inputs, "-filter_complex", fc, "-map", "[mix]", "-ar", "48000", "-ac", "2",
       "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a"))
    print(f"{name}: master.m4a ({len(events)} sfx events)")


if __name__ == "__main__":
    make_sfx()
    for name, cfg in REELS.items():
        mix(name, cfg)
