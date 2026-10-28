# Review — placa dibujándose

## Decisiones
- Concepto: time-lapse de un boceto de arquitecto sobre la misma hoja. Nada se
  "aparece" con fundido: cada trazo crece a lo largo de sí mismo (líneas y círculos
  recorridos con distancia geodésica sobre la tinta), los textos se escriben de
  izquierda a derecha, MESAS y SOLD OUT se dibujan letra por letra (contorno primero,
  después el rayado trazo por trazo en la dirección del sombreado original).
- Orden: marco y arcos (0–1 s) → tramas de las esquinas → plano y mesas (0,8–2,8 s)
  → CN PROD / EXIT / textos → guías y MESAS (2,5–4,8 s) → guías rojas y SOLD OUT
  (4,4–6,2 s) → logos (6–6,9 s) → acuarelas (6,3–7,6 s) → placa completa hasta 10 s.
- Tinta fresca un poco más oscura en el borde que avanza (efecto "tinta húmeda").
- Cámara: alejamiento lento de 1,045 a 1,0 que se asienta en la placa entera a los 7,9 s.
- Sin audio: es una historia de 10 s y en Instagram se suele sumar la música en la app.

## Medido
- `hyperframes check`: OK. Advertencia `canvas_content_at_edge` aceptada: la placa
  es a sangre (tramas y marco tocan el borde por diseño).
- Último cuadro vs. placa original: diferencia media 1,5/255 (solo compresión JPEG).
- Render: h264, 1080×1920, 30 fps, 300 cuadros, 10,0 s, 17,5 MB.

## Lo más débil
- La división entre la "L" y la "D" de SOLD es una línea recta: el pie de la L se
  completa junto con la D. Con más tiempo, máscaras de letra a mano.
- Manchas de tinta sueltas aparecen ~0,1–0,3 s después del trazo más cercano; algunas
  pueden verse "saltar" en lugar de salpicar.
