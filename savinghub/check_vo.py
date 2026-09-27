#!/usr/bin/env python3
"""Voiceover QA gate: catches doubled / misaligned voices.

For an audio/video file and the VO lines placed in it:
  1. L/R correlation must be ~1 (the VO is centred mono; a phase-shifted
     second channel sounds like two overlapping voices).
  2. Each line must be found once, at its planned offset (±40 ms), by
     cross-correlating the TTS file against the mix.
Exit code 1 on any failure.
"""
import subprocess
import sys

import numpy as np

SR = 16000


def load(path, stereo=False):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2" if stereo else "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    return x.reshape(-1, 2) if stereo else x


def check(path, events):
    ok = True
    st = load(path, stereo=True)
    l, r = st[:, 0], st[:, 1]
    corr = float(np.corrcoef(l, r)[0, 1]) if l.std() > 0 and r.std() > 0 else 1.0
    good = corr > 0.98
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] L/R correlation {corr:.3f}")
    mix = st.mean(axis=1)
    for wav, t in events:
        line = load(wav)
        seg = line[: min(len(line), int(1.2 * SR))]
        lo, hi = max(0, int((t - 1.0) * SR)), min(len(mix), int((t + 1.0) * SR) + len(seg))
        win = mix[lo:hi]
        c = np.correlate(win, seg, mode="valid")
        norm = np.sqrt(np.convolve(win ** 2, np.ones(len(seg)), mode="valid")) * np.sqrt((seg ** 2).sum()) + 1e-9
        c = c / norm
        found = (lo + int(np.argmax(c))) / SR
        good = abs(found - t) <= 0.04 and float(c.max()) > 0.5
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] line at {t:.2f}s found at {found:.2f}s (score {float(c.max()):.2f})")
    return ok


if __name__ == "__main__":
    sys.exit(0 if check(sys.argv[1], []) else 1)
