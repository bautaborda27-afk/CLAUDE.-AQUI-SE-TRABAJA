# CN PROD — MESAS SOLD OUT · placa dibujándose

Historia vertical (1080×1920, 10 s, 30 fps, sin audio) en la que la placa
"MESAS SOLD OUT" se dibuja sola sobre el papel: primero el marco y las líneas de
construcción, después el plano (escenario, cabina, mesas 1–4, sectores), los textos,
MESAS letra por letra (contorno y luego el rayado), SOLD OUT en rojo, los logos y al
final las manchas de acuarela. Termina exactamente en la placa original y la
sostiene ~2,5 s.

- `output/CNPROD_Mesas_SoldOut_dibujo.mp4` — video final para publicar.
- `source-placa.png` — la placa original.
- `build/build_assets.py` — separa la tinta del papel y calcula, píxel por píxel,
  en qué momento se dibuja cada trazo. El orden y los tiempos de cada elemento
  están al final del script (sección `timeline`).
- `assets/` — capas generadas: `placa.jpg` (final), `papel.jpg` (hoja en blanco),
  `violeta.jpg` (capa violeta bajo el rojo), `tiempo*.png` y `mascara.png`
  (mapas de tiempo, sin pérdida).
- `compositions/dibujo.html` — pinta cada cuadro en un canvas a partir de esas
  capas; `index.html` es la composición raíz.

## Regenerar

```sh
pip install numpy scipy scikit-image pillow
python3 build/build_assets.py source-placa.png assets
npx hyperframes render -q delivery -o output/CNPROD_Mesas_SoldOut_dibujo.mp4
```

Para cambiar el ritmo general sin tocar el orden, editar los segundos en
`build/build_assets.py` y volver a correrlo; la duración total del video está en
`data-duration` de `index.html` y `compositions/dibujo.html` (`DUR`).
