# CN PROD — BACKSTAGE SOLD OUT (flyer animado, minimalista)

El flyer original animado como historia vertical (1080×1920, 30 fps, 7 s).

- `source/flyer-original.png`: el flyer que se mandó.
- `output/CNPROD_Backstage_SoldOut_Minimal.mp4`: versión final, con dos sonidos suaves (-14,6 LUFS).
- `output/CNPROD_Backstage_SoldOut_Minimal_sin-audio.mp4`: la misma, muda, para poner música en Instagram.
- `output/CNPROD_Backstage_SoldOut_Minimal_still.png`: último cuadro como imagen fija.
- `output/v1-efectos/`: la primera versión, cargada de efectos (glitch, neón, salpicaduras, grano).

## Qué pasa en el video

| Tiempo | Movimiento |
| --- | --- |
| 0–1.3 s | El plano ya está; la página se acomoda apenas (zoom 1.03 → 1). |
| 0.25–1.05 s | BACKSTAGE aparece con un solo barrido limpio, de izquierda a derecha. |
| 1.3–1.5 s | SOLD OUT se apoya como un sello: baja de 1.14 a 1 con un giro mínimo, sin rebote. |
| 1.5–7 s | El flyer queda quieto. |

Sonido: un trazo de lápiz suave bajo BACKSTAGE y un golpe seco de sello. Nada más.

## Regenerar

```sh
pip install opencv-python-headless scipy pillow numpy
python3 build_layers.py   # separa el flyer en capas -> fx/assets/{plan,backstage,soldout}.png
python3 build_sfx.py      # sintetiza los dos sonidos -> fx/assets/sfx.wav
(cd fx && npx hyperframes render --quality delivery -o ../output/raw.mp4)
```

Encode final: `libx264 -crf 18 -maxrate 14M`, audio `loudnorm I=-14 TP=-1.5`, AAC 192k.
La animación está en `fx/compositions/flyer.html` (GSAP; todos los tiempos en segundos).
La v1 con efectos está en el historial de git (commit `b418d2e`).
