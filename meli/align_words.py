#!/usr/bin/env python3
"""Word timings for the three clips.

Text comes from a Higgsfield video-analysis transcript. Phrase spans (source
seconds) were set by matching phrases to pauses in the speech-energy envelope
(data/v*.wav.npy, 10 ms frames); words inside a phrase are spread by syllable
count over the voiced frames. Writes data/words.json.
"""
import json, re
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
PHRASES = {
    "v2": [(0.79, 2.77, "Che, ¿viste que a veces uno quiere aprender inglés,"),
           (3.07, 4.93, "pero pareciera que tiene que saber"),
           (4.93, 6.14, "un montón antes de empezar?"),
           (6.71, 6.98, "Bueno,"), (7.24, 7.46, "no."),
           (7.98, 9.21, "Esto lo escucho siempre,"),
           (9.36, 9.76, "pero ¿sabés qué?"),
           (9.89, 13.10, "No necesitás saber absolutamente nada para arrancar.")],
    "v3": [(0.90, 2.00, "Podés empezar con frases"),
           (2.32, 4.20, "súper sencillas como por ejemplo"),
           (4.39, 5.33, "decir tu nombre,"), (5.77, 6.30, "tu edad,"),
           (6.63, 8.08, "o contar algo sobre vos."),
           (8.32, 9.92, "Obvio que te voy a ayudar, ¿por qué?"),
           (9.95, 12.03, "Porque la idea no es que te llenes de reglas"),
           (12.52, 13.16, "sin sentido,"), (13.54, 14.23, "sino más bien"),
           (14.61, 15.71, "que vayas construyendo"), (16.20, 16.89, "con frases"),
           (17.16, 17.68, "útiles,"), (18.17, 19.66, "un vocabulario que te sirva"),
           (19.66, 20.56, "en un inglés real.")],
    "v1": [(0.79, 2.47, "Así que si venís pateando el inglés"),
           (2.63, 4.00, "porque pensás que estás en cero,"),
           (4.00, 4.65, "escribí CERO"),
           (4.79, 6.40, "y te cuento cómo son mis clases."),
           (7.18, 7.80, "Bye!")],
}

def syl(w):
    w = re.sub(r"[^a-záéíóúüñ]", "", w.lower())
    if w == "bye": return 1
    groups = re.sub(r"[^aeiouáéíóúü]", " ", w).split()
    n = 0
    for g in groups:
        n += 1 + sum(1 for a, b in zip(g, g[1:])
                     if (a in "aeoáéó" and b in "aeoáéó") or a in "íú" or b in "íú")
    return max(n, 1)

out = {}
for clip, phrases in PHRASES.items():
    db = np.load(ROOT / f"data/{clip}.wav.npy")
    p10, p90 = np.percentile(db, [10, 90])
    voiced = db >= p10 + (p90 - p10) * 0.30
    words = []
    for pi, (s, e, text) in enumerate(phrases):
        fs, fe = int(round(s * 100)), int(round(e * 100))
        v = voiced[fs:fe].astype(float)
        v[v == 0] = 0.15            # unvoiced frames still advance time a little
        cum = np.cumsum(v); total = cum[-1]
        toks = text.split(); sy = [syl(t) for t in toks]; S = sum(sy); acc = 0
        for t, n in zip(toks, sy):
            a = fs + int(np.searchsorted(cum, acc / S * total)); acc += n
            b = fs + int(np.searchsorted(cum, acc / S * total))
            words.append({"w": t, "s": round(a / 100, 2), "e": round(min(b, fe) / 100, 2), "p": pi})
    out[clip] = words
(ROOT / "data/words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for c, ws in out.items():
    print(c, " ".join(f"{w['w']}@{w['s']}" for w in ws))
