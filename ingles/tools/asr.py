#!/usr/bin/env python3
"""Transcription helpers for cutting "Inglés Reel" talking-head clips (offline, sherpa-onnx).

    python3 tools/asr.py segments <video>     # speech segments between pauses + their text (to pick the cuts)
    python3 tools/asr.py words <reel-dir>     # word times for every cut in reel.json (to time the text beats)

Models (Parakeet TDT 0.6b v3 multilingual, Spanish + English) are downloaded once from the sherpa-onnx
GitHub releases into ~/.cache/sherpa-onnx-models. Needs: pip install sherpa-onnx numpy.

Word times printed by `words` are already corrected (+0.08 s, first word clamped to the cut start)
and expressed as "SRC:seconds", ready to paste into reel.json beats.
"""
import json
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/sherpa-onnx-models"
MODEL = "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{MODEL}.tar.bz2"
SR = 16000


def recognizer():
    import sherpa_onnx
    d = CACHE / MODEL
    if not (d / "tokens.txt").exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        tgz = CACHE / f"{MODEL}.tar.bz2"
        print("downloading", URL, file=sys.stderr)
        urllib.request.urlretrieve(URL, tgz)
        with tarfile.open(tgz) as t:
            t.extractall(CACHE)
        tgz.unlink()
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / "encoder.int8.onnx"), decoder=str(d / "decoder.int8.onnx"),
        joiner=str(d / "joiner.int8.onnx"), tokens=str(d / "tokens.txt"),
        model_type="nemo_transducer", num_threads=4)


def load(video):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def decode(rec, x):
    """Words with start times relative to x (0.3 s of silence padding on both sides)."""
    pad = np.zeros(int(0.3 * SR), dtype=np.float32)
    s = rec.create_stream()
    s.accept_waveform(SR, np.concatenate([pad, x, pad]))
    rec.decode_stream(s)
    words, cur = [], None
    for tok, t in zip(s.result.tokens, s.result.timestamps):
        if tok.startswith((" ", "▁")) or cur is None:
            if cur:
                words.append(cur)
            cur = {"w": tok.lstrip(" ▁"), "t": round(t - 0.3, 3)}
        else:
            cur["w"] += tok
    if cur:
        words.append(cur)
    return s.result.text.strip(), words


def pauses(x, min_len=0.2, frac=0.2):
    """Low-energy runs (speech band 250-3500 Hz) as (start, end) seconds."""
    hop, win = int(0.01 * SR), int(0.03 * SR)
    fr = np.fft.rfftfreq(win, 1 / SR)
    band = (fr > 250) & (fr < 3500)
    db = np.array([10 * np.log10((np.abs(np.fft.rfft(x[i:i + win] * np.hanning(win))) ** 2)[band].sum() + 1e-10)
                   for i in range(0, len(x) - win, hop)])
    db = np.convolve(db, np.ones(5) / 5, mode="same")
    floor, peak = np.percentile(db, 8), np.percentile(db, 90)
    low = db < floor + frac * (peak - floor)
    runs, i = [], 0
    while i < len(low):
        if low[i]:
            j = i
            while j < len(low) and low[j]:
                j += 1
            if (j - i) * 0.01 >= min_len:
                runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return runs


def cmd_segments(video):
    x = load(video)
    rec = recognizer()
    dur = len(x) / SR
    t, segs = 0.0, []
    for a, b in pauses(x):
        if a - t > 0.05:
            segs.append((t, a))
        t = b
    if dur - t > 0.05:
        segs.append((t, dur))
    for a, b in segs:
        pa, pb = max(0, a - 0.12), min(dur, b + 0.12)
        text, _ = decode(rec, x[int(pa * SR):int(pb * SR)])
        print(f"{a:6.2f}-{b:6.2f} ({b - a:.2f})  {text}")


def cmd_words(reel_dir):
    d = (ROOT / reel_dir).resolve()
    cfg = json.loads((d / "reel.json").read_text())
    audio = {k: load(ROOT / v) for k, v in cfg["sources"].items()}
    rec = recognizer()
    for i, c in enumerate(cfg["cuts"]):
        src, a, b = c[0], float(c[1]), float(c[2])
        text, words = decode(rec, audio[src][int(a * SR):int(b * SR)])
        out = []
        for k, w in enumerate(words):
            t = a + w["t"] + 0.08
            if k == 0:
                t = max(t, a + 0.06)
            out.append(f'{w["w"]}={src}:{t:.2f}')
        print(f"#{i:02d} {src} [{a:.2f}-{b:.2f}]  " + " ".join(out))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("segments", "words"):
        sys.exit(__doc__)
    {"segments": cmd_segments, "words": cmd_words}[sys.argv[1]](sys.argv[2])
