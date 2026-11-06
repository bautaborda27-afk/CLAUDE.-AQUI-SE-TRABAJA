# CN PROD — BACKSTAGE SOLD OUT (flyer con efectos)

El flyer original animado como historia vertical (1080×1920, 30 fps, 9 s).

- `source/flyer-original.png`: el flyer que se mandó.
- `output/CNPROD_Backstage_SoldOut_FX.mp4`: versión final con efectos de sonido (-16 LUFS).
- `output/CNPROD_Backstage_SoldOut_FX_sin-audio.mp4`: la misma, muda, para poner música en Instagram.
- `output/CNPROD_Backstage_SoldOut_FX_still.png`: último cuadro como imagen fija.

## Qué pasa en el video

| Tiempo | Efecto |
| --- | --- |
| 0.0–0.85 s | El plano se escanea de arriba hacia abajo con una línea de luz; la cámara se abre desde un encuadre cerrado. |
| 0.4–1.0 s | BACKSTAGE se escribe a mano de izquierda a derecha (barrido inclinado + desenfoque de tinta). |
| 1.2–1.45 s | SOLD OUT cae como un sello: viene grande y girado, con su sombra cerrándose debajo. |
| 1.45 s | Impacto: flash, temblor de pantalla, separación RGB, onda expansiva y salpicaduras de tinta roja. |
| 1.9 s | El cartel EXIT se prende como neón rojo, titilando (vuelve a titilar en 4.6 y 7.25 s). |
| 2.0–7.6 s | Destellos en las estrellas del dibujo, brillo que recorre SOLD OUT (2.55 y 7.0 s) y BACKSTAGE (5.2 s). |
| 3.9 / 6.15 / 8.05 s | Glitch digital sobre SOLD OUT (cortes horizontales + aberración cromática). |
| 4.85–5.45 s | Los puntos 1-2-3-4 del escenario disparan anillos de luz, uno por golpe de bombo. |
| todo | Grano de película, parpadeo de proyector, luz cálida que se desplaza y viñeta suave. |

## Regenerar

```sh
pip install opencv-python-headless scipy pillow numpy
python3 build_layers.py   # separa el flyer en capas -> fx/assets/*.png
python3 build_sfx.py      # sintetiza los efectos de sonido -> fx/assets/sfx.wav
(cd fx && npx hyperframes render --quality delivery -o ../output/raw.mp4)
```

Encode final: `libx264 -crf 18 -maxrate 14M`, audio `loudnorm I=-14 TP=-1.5`, AAC 192k.
La animación está en `fx/compositions/flyer.html` (GSAP; todos los tiempos en segundos).
