# Saving Hub — reels

Reels verticales (9:16) para savings.hub.

**Estilo de la marca:** el de la cuenta (capturas en `referencias/`, tokens en
`.claude/skills/video-editing/styles/savings-hub/FRAME.md`): grilla oscura con el video en tarjeta,
subtítulos en barras con palabra clave dorada, pill bordó en la costura del split y cierre en papel con
"ESCRIBINOS · SAVINGS.HUB". Se genera con `build_sh.py`. Los reels de las rondas 1–4 usan el estilo
"Documental Reel" (Anton rojo/blanco), que **no** es el de la marca.

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

Estilo Savings Hub (ronda 5 en adelante):

```sh
python3 build_sh.py edit-v5-caja-sh         # voz + base.mp4/base_b.mp4 + index.html + master.m4a
(cd edit-v5-caja-sh && hyperframes render)
GRAIN=0 ./finalize.sh edit-v5-caja-sh SavingsHub_V5_CajaDePerfumes_VozIA   # sin grano, -14 LUFS, gate
```

El paso final (grano + loudness -14 LUFS) está documentado en `edit-report.md`.
