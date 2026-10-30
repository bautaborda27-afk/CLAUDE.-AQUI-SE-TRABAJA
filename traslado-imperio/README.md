# Traslado — Victoria Whynot · Imperio (CN Prod.)

Historia vertical (1080×1920, 30 fps, 11 s) hecha a partir de la placa estática
`source/placa-traslado.png`: primero se dibuja toda la placa, ruta vacía
incluida; después el colectivo viene por la ruta desde el fondo, frena y queda
en su lugar, y el video termina en la placa original quieta (~3 s).

- `output/Traslado_VictoriaWhynot_Imperio.mp4` — video final.
- `edit/` — proyecto HyperFrames (`index.html` + `assets/` con las capas).
- `REVIEW.md` — decisiones y revisión.

## Regenerar

```sh
pip install opencv-contrib-python-headless
python3 build_plate.py    # placa 1080x1920, máscara de tinta, papel limpio
python3 build_road.py     # reconstruye la ruta vacía debajo del colectivo
python3 build_layers.py   # recorta cada elemento como capa -> edit/assets/
python3 build_comp.py     # animación -> edit/index.html
mkdir -p edit/vendor && cp "$HYPERFRAMES_GSAP_JS" edit/vendor/gsap.min.js
(cd edit && hyperframes render --quality delivery -o renders/traslado.mp4)
```

El contorno del colectivo está en `bus_poly.json` (puntos sobre la placa a 1080×1920).
