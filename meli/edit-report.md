# Informe de edición — Meli: "Inglés desde CERO"

**Estado:** listo para revisar
**Salida:** `output/Meli_InglesDesdeCero.mp4`: 1080×1920, 36,1 s, h264/yuv420p, 30 fps, AAC 48 kHz, -14,1 LUFS integrado
**Estilo:** el del video de referencia de @ingleswithjuli (reel educativo hablado a cámara)

## Estilo tomado de la referencia
| Recurso de la referencia | Cómo quedó acá |
|---|---|
| Cartel blanco redondeado arriba a la izquierda como portada | "Inglés desde CERO / ¿Se puede?" (0–1 s) |
| Subtítulos en español palabra por palabra, blancos con borde negro, arriba | Poppins 800, grupos de 1 a 3 palabras, cada palabra aparece cuando se dice |
| Frase en inglés en crema con borde oscuro y significado en blanco abajo | "Start from zero", "Real English" |
| Ejemplos entre comillas con la palabra clave en crema y la traducción abajo | "My name is __", "I'm __ years old", "I love coffee" |
| Traducción literal equivocada en rojo con la imagen en blanco y negro | El mito ("pareciera que tiene que saber un montón") y "reglas sin sentido" |
| Título grande al centro con zoom a la cara | "¡Bueno, NO!" y "Escribí CERO" |
| Emojis que aparecen de golpe | 😩 ☕ 🤝 🤯 ✅ 💬 👋 |
| Destello blanco diagonal en los cambios de toma | Al pasar del clip 2 al 3 y del 3 al 1 |

## Decisiones plano por plano
| Tiempo | Clip (seg. de origen) | Qué se ve | Cámara | Sonidos |
|---|---|---|---|---|
| 0–2,1 | 2 (0,70–2,82) | Cartel de portada; después subtítulos | 1,00→1,05 | pop |
| 2,1–5,3 | 2 (3,02–6,20) | **Blanco y negro**, subtítulos rojos, 😩 | 1,12→1,17 | swish, pop |
| 5,3–6,2 | 2 (6,62–7,52) | "¡Bueno," → "NO!" grande en crema | zoom a 1,30 en "no" | thock ×2 |
| 6,2–11,4 | 2 (7,92–13,12) | Subtítulos → tarjeta "Start from zero" | 1,10→1,03 | pop |
| 11,4 | cambio de clip | destello diagonal | — | whoosh |
| 11,4–16,0 | 3 (0,82–5,40) | Subtítulos → "My name is __" | 1,00→1,06 | pop |
| 16,0–22,4 | 3 (5,70–12,10) | "I'm __ years old", "I love coffee" ☕, 🤝, luego **blanco y negro** + 🤯 | 1,12 → zoom a 1,00 en "Obvio" → 1,18 en "reglas" | pops, swish |
| 22,4–29,4 | 3 (cinco cortes de pausas) | "sin sentido" → tarjeta "Real English" ✅ | zoom alternado 1,0/1,12 en cada corte | pop |
| 29,4 | cambio de clip | destello diagonal | — | whoosh |
| 29,4–35,2 | 1 (0,70–6,48) | Subtítulos → "Escribí CERO" grande + 💬 | zoom a 1,27 en "escribí" | thock ×2, pop |
| 35,2–36,0 | 1 (7,08–7,91) | "Bye!" en crema + 👋 | 1,14→1,18 | pop |

Se cortaron las pausas de más de ~0,35 s (de 41,7 s de material a 36,0 s). En cada corte cambia el nivel de zoom, para que el salto se lea como un acercamiento y no como un error.

## Material y procedencia
- Video: los 3 clips del usuario. El original en HEVC `.mov` se convirtió a H.264 en `source/`.
- Transcripción: análisis de video de Higgsfield, hecho en la cuenta del usuario con su autorización. Los tiempos se alinearon a las pausas del audio (`align_words.py`). Texto completo en `data/transcript.md`.
- Tipografías: Poppins 500/700/800/900 (SIL OFL, paquete npm `@fontsource/poppins`).
- Emojis: Noto Color Emoji (SIL OFL), recortado a los 7 que se usan.
- Sonidos: todos sintetizados con ffmpeg (whoosh, pop, click, thock, swish); no tienen derechos de autor.
- Música: ninguna.

## Audio
Voz: highpass 85 Hz, reducción de ruido suave (afftdn), compresión 3:1 y limitador. Los sonidos van mezclados por debajo de la voz en una sola pista (`edit/master.m4a`). La normalización final a -14 LUFS se hace en `finalize.sh`.

## Para revisar antes de publicar
- **Tiempos de los subtítulos:** salen de la transcripción y de las pausas del audio, no de un reconocimiento de voz palabra por palabra. Pueden correrse unos ±0,15 s; conviene verlos con el audio.
- **Las tarjetas en inglés son agregados de edición**, no cosas que ella dice textualmente: "Start from zero", los tres ejemplos y "Real English". Los ejemplos de nombre y edad llevan una raya en blanco a propósito, para no inventar datos.
- **El CTA "Escribí CERO"** no dice dónde (comentarios o DM) porque ella tampoco lo dice.

## Cómo regenerar
```sh
python3 align_words.py          # tiempos de cada palabra -> data/words.json
python3 build.py                # base.mp4 + master.m4a + index.html
(cd edit && hyperframes render -o renders/meli.mp4 -f 30)
./finalize.sh                   # -14 LUFS + verificación + hoja de capturas
```

## Verificación
- Lint de HyperFrames: 0 errores. Hay 51 avisos de estructura y densidad (sugiere separar en subcomposiciones); no hacen falta para un reel corto.
- Capturas de vista previa en 16 momentos clave. Detecté y corregí un subtítulo rojo que se pisaba con "¡Bueno, NO!".
- Verificación final (`verify-render.mjs`): PASA. 1080×1920, h264, yuv420p, AAC, 36,10 s.
- Volumen: -14,1 LUFS integrado, LRA 2,5 LU.
- Cuadros revisados del video final: portada, blanco y negro, títulos grandes, tarjetas, ejemplos, destellos y "Escribí CERO". La cara queda entera en todos los cuadros.
