#!/usr/bin/env python3
"""Assets for the motion-graphics reels (round 3).

- mg/clips/<name>.mp4 : short muted product clips (1080x1920, 30fps, 1 keyframe/s,
  graded) that the compositions mount inside animated frames.
- mg/beat.wav : rights-free 120 BPM beat synthesized with numpy (kick, clap,
  hats, sub bass). Deterministic (fixed RNG seed).
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
MG = ROOT / "mg"
CLIPS = {
    # Jean Lowe Immortel (vid34)
    "jl_front": ("vid34", 5.0), "jl_holo": ("vid34", 17.5), "jl_peel": ("vid34", 26.0),
    "jl_back": ("vid34", 40.0), "jl_tube": ("vid34", 66.0), "jl_reveal": ("vid34", 84.5),
    "jl_bottle": ("vid34", 95.0), "jl_liquid": ("vid34", 102.5), "jl_end": ("vid34", 124.0),
    # Bharara King (vid31)
    "bh_open": ("vid31", 3.5), "bh_box": ("vid31", 7.0), "bh_hand": ("vid31", 15.0),
    "bh_table": ("vid31", 40.0), "bh_syringe": ("vid31", 57.0), "bh_draw": ("vid31", 64.0),
    "bh_fill": ("vid31", 76.0), "bh_cap": ("vid31", 86.0), "bh_spray": ("vid31", 100.0),
    "bh_final": ("vid31", 106.0),
}
CLIP_LEN = 4.5
SR = 48000
BPM = 120


def cut_clips():
    (MG / "clips").mkdir(parents=True, exist_ok=True)
    for name, (src, ss) in CLIPS.items():
        out = MG / "clips" / f"{name}.mp4"
        if out.exists():
            continue
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(CLIP_LEN),
            "-i", str(ROOT / "source" / f"{src}.mp4"), "-an", "-vf",
            "scale=1080:1936:flags=lanczos,crop=1080:1920,setsar=1,fps=30,"
            "eq=contrast=1.12:saturation=0.9",
            "-c:v", "libx264", "-crf", "18", "-g", "30", "-keyint_min", "30",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)


def env(n, attack, decay):
    t = np.arange(n) / SR
    e = np.exp(-t / decay)
    a = int(attack * SR)
    if a:
        e[:a] *= np.linspace(0, 1, a)
    return e


def synth_beat(seconds=32.0):
    rng = np.random.default_rng(7)
    n = int(seconds * SR)
    out = np.zeros(n)
    beat = 60 / BPM

    def put(sig, t, gain):
        i = int(t * SR)
        j = min(n, i + len(sig))
        out[i:j] += sig[: j - i] * gain

    # kick: pitch sweep 140 -> 45 Hz
    kn = int(0.35 * SR)
    kt = np.arange(kn) / SR
    freq = 45 + 95 * np.exp(-kt / 0.04)
    kick = np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(kn, 0.002, 0.12)
    # clap: band-limited noise bursts
    cn = int(0.25 * SR)
    noise = rng.standard_normal(cn)
    clap_f = np.convolve(noise, np.ones(6) / 6, mode="same") - np.convolve(noise, np.ones(40) / 40, mode="same")
    clap = clap_f * env(cn, 0.001, 0.06)
    # hat: high-passed noise, very short
    hn = int(0.06 * SR)
    hnoise = rng.standard_normal(hn)
    hat = (hnoise - np.convolve(hnoise, np.ones(4) / 4, mode="same")) * env(hn, 0.0005, 0.015)
    # sub bass notes (A minor-ish: A1, F1, C2, G1), one per bar
    notes = [55.0, 43.65, 65.41, 49.0]
    bar = beat * 4
    t_total = np.arange(n) / SR
    for b in range(int(seconds / bar) + 1):
        f = notes[b % 4]
        for k in range(8):  # eighth-note pulses
            t0 = b * bar + k * beat / 2
            if t0 >= seconds:
                break
            ln = int(beat / 2 * 0.9 * SR)
            tt = np.arange(ln) / SR
            s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * env(ln, 0.005, 0.12)
            put(s, t0, 0.35)
    steps = int(seconds / (beat / 2))
    for s in range(steps):
        t0 = s * beat / 2
        if s % 2 == 0:
            put(kick, t0, 0.9)
        if s % 4 == 2:
            put(clap, t0, 0.45)
        put(hat, t0 + (beat / 4 if s % 2 else 0), 0.18 if s % 2 else 0.12)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.8
    stereo = np.stack([out, out], axis=1)
    with wave.open(str(MG / "beat.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    MG.mkdir(exist_ok=True)
    cut_clips()
    synth_beat()
    print("clips:", len(list((MG / "clips").glob("*.mp4"))), "beat: mg/beat.wav")
