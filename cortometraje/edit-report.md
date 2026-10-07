# Edit report — Cortometraje: transiciones y efectos

**Disposition:** in_review (esperando feedback)
**Output:** `output/Corto_Transiciones_Efectos.mp4` — 1920x1080, 258.5 s, h264/yuv420p 30 fps, AAC 192k, -14.9 LUFS (true peak -1.1 dBFS), 94 MB
**Estilo:** "Documental Reel" del usuario (Anton, blanco + palabra clave en rojo #E0201B, grano, whips/zooms con motion blur, flashes, pixelado→nítido) adaptado a un corto de suspenso en B/N y 16:9.

## Material
- `source/corto_original.mp4` — 1024x576, 30 fps, 256 s, blanco y negro. Sin diálogos (VAD Silero: 0 s de voz); el audio es la música del corto.
- 13 cortes detectados con `scdet` y revisados cuadro a cuadro (el de 182.63 s es un jump cut dentro del plano de la nota "YA TE ENCONTRÉ"; un falso positivo en 172.3 s se descartó).

## Corte por corte
| ts | Plano | Transición / efecto | SFX |
|----|-------|---------------------|-----|
| 0.0 | pasillo | apertura "ojos": barras negras se abren, pixelado→nítido (steps), fade-up de exposición | swell + impacto |
| 25.77 | pasillo → aula | zoom-through (1→1.4→1) + blur + flash blanco suave | whoosh |
| 51.9 | aula (golpe de la música) | punch-in 1→1.07, vuelve en 1.4 s | — (ya está en la música) |
| 75.17 | aula → primer plano del protagonista | blur flash + pixelado→nítido | whoosh, click |
| 97.4–100.9 | la nota | fondo oscurecido + desenfocado; texto palabra por palabra **TE BUSQUÉ / POR MUCHO / TIEMPO** (rojo, golpe + tinte rojo + sacudida) | clicks, riser, impacto |
| 104.0 | primeros planos → lee la nota | whip pan a la izquierda con motion blur direccional (el plano siguiente entra pegado) | whip |
| 117.63 | nota → plano general del banco | flash de exposición (sobreexpuesto a blanco) | shimmer, whoosh |
| 143.3 | banco → banco vacío (salto de tiempo) | glitch digital (cortes de línea, RGB split, bloques, stutter) + 2 cuadros negros | glitch, impacto |
| 157.73 | pasa el acosador → cara | dip a oscuro + punch-in desde 1.18 | whoosh, impacto |
| 174.4–179.05 | antes del baño | 7 latidos: viñeta que late + micro-zoom | latidos (lub-dub) |
| 179.2–182.63 | la nota del baño | texto **¡YA TE / ENCONTRÉ!** (rojo, golpe), tinte rojo, glitch, sacudida de cámara | clicks, impacto, glitch |
| 182.63 | jump cut | slam: punch-in 1.16→1 + tinte rojo + glitch + sacudida | impacto, glitch |
| 187.57 | cabeza → cara | whip pan a la derecha | whip |
| 198.43 | cara → lavatorios | zoom-through | whoosh |
| 215.87 | aparece el acosador | glitch fuerte + 2 cuadros negros + tinte rojo + sacudida | glitch, impacto |
| 222.0 | entra la música de persecución | punch-in 1.1 + flash blanco + tinte rojo + sacudida fuerte | impacto, glitch |
| 229.87 | enfrentamiento → huye | whip pan a la izquierda; desde acá cámara en mano suave (persecución) | whip |
| 241.07 | → escaleras | whip vertical (hacia arriba) | whip |
| 248.83 | → pasillo largo | zoom-through + flash | whoosh, impacto |
| 255.45–256.0 | final | glitch + barras se cierran ("ojos se cierran") | glitch, boom con cola |
| 256.0–258.5 | cartel | **FIN** (blur→nítido, línea roja), fundido a negro | click |

Además, en todo el corto: grade B/N con más contraste y negros más profundos, viñeta, letterbox 2:1 (barras de 60 px), grano de film (pase final, también sobre los textos), polvo y rayas de película deterministas, y un push lento (Ken Burns) en cada plano hacia el sujeto.

## Audio
- Música original del corto (+5 dB), con fade de 0.35 s al cerrar las barras.
- 45 SFX sintetizados con ffmpeg (rights-free): whoosh, whip, impacto, boom, glitch, click, riser, shimmer, swell, latido. Cada uno se nivela contra la música que tiene alrededor (`work/sfx_log.txt`).
- Un único `work/master.m4a`, loudnorm 2 pasadas a -14 LUFS + limitador.

## Design decisions
- **Se mantuvo 16:9.** Es un corto horizontal; pasarlo a 9:16 recortaría a los personajes en casi todos los planos. Si se quiere una versión para Reels/TikTok se puede hacer aparte.
- **No se re-editó el corto**: se respetan los cortes, la duración y la música originales; los efectos van sobre ellos (+2.5 s de cartel FIN).
- **Pipeline híbrido (desvío del workflow estándar).** En esta máquina sin GPU, HyperFrames captura cada cuadro con video en ~15–20 s (Chrome + SwiftShader), o sea ~40 h para el corto; el tratamiento canónico (`data-color-grading`) además depende de WebGL. Por eso:
  - todo lo que toca los píxeles del metraje (cámara, whips, glitch, blur, pixelado, flashes, grade, polvo, barras) está en `fx_film.py` (OpenCV, determinista, ~23 fps), con curvas de easing GSAP y tiempos de `plan.py`;
  - HyperFrames renderiza la capa gráfica (textos y FIN) como sub-composiciones transparentes (`edit/compositions/*.html`, PNG RGBA) que `finalize.sh` monta en su tiempo exacto.
- Solo se animaron las dos notas legibles. La tercera (lavatorio, ~205 s) no se lee bien, así que no lleva texto.
- No se agregó título al principio porque no sé cómo se llama el corto.

## Verification
- Capa de imagen: contact sheet de 36 cuadros en todos los momentos de transición (apertura, zooms, whips con el plano vecino entrando, flash, glitch, dip, latidos, tintes rojos, cierre). Todo en estilo y con el sujeto en cuadro.
- Capa gráfica: `hyperframes lint` 0 errores / 0 warnings; snapshots de las tres sub-composiciones (Anton cargada, acentos y ¡! correctos).
- Final: textos revisados sobre el video (97.8–100.8 s, 179.4–182.55 s, FIN); SFX caen en el cuadro del corte (medido en el audio final: picos en 98.9, 179.95, 182.63, 215.87, 256.0 s).
- `verify-render.mjs --width 1920 --height 1080 --duration 258.5`: **GATE PASS** (1920x1080, h264, yuv420p, audio aac, 258.50 s).
- Contact sheet del final: `work/Corto_Transiciones_Efectos_sheet.jpg`.

## Rights flags
- Música: la del video original del usuario.
- SFX: sintetizados (sin licencia que gestionar). Fuente Anton: OFL.

## Gaps / next steps
- Si me pasan el título del corto, agrego un cartel de título al inicio (después de la apertura de barras).
- Versión 9:16 para redes, si hace falta.
- Si alguna transición se siente demasiado (glitch, tintes rojos), se ajusta en `plan.py` / `fx_tracks.py` y se re-renderiza en ~25 min.
