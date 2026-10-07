#!/usr/bin/env python3
"""Voiceover reels (round 2): AI voice (Kokoro, local) drives the edit.

Each video is a list of lines. A line has:
  vo   — what the voice says (spelled phonetically where Kokoro needs help)
  cap  — the on-screen caption (giant Anton caps, "*" marks the red key word)
  shots — source timestamps covering the line (time is split evenly); a
          [from, to] pair retimes that stretch to fit (fast-forward / rewind)
  sfx   — optional extra SFX at the start of the line (e.g. "rewind")
The last line plays over the branded end card.
A video with "sync": True writes `cap` word-for-word with `vo` and times each
caption word to its estimated onset in the speech; "|" in a caption forces a
new caption screen.

Pipeline per video: TTS each line -> lay out timeline from VO durations ->
cut base video (build_base) -> captions/animation (build_comp) -> mix VO +
SFX into master.m4a (no original sound). Render with `hyperframes render` after.
"""
import json
import subprocess
import sys
from pathlib import Path

import build_audio
import build_base
import build_comp

ROOT = Path(__file__).resolve().parent
TTS = ROOT / "work" / "tts"
SFX = ROOT / "sfx"
VOICE, SPEED = "ef_dora", 1.08
GAP = 0.12          # breath between lines
TAIL = 1.1          # hold after the last line

# ---- Idea 1: Jean Lowe — "¿Cómo saber si tu perfume árabe es original?"
JEANLOWE_ORIGINAL = {
    "src": "source/vid34.mp4",
    "tag": ["LUJO SIN PAGAR", "DE *MÁS"],
    "lines": [
        {"vo": "¿Cómo saber si tu perfume árabe es original?",
         "cap": "¿CÓMO SABER SI TU PERFUME ÁRABE ES *ORIGINAL?", "shots": [3.0, 5.0], "punch": True},
        {"vo": "Fijate en tres cosas.", "cap": "FIJATE EN *3 COSAS", "shots": [10.0]},
        {"vo": "Uno: el holograma en la caja.", "cap": "*1. HOLOGRAMA EN LA CAJA", "shots": [17.5]},
        {"vo": "Dos: que venga sellado, con el film intacto.",
         "cap": "*2. SELLADO CON FILM INTACTO", "shots": [26.0, 28.0]},
        {"vo": "Tres: toda la información impresa atrás.",
         "cap": "*3. INFO IMPRESA ATRÁS", "shots": [40.0]},
        {"vo": "Nosotros lo abrimos frente a cámara.",
         "cap": "LO ABRIMOS FRENTE A *CÁMARA", "shots": [50.5, 66.0]},
        {"vo": "Yin Lou Inmortel, de Maison Alhambra.",
         "cap": "JEAN LOWE *IMMORTEL", "shots": [84.5, 95.0]},
        {"vo": "Séiving Jab. Lujo sin pagar de más.", "cap": None, "shots": [124.0]},
    ],
}

# ---- Idea 2: Bharara King — "Así armamos tu decant" (body shared by the hook test)
BHARARA_BODY = [
    {"vo": "Así armamos tu decánt.", "cap": "ASÍ ARMAMOS TU *DECANT", "shots": [15.0]},
    {"vo": "Sacamos el perfume directo del frasco original, con jeringa.",
     "cap": "DIRECTO DEL FRASCO *ORIGINAL", "shots": [57.0, 64.0], "plate": True},
    {"vo": "Lo pasamos a un atomizador de vidrio.",
     "cap": "A UN ATOMIZADOR DE *VIDRIO", "shots": [76.0]},
    {"vo": "Lo cerramos, y listo.", "cap": "Y *LISTO", "shots": [86.0, 100.0]},
    {"vo": "Probás Bajarára King, sin gastar en el frasco entero.",
     "cap": "PROBÁS BHARARA KING SIN GASTAR DE *MÁS", "shots": [40.0, 50.5]},
    {"vo": "Séiving Jab. Pedilo por mensaje.", "cap": None, "shots": [106.0]},
]
HOOK_SHOTS = [3.5, 7.0]
HOOKS = {
    "a": {"vo": "¿Qué es un decánt? Mirá.", "cap": "¿QUÉ ES UN *DECANT?"},
    "b": {"vo": "No compres un perfume de lujo a ciegas.", "cap": "NO COMPRES UN PERFUME A *CIEGAS"},
    "c": {"vo": "Este perfume cuesta una fortuna. Pero hay un truco.",
          "cap": "ESTE PERFUME CUESTA UNA *FORTUNA"},
}

# ---- Round 4: packing a wholesale order — "Todo esto es un pedido mayorista" (rewind hook)
PEDIDO = {
    "src": "source/vid_pedido.mp4",
    "tag": ["¿QUERÉS", "*REVENDER?"],
    "cta": "ESCRIBINOS POR DM",
    "sync": True,
    "lines": [
        {"vo": "Todo esto, es un pedido mayorista.", "cap": "TODO ESTO ES UN PEDIDO *MAYORISTA",
         "shots": [[75.4, 77.3]], "punch": True},
        {"vo": "Rebobinemos.", "cap": "*REBOBINEMOS", "shots": [[77.3, 7.0]], "sfx": "rewind"},
        {"vo": "Primero, el Asád de Latáfa, bien al fondo.",
         "cap": "PRIMERO, EL *ASAD DE LATTAFA, | BIEN AL *FONDO",
         "shots": [[7.0, 9.7], 9.9, [10.7, 12.2]]},
        {"vo": "Después, cada caja en su lugar, bien apretada.",
         "cap": "DESPUÉS, CADA CAJA | EN SU *LUGAR, | BIEN *APRETADA",
         "shots": [[15.5, 19.5], [22.5, 26.5], [29.0, 33.0]]},
        {"vo": "Club de Nuí Inténs, de Armáf. Y el Vúlcan.",
         "cap": "CLUB DE NUIT INTENSE, DE *ARMAF. | Y EL *VULCAN",
         "shots": [37.6, [40.5, 44.0], 47.8, [50.0, 54.0]]},
        {"vo": "Y hasta el cargador, con su cable.", "cap": "Y HASTA EL *CARGADOR, | CON SU *CABLE",
         "shots": [67.6, 71.9]},
        {"vo": "Papel de relleno, para que llegue perfecto.",
         "cap": "PAPEL DE RELLENO, | PARA QUE LLEGUE *PERFECTO",
         "shots": [[85.0, 90.0], [93.0, 97.0], [99.0, 103.0]]},
        {"vo": "Serramos, y listo para salir.", "cap": "CERRAMOS, | Y LISTO PARA *SALIR",
         "shots": [[103.5, 107.0], [107.0, 110.5]]},
        {"vo": "Séiving Jab. ¿Querés revender? Escribinos por mensaje.", "cap": None,
         "shots": [[75.4, 77.3]]},
    ],
}

VIDEOS = {"edit-v2-jeanlowe-original": JEANLOWE_ORIGINAL, "edit-v4-pedido": PEDIDO}
for k, h in HOOKS.items():
    VIDEOS[f"edit-v2-bharara-hook-{k}"] = {
        "src": "source/vid31.mp4",
        "tag": ["PROBÁ ANTES", "DE *COMPRAR"],
        "lines": [{**h, "shots": HOOK_SHOTS, "punch": True}] + BHARARA_BODY,
    }


def sh(*cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def tts(text):
    TTS.mkdir(parents=True, exist_ok=True)
    key = f"{VOICE}_{SPEED}_" + "".join(c if c.isalnum() else "_" for c in text)[:80]
    raw, out = TTS / f"{key}.raw.wav", TTS / f"{key}.wav"
    if not out.exists():
        sh("hyperframes", "tts", text, "-v", VOICE, "-s", str(SPEED), "-o", str(raw),
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # trim leading/trailing silence so the timeline follows the speech
        sh("ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "aresample=48000", "-ac", "1", str(out))
        raw.unlink()
    return out


def chunk_caption(cap):
    """Split a caption into screens (<=6 words) of lines (<=12 chars); "|" forces a new screen."""
    return [sc for part in cap.split("|") for sc in _chunk(part)]


def _chunk(cap):
    words = cap.split()
    screens, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 6:
            screens.append(cur)
            cur = []
    if cur:
        if screens and len(cur) <= 2:
            screens[-1] += cur
        else:
            screens.append(cur)
    out = []
    for sc in screens:
        lines, line = [], []
        for w in sc:
            if line and len(" ".join(line + [w]).replace("*", "")) > 12:
                lines.append(line)
                line = []
            line.append(w)
        lines.append(line)
        out.append(lines)
    return out


def word_onsets(vo, n, d):
    """Estimated onset (s) of each of the n spoken words over d seconds: weighted
    by letter count plus a pause after punctuation. None if the counts differ."""
    words = vo.split()
    if len(words) != n:
        return None
    weights = []
    for i, w in enumerate(words):
        pause = 0.0
        if i < len(words) - 1:
            pause = 4.0 if w[-1] in ".:?!" else 2.5 if w[-1] in ",;" else 0.0
        weights.append(sum(c.isalnum() for c in w) + 1.5 + pause)
    total, acc, out = sum(weights), 0.0, []
    for w in weights:
        out.append(d * acc / total)
        acc += w
    return out


def layout(name, cfg):
    """TTS every line and derive shots, phrases and VO placement."""
    t, shots, phrases, vo_events, punch, extra = 0.0, [], [], [], [], []
    for li, line in enumerate(cfg["lines"]):
        wav = tts(line["vo"])
        d = duration(wav)
        is_last = li == len(cfg["lines"]) - 1
        span = d + (TAIL if is_last else GAP)
        vo_events.append((wav, t))
        if line.get("sfx"):
            extra.append((line["sfx"], t - 0.05, 0.35))
        n = len(line["shots"])
        for s in line["shots"]:
            shots.append((s, round(span / n, 3)))
        if line.get("cap"):
            screens = chunk_caption(line["cap"])
            nwords = sum(len(ln) for sc in screens for ln in sc)
            per = min(d / max(nwords, 1), 0.33)
            slot = d / len(screens)
            onsets = word_onsets(line["vo"], nwords, d) if cfg.get("sync") else None
            wi = 0
            for si, sc in enumerate(screens):
                count = sum(len(ln) for ln in sc)
                if onsets:
                    at = [round(t + o, 3) for o in onsets[wi:wi + count]]
                    st = t if si == 0 else at[0] - 0.04
                    en = t + onsets[wi + count] - 0.04 if si < len(screens) - 1 else t + span
                else:
                    st = t + si * slot
                    en = t + (si + 1) * slot if si < len(screens) - 1 else t + span
                    at = [round(st + j * per, 3) for j in range(count)]
                ph = {"t": round(st, 3), "end": round(en - 0.02, 3), "lines": sc, "at": at}
                if line.get("plate"):
                    ph["plate"] = True
                phrases.append(ph)
                if line.get("punch") and si == len(screens) - 1:
                    punch.append(at[-1])
                wi += count
        end_t = t
        t += span
    shot_sum = sum(d for _, d in shots)
    comp = {"punch": punch, "phrases": phrases, "sfx": extra,
            "end": {"t": round(end_t, 3), "tag": cfg["tag"], "cta": cfg.get("cta", "PEDILO POR DM")}}
    return comp, shots, vo_events, shot_sum


def mix(name, comp, vo_events, dur):
    out = ROOT / name
    events = []
    shots = json.loads((out / "shots.json").read_text())["shots"]
    for s in shots[1:]:
        events.append(("whoosh", s["start"] - 0.06, 0.16))
    for p in comp["punch"]:
        events.append(("impact", p, 0.45))
    et = comp["end"]["t"]
    events += [("riser", et - 0.8, 0.22), ("impact", et + 0.1, 0.4)]
    events += comp.get("sfx", [])
    # voice replaces the original (ASMR) sound: master = AI voice + edit SFX only
    inputs, chains, vo_labels = [], [], []
    for i, (wav, t) in enumerate(vo_events):
        inputs += ["-i", str(wav)]
        ms = int(round(t * 1000))
        chains.append(f"[{i}]aresample=48000,adelay={ms},volume=1.0[v{i}]")
        vo_labels.append(f"[v{i}]")
    base = len(vo_events)
    sfx_labels = []
    for j, (f, t, vol) in enumerate(events):
        inputs += ["-i", str(SFX / f"{f}.wav")]
        ms = max(0, int(round(t * 1000)))
        chains.append(f"[{base + j}]aresample=48000,adelay={ms}|{ms},volume={vol}[e{j}]")
        sfx_labels.append(f"[e{j}]")
    chains.append("".join(vo_labels) + f"amix=inputs={len(vo_labels)}:normalize=0,"
                  "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                  "loudnorm=I=-15:TP=-2,aresample=48000,aformat=channel_layouts=stereo[vo]")
    fc = ";".join(chains) + ";[vo]" + "".join(sfx_labels) + \
        f"amix=inputs={1 + len(sfx_labels)}:duration=longest:normalize=0,alimiter=limit=0.95," \
        f"apad,atrim=0:{dur},afade=t=out:st={dur - 0.4:.2f}:d=0.4[mix]"
    sh("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[mix]",
       "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(out / "master.m4a"))


def build(name, cfg):
    out = ROOT / name
    if not (out / "index.html").exists():
        sh("hyperframes", "init", name, "--non-interactive", "--example", "blank",
           "--resolution", "portrait", cwd=ROOT, stdin=subprocess.DEVNULL,
           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comp, shots, vo_events, dur = layout(name, cfg)
    build_base.build(name, {"src": cfg["src"], "shots": shots})
    real = json.loads((out / "shots.json").read_text())["duration"]
    build_comp.build(name, comp)
    mix(name, comp, vo_events, real)
    (out / "vo.json").write_text(json.dumps([[str(w), round(t, 3)] for w, t in vo_events], indent=1))
    print(f"{name}: {real:.2f}s, {len(comp['phrases'])} caption screens")


if __name__ == "__main__":
    if not (SFX / "rewind.wav").exists():
        build_audio.make_sfx()
    for name in sys.argv[1:] or VIDEOS:
        build(name, VIDEOS[name])
