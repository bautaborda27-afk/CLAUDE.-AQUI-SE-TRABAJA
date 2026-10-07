#!/usr/bin/env python3
"""Synthesize rights-free SFX and mix them under the film's own music into one
master track (work/master.m4a).

Each SFX is placed on the frame of its transition (plan.py) and levelled
against the music around it: target = local music RMS + an offset per sound,
clamped to an audible floor, so a whoosh in a quiet stretch does not jump out
and an impact in the chase still lands. Final loudness: -14 LUFS.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

from plan import (C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, FILM, FIN_AT,
                  HEARTBEATS, HIT, NOTE1, NOTE2, TOTAL)

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source/corto_original.mp4"
SFX = ROOT / "sfx"
WORK = ROOT / "work"
EDIT = ROOT / "edit"
SR = 48000


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def make_sfx():
    SFX.mkdir(exist_ok=True)
    noise = lambda d, color, amp, seed: (
        "-f", "lavfi", "-i", f"anoisesrc=duration={d}:color={color}:sample_rate={SR}:amplitude={amp}:seed={seed}")
    ff(*noise(0.4, "pink", 0.6, 7), "-af",
       "afade=t=in:st=0:d=0.18:curve=qsin,afade=t=out:st=0.2:d=0.2,highpass=f=300,lowpass=f=6000",
       str(SFX / "whoosh.wav"))
    # whip: brighter, faster swell that peaks on the cut
    ff(*noise(0.4, "white", 0.5, 21), "-af",
       "afade=t=in:st=0:d=0.2:curve=exp,afade=t=out:st=0.2:d=0.2:curve=exp,"
       "bandpass=f=2200:width_type=o:w=2.5,highpass=f=500", str(SFX / "whip.wav"))
    ff("-f", "lavfi", "-i", f"sine=frequency=58:duration=0.7:sample_rate={SR}",
       *noise(0.14, "brown", 0.8, 3), "-filter_complex",
       "[0]volume=1.4,afade=t=out:st=0.03:d=0.65[b];[1]lowpass=f=900,afade=t=out:st=0.02:d=0.12[n];"
       "[b][n]amix=inputs=2:normalize=0,alimiter=limit=0.9", str(SFX / "impact.wav"))
    ff("-f", "lavfi", "-i", f"sine=frequency=46:duration=2.4:sample_rate={SR}",
       *noise(0.3, "brown", 0.9, 5), "-filter_complex",
       "[0]volume=1.5,afade=t=out:st=0.05:d=2.3[b];[1]lowpass=f=700,afade=t=out:st=0.02:d=0.28[n];"
       "[b][n]amix=inputs=2:normalize=0,aecho=0.8:0.6:120|260:0.35|0.2,alimiter=limit=0.9",
       str(SFX / "boom.wav"))
    ff(*noise(0.3, "white", 0.6, 13), "-af",
       "acrusher=bits=5:mode=log:samples=24,tremolo=f=26:d=0.95,highpass=f=700,"
       "afade=t=out:st=0.22:d=0.08", str(SFX / "glitch.wav"))
    ff("-f", "lavfi", "-i", f"sine=frequency=1900:duration=0.035:sample_rate={SR}",
       "-af", "afade=t=out:st=0.008:d=0.027", str(SFX / "click.wav"))
    ff("-f", "lavfi", "-i", f"aevalsrc='0.35*sin(2*PI*(160*t+700*t*t))':s={SR}:d=0.8",
       *noise(0.8, "white", 0.25, 11), "-filter_complex",
       "[1]highpass=f=2500[n];[0][n]amix=inputs=2:normalize=0,afade=t=in:st=0:d=0.7:curve=exp,"
       "afade=t=out:st=0.75:d=0.05", str(SFX / "riser.wav"))
    ff(*noise(0.5, "white", 0.4, 17), "-af",
       "highpass=f=4000,afade=t=in:st=0:d=0.12,afade=t=out:st=0.15:d=0.35", str(SFX / "shimmer.wav"))
    ff(*noise(1.4, "pink", 0.5, 29), "-af",
       "lowpass=f=900,afade=t=in:st=0:d=1.2:curve=exp,afade=t=out:st=1.25:d=0.15", str(SFX / "swell.wav"))
    # heartbeat: lub-dub, two low thumps
    ff("-f", "lavfi", "-i",
       f"aevalsrc='0.9*sin(2*PI*52*t)*exp(-22*t)+0.7*sin(2*PI*46*(t-0.17))*exp(-24*(t-0.17))*gte(t,0.17)':"
       f"s={SR}:d=0.55", "-af", "lowpass=f=180", str(SFX / "heartbeat.wav"))


def read_wav(p):
    with wave.open(str(p)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()).mean(axis=1) if w.getnchannels() > 1 else a


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


# (sound, time, dB over local music, absolute floor dBFS)
def events():
    ev = [("swell", 0.0, 0, -30), ("impact", 0.15, 4, -24)]
    ev += [("whoosh", C1 - 0.2, 2, -28), ("whoosh", C9 - 0.2, 2, -28),
           ("whoosh", C13 - 0.2, 0, -24), ("impact", C13, 0, -24)]
    ev += [("whoosh", C2 - 0.2, 2, -28), ("click", C2, -4, -32)]
    for line in NOTE1["lines"]:
        for word, t, red in line:
            ev.append(("impact", t, 6, -22) if red else ("click", t, -2, -30))
    t_red1 = NOTE1["lines"][-1][-1][1]
    ev += [("riser", t_red1 - 0.8, 0, -30), ("whoosh", NOTE1["end"] - 0.3, -4, -32)]
    for c in (C3, C8, C11, C12):
        ev.append(("whip", c - 0.2, 3, -26))
    ev += [("shimmer", C4 - 0.2, 0, -30), ("whoosh", C4 - 0.2, 0, -30)]
    ev += [("glitch", C5 - 0.3, 2, -28), ("impact", C5, 2, -26)]
    ev += [("whoosh", C6 - 0.25, 0, -30), ("impact", C6, 3, -26)]
    ev += [("heartbeat", hb, 5 + 0.5 * i, -26) for i, hb in enumerate(HEARTBEATS)]
    for line in NOTE2["lines"]:
        for word, t, red in line:
            ev.append(("impact", t, 8, -20) if red else ("click", t, -2, -30))
    t_red2 = NOTE2["lines"][-1][-1][1]
    ev += [("glitch", t_red2, 2, -26), ("glitch", C7 - 0.18, 2, -26), ("impact", C7, 5, -22)]
    ev += [("glitch", C10 - 0.27, 2, -26), ("impact", C10, 6, -20)]
    ev += [("impact", HIT, 0, -18), ("glitch", HIT, -2, -24)]
    ev += [("glitch", FILM - 0.55, 0, -22), ("boom", FILM - 0.02, 2, -16), ("click", FIN_AT, -6, -30)]
    return ev


def mix():
    WORK.mkdir(exist_ok=True)
    ff("-i", str(SRC), "-vn", "-ac", "1", "-ar", str(SR), str(WORK / "music.wav"))
    music = read_wav(WORK / "music.wav")
    n = int(round(TOTAL * SR))
    music = np.pad(music, (0, max(0, n - len(music))))[:n]
    # fade the music out under the closing bars; the boom tail carries the FIN card
    f0, f1 = int((FILM - 0.35) * SR), int(FILM * SR)
    music[f0:f1] *= np.linspace(1, 0, f1 - f0) ** 2
    music[f1:] = 0
    music *= 10 ** (5 / 20)

    out = music.copy()
    log = []
    for name, t, over, floor in events():
        s = read_wav(SFX / f"{name}.wav")
        i0 = int(round(t * SR))
        a, b = max(0, int((t - 0.6) * SR)), min(f1, int((t + 0.6) * SR))
        local = rms_db(music[a:b]) if b > a else -60
        target = min(max(local + over, floor), -8 if name in ("boom", "impact", "whip") else -14)
        g = 10 ** ((target - rms_db(s)) / 20)
        seg = s[: n - i0] * g
        out[i0:i0 + len(seg)] += seg
        log.append(f"{t:8.3f} {name:9} local {local:6.1f} -> {target:6.1f} dB")
    out = np.tanh(out * 1.1) / 1.1                  # soft clip before the limiter
    fade = int(0.4 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(WORK / "master_raw.wav"), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    (WORK / "sfx_log.txt").write_text("\n".join(log) + "\n")

    # two-pass loudnorm to -14 LUFS (linear), then AAC for the composition
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(WORK / "master_raw.wav"), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=20:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True).stderr
    import json
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=20:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true")
    ff("-i", str(WORK / "master_raw.wav"), "-af", f"{ln},alimiter=limit=0.8:level=false,aresample={SR}", "-ac", "2",
       "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL}", str(WORK / "master.m4a"))
    print(f"master.m4a: {TOTAL}s, {len(log)} sfx events (input {m['input_i']} LUFS)")


if __name__ == "__main__":
    make_sfx()
    mix()
