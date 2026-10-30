# Review — Traslado (Victoria Whynot · Imperio)

## Qué se hizo

La placa se separó en 39 capas (texto, estrellas, pines, carteles, flechas, óvalo,
ruta, líneas de velocidad, colectivo, logos) sobre un fondo de papel sin tinta.
Cada capa es un recorte RGBA "desmezclado" contra ese papel, así que todas juntas
devuelven la placa. La ruta que tapa el colectivo se reconstruyó (`build_road.py`):
el guardarraíl se continúa a lo largo de su línea, el asfalto se rellena con
parches reales de la ruta (tono suavizado aparte para que no queden bloques) y
los árboles de la derecha crecen una copa hacia el hueco. A los 7,85 s el video
pasa a la placa original (`assets/poster.png`) con un fundido invisible.

| Tiempo | Qué pasa |
| --- | --- |
| 0–0,85 s | marco y rayado de los bordes entran en diagonal |
| 0,15–1,45 s | logo CN Prod., VICTORIA / WHYNOT (barridos opuestos), SAB 07 NOV — IMPERIO |
| 1,15–2,55 s | TRASLADO letra por letra (sello), el óvalo se dibuja alrededor, estrellas |
| 2,25–4,2 s | pines con rebote, carteles, flechas hacia San Francisco, rayos |
| 2,9–4,0 s | la ruta vacía se dibuja de izquierda a derecha |
| 3,7–4,65 s | línea inferior, estrellas y sponsors: la placa completa, sin colectivo |
| **4,3–7,7 s** | **el colectivo aparece en el fondo de la ruta (detrás del marco, a la izquierda), viene por la ruta creciendo en perspectiva (escala desde el punto de fuga), frena, cabecea y queda; las líneas de velocidad aparecen detrás mientras va más rápido** |
| 7,85–11 s | placa original estática |

## Medido / mirado

- `hyperframes check`: sin errores. Aviso informativo `canvas_covered` sobre
  `#plate`: falso, se comprobó que la placa final se pinta encima.
- Último cuadro del MP4 vs. placa: diferencia media 1,9/255 (solo compresión).
- Cuadros revisados: ruta vacía (4,6 s), recorrido del colectivo (4,6–7,6 s), corte a la placa.
- Sin sonido (para poner la música en Instagram).

## Lo más débil

- La ruta reconstruida bajo el colectivo: a tamaño celular se lee como asfalto
  con sombra, pero a tamaño completo el centro queda algo más liso que el resto.
- El cuadro 0 es solo papel (el marco entra enseguida).
