# Review — Traslado (Victoria Whynot · Imperio)

## Qué se hizo

La placa se separó en 38 capas (texto, estrellas, pines, carteles, flechas, óvalo,
ruta, colectivo, logos) sobre un fondo de papel sin tinta. Cada capa es un recorte
RGBA "desmezclado" contra ese papel, así que todas juntas devuelven la placa tal
cual. A los 6,85 s el video pasa a la placa original (`assets/poster.png`) con un
fundido invisible, y queda quieta hasta los 10 s.

| Tiempo | Qué pasa |
| --- | --- |
| 0–0,85 s | marco y rayado de los bordes entran en diagonal |
| 0,15–1,45 s | logo CN Prod., VICTORIA / WHYNOT (barridos opuestos), SAB 07 NOV — IMPERIO |
| 1,15–2,55 s | TRASLADO letra por letra (sello), el óvalo se dibuja alrededor, estrellas |
| 2,25–4,2 s | pines caen con rebote, carteles se despliegan, flechas se dibujan hacia San Francisco, rayos |
| **3,55–6,3 s** | **el colectivo entra desde la izquierda con desenfoque de movimiento y traqueteo, frena (power3.out, 2,1 s), cabecea al frenar y se asienta; la ruta se dibuja detrás de él y los árboles de la derecha al frenar** |
| 5,8–6,65 s | estrella, línea inferior y logos de sponsors |
| 6,85–10 s | placa original estática |

## Decisiones

- La ruta se dibuja detrás del colectivo (no está antes): así nunca se ve el hueco
  donde estaba el colectivo en la placa, y encaja con el estilo boceto.
- El colectivo pasa por detrás del cartel de Sunchales (queda debajo en el orden de capas).
- Sin sonido: es una historia corta y la música se suele poner en la app. Si se
  quiere un tema, se agrega al `index.html` como `<audio>`.

## Medido / mirado

- `hyperframes check`: sin errores. Queda un aviso informativo `canvas_covered`
  sobre `#plate` que es falso: se comprobó que la placa final se pinta encima.
- Recomposición de capas vs. placa: idéntica salvo un anillo de 2–3 px alrededor
  del colectivo (relleno del hueco), cubierto por el pase a la placa original.
- Último cuadro del MP4 vs. placa: diferencia media 1,9/255 (solo compresión).
- Cuadros revisados: entrada (3,62–4,2 s), frenado (5,6–6,0 s), corte a la placa.

## Lo más débil

- Los primeros cuadros del colectivo pasan sobre papel vacío (la ruta todavía no
  está). Con más tiempo: reconstruir la ruta completa bajo el colectivo para que
  pueda llegar por una ruta ya dibujada.
- El cuadro 0 es solo papel (el marco entra enseguida).
