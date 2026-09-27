# Saving Hub — reels

Reels verticales (9:16) para Saving Hub, estilo "Documental Reel".

- `source/` — videos originales (unboxings).
- `output/` — reels finales listos para publicar.
- `edit-report.md` — decisiones de edición plano por plano.

## Regenerar

```sh
python3 build_base.py    # corta planos -> edit-*/base.mp4
python3 build_audio.py   # SFX + ASMR -> edit-*/master.m4a
python3 build_comp.py    # textos/animación -> edit-*/index.html
(cd edit-jeanlowe && hyperframes render)   # idem edit-bharara
```

El paso final (grano + loudness -14 LUFS) está documentado en `edit-report.md`.
