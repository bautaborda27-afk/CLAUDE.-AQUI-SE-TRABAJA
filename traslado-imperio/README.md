# Traslado — Victoria Whynot · Imperio (CN Prod.)

Historia vertical (1080×1920, 30 fps, 10 s) hecha a partir de la placa estática
`source/placa-traslado.png`: la placa se arma sola elemento por elemento, el
colectivo entra desde la izquierda, frena y queda en su lugar, y el video
termina en la placa original quieta (~3 s).

- `output/Traslado_VictoriaWhynot_Imperio.mp4` — video final.
- `edit/` — proyecto HyperFrames (`index.html` + `assets/` con las capas).
- `REVIEW.md` — decisiones y revisión.

## Regenerar

```sh
pip install opencv-python-headless
python3 build_plate.py    # placa 1080x1920, máscara de tinta, papel limpio
python3 build_layers.py   # recorta cada elemento como capa -> edit/assets/
python3 build_comp.py     # animación -> edit/index.html
mkdir -p edit/vendor && cp "$HYPERFRAMES_GSAP_JS" edit/vendor/gsap.min.js
(cd edit && hyperframes render --quality delivery -o renders/traslado.mp4)
```

El contorno del colectivo está en `bus_poly.json` (puntos sobre la placa a 1080×1920).
