# Cortometraje — transiciones y efectos

Corto en blanco y negro (4:16, 16:9) con transiciones, efectos de cámara, glitch,
textos animados y diseño sonoro agregados. El montaje y la música originales se
respetan; todo se monta sobre los 13 cortes del film.

- `source/corto_original.mp4` — video original.
- `output/Corto_Transiciones_Efectos.mp4` — versión final (1920x1080, 30 fps).
- `edit-report.md` — qué se hizo en cada corte y cómo se verificó.

## Regenerar

```sh
python3 build_base.py     # 1080p base + stills de los whips   -> edit/base.mp4
python3 build_audio.py    # SFX sintetizados + música original -> work/master.m4a
python3 fx_film.py        # capa de imagen (cámara, glitch, flashes, grade) -> work/film_fx.mp4
python3 build_comp.py     # capa gráfica HyperFrames (textos, FIN) -> edit/
(cd edit && for c in note-1 note-2 fin; do \
  npx hyperframes render -c compositions/$c.html --format png-sequence -o ../work/overlay/$c; done)
./finalize.sh             # composición + grano + audio + verificación -> output/
```

Los tiempos de todo (cortes, transiciones, golpes, textos) están en `plan.py`.
