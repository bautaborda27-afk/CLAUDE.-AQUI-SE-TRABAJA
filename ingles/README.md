# Reels de inglés — estilo "Inglés Reel"

Reels verticales (9:16) de clase de inglés a cámara, editados con el estilo guardado en
`.claude/skills/video-editing/styles/ingles-reel/FRAME.md`. Ese estilo se sacó de un reel de referencia
de una profe de inglés para hispanohablantes. Sus firmas: jump cuts sin pausas, punch-ins en cada corte,
Poppins con contorno negro, la expresión en inglés en crema, el chiste del error en blanco y negro con la voz apagada,
y la transición con una línea blanca.

```
ingles/
├── source/                 videos crudos (WhatsApp / celular)
├── build_reel.py           reel.json -> base.mp4 + master.wav + index.html (HyperFrames)
├── finalize.sh             render + master -> output/<nombre>.mp4 (-14 LUFS, verificado)
├── tools/asr.py            transcripción offline (sherpa-onnx, Parakeet v3 es/en) para cortar y sincronizar
├── output/                 reels finales
└── reel-no-te-soporto/     reel #1: "¿Cómo se dice 'no te soporto' en inglés?"
    ├── reel.json           cortes + encuadres + textos (la única fuente que se edita a mano)
    └── edit-report.md      decisiones de edición
```

## Hacer un reel nuevo

1. Copiar los clips a `source/` y crear la carpeta del reel: `hyperframes init <reel> --example blank --resolution portrait --non-interactive`.
2. **Ver qué dice y dónde están las pausas:** `python3 tools/asr.py segments source/<clip>.mp4`.
   Elegir los tramos a conservar: sacar pausas, "eh/um/okay", tomas repetidas (queda la última buena).
3. Escribir `cuts` en `<reel>/reel.json` → `[fuente, in, out, zoom, push]`. Alternar el zoom entre cortes
   (1.00 / 1.10 / 1.20 en la keyword) y poner `push` 0.03–0.04 en los planos largos.
4. **Tiempos por palabra de cada corte:** `python3 tools/asr.py words <reel>` y armar los `beats` con esos tiempos.
5. `python3 build_reel.py <reel>` → `cd <reel> && npx hyperframes check && npx hyperframes snapshot --at ...`
   (revisar que el texto no tape la cara y quede entre el 14 % y el 65 % de la altura).
6. `cd <reel> && npx hyperframes render` → `./finalize.sh <reel>` → `output/<output>.mp4`.

## reel.json

Los tiempos `T` son segundos de salida (número) o `"FUENTE:segundos"` en el clip original (se mapean solos a
través de los cortes). Así, si se cambia un corte, los textos lo siguen.

| campo | qué es |
|---|---|
| `sources` | `{"B": "source/clip.mp4"}` |
| `cuts` | `[fuente, in, out, zoom, push]`, en orden |
| `punch` | `{"at": T, "scale": s, "push": p}` cambio seco de encuadre dentro de un corte |
| `bw` | `[[T, T]]` blanco y negro + voz apagada (el gag del error común) |
| `transitions` | `[T]` línea blanca + blur + click (antes de cada ejemplo) |
| `face_origin` / `band_top` | origen del zoom (la cara) y altura de la banda de texto en cqh |

Beats (`type`):

- `title` `{from, to, l1, l2}`: tarjeta blanca del hook ("¡Frase!" / "In English").
- `big` `{from, to, lines, span}`: frase gigante letra por letra.
- `caption` `{to, words:[[texto, T, acento?]...]}`: subtítulo palabra por palabra (`"\n"` = salto de línea).
- `wrong` `{from, to, text, strike}`: traducción incorrecta en rojo, tachada con ❌ en `strike`.
- `keyword` `{from, to, text, meaning | meaning_lines + meaning_at}`: expresión en crema + significado.
- `example` `{to, en, es, size?, emoji?, emoji_at?}`: par “EN” / “ES” palabra por palabra (acento = crema).
- `sticker` `{to, seq:[[emoji, T]...], grow?, pos?}`: emoji grande; varios en `seq` = escalada (😠→😡→🤬).
  Emojis disponibles en `styles/ingles-reel/stickers/`.

Requisitos: ffmpeg, HyperFrames (`npm i -g hyperframes`), `pip install sherpa-onnx numpy`. El modelo de
transcripción se baja solo de GitHub (sherpa-onnx releases) la primera vez.
