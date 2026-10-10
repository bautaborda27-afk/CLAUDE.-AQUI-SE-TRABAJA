# Memoria del proyecto — Savings Hub (savings.hub)

Reels verticales 9:16 para **savings.hub** (perfumes árabes y de diseñador, decants, venta mayorista y a
revendedores). Todo vive en `savinghub/`; el detalle ronda por ronda está en `savinghub/edit-report.md`.

## Estilo (obligatorio)
- Usar SIEMPRE el estilo de la cuenta: `.claude/skills/video-editing/styles/savings-hub/FRAME.md`, con las
  capturas de referencia en `savinghub/referencias/`. Se genera con `savinghub/build_sh.py`.
- **No** usar el estilo "Documental Reel" (Anton gigante rojo/blanco, grano, whips, pixelado): el cliente lo
  rechazó para Saving ("ese no es el estilo de edición de saving"). Las rondas 1–4 quedaron en ese estilo.
- Imagen limpia: `GRAIN=0 ./finalize.sh <dir> <Salida>`. CTA: "ESCRIBINOS · SAVINGS.HUB".

## Voz
- Voz IA local: Kokoro `ef_dora`, velocidad 1.08 (`hyperframes tts`; necesita `pip install kokoro-onnx soundfile`).
- La marca se pronuncia "Séivings Jab" y se escribe "Savings Hub" / "savings.hub".
- Nombres en fonética para el TTS ("Latáfa", "Bajarára", "Jauás", "Yan Pol Goltié", "Vélvet Úd").
- Kokoro usa español de España: C/Z antes de E/I suena θ. Escribir con S ("vasía", "empiesa", "Serramos") y
  revisar fonemas con `kokoro_onnx.tokenizer.Tokenizer().phonemize(texto, "es")`.
- Con voz IA: **sin sonido original ni música**; solo voz + SFX suaves. Un único `master.m4a`.

## Hechos (no inventar)
- No inventar precios, cantidades ni marcas que no se lean en el video; lo dudoso va a "A confirmar".
- El pedido de `source/vid_pedido.mp4` es **mayorista** (confirmado por el cliente).
- "$30.000" sale del título del video del revendedor. Velvet Oud: no se nombra la casa. "Hawas, de Rasasi" y el
  "set de regalo" están sin confirmar. Las cajas con "X" no se nombran. Cargador/cable con logo Apple: no nombrar la marca.

## Material
- Originales en `savinghub/source/`. Para resúmenes usar los originales sin texto, no reels ya editados.
- `revendedor_30000.mp4` y `velvet_oud.mp4` son reels propios con títulos quemados arriba: usar planos con zoom
  (`at(..., zoom, fy=1)` en `build_sh.py`) para dejar los títulos fuera de cuadro.

## Verificación antes de entregar
`hyperframes lint` (0 errores) → snapshots (incluido el cuadro 0) → render → `finalize.sh` →
`verify-render.mjs` (GATE PASS) → `check_vo.py` (L/R ~1, frases en su lugar) → cuadros a mitad de cada plano.

## Entorno
- Si `hyperframes` da "Permission denied" tras un auto-update: `chmod +x /opt/node22/lib/node_modules/hyperframes/bin/hyperframes.mjs`.
- Hugging Face está bloqueado por la red: no hay transcripción con Whisper.
- Al esperar procesos, no usar `pgrep -f` con un texto que también aparezca en el propio comando (se encuentra a sí mismo).
