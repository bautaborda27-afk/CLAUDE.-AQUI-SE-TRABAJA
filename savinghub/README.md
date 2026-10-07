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

Reels con voz IA (rondas 2 y 4; requiere `pip install kokoro-onnx soundfile`):

```sh
python3 build_vo.py edit-v4-pedido          # voz + cortes + textos + master.m4a
(cd edit-v4-pedido && hyperframes render)
./finalize.sh edit-v4-pedido SavingHub_V4_PedidoMayorista_VozIA   # grano + -14 LUFS + gate
```

El paso final (grano + loudness -14 LUFS) está documentado en `edit-report.md`.
