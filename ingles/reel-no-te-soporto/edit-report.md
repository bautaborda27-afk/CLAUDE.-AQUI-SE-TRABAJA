# Edit report — "¿Cómo se dice 'no te soporto' en inglés?"

**Disposition:** in_review (esperando feedback)
**Output:** `output/Ingles_NoTeSoporto.mp4`: 1080x1920, 30 fps, h264/yuv420p, AAC 48 kHz, −14 LUFS, 44,7 s
**Style:** `ingles-reel` (`.claude/skills/video-editing/styles/ingles-reel/FRAME.md`)

## Material
- `source/VID-20261117-WA0088.mp4` (49,6 s, 576x1024): cuerpo completo del guion. Termina cortado en
  "si querés aprender más de un inglés real y útil…".
- `source/VID-20261117-WA0089.mp4` (12,7 s): retoma del cierre/CTA, completa ("…escribime y te cuento cómo son mis clases. Bye.").
- Los dos clips están grabados desde abajo y la cara ocupa el tercio superior, así que los textos van en la
  banda del cuello/pecho (49–65cqh) y no arriba como en la referencia.

## Cortes (20 jump cuts, 94,2 s de material → 44,7 s)
Se quitaron todas las pausas mayores a ~0,25 s, más:
- "Por ejemplo," suelto antes de "es cuando vos no soportás hacer algo" (B 13,85–14,38).
- "okay"/respiración antes del ejemplo 1 (B 17,6–18,2).
- "eh/um" antes de "This noise…" (B 34,6–35,6).
- El final de WA0088 (B 42,4 →), reemplazado por la toma completa de WA0089.
- Se dejó la pausa cómica corta entre "don't support you… bueno… no".

Encuadre: alternancia 1.00 / 1.06–1.10 entre cortes, punch-in 1.20 en cada keyword y en "¡No te soporto!",
1.22 en el "No." del gag, 1.12 en "guardá el video", push lento (+3/4 %) en los planos largos. Origen del zoom `50% 45%`
para que el mentón no baje sobre el texto.

## Beats
| t (s) | Plano | Texto / efecto |
|---|---|---|
| 0,0–2,3 | "Ayer una alumna me preguntó cómo se dice…" | Tarjeta blanca «¡No te soporto! / In English» |
| 2,3–3,4 | "…no te soporto en inglés" | «¡No te soporto!» gigante letra por letra + punch-in |
| 3,4–4,6 | "Si pensaste en…" | subtítulo palabra por palabra |
| 4,6–6,4 | "don't support you, bueno…" | **B&N + voz apagada + thud**, «I don’t support you?» en rojo con sacudida |
| 6,4–6,7 | "No." | vuelve el color, tachado + ❌, punch-in 1.22 |
| 6,7–8,9 | "Te voy a dejar 3 maneras de decirlo" | subtítulo, «3 maneras» en crema |
| 8,9–13,3 | "La primera es… can't stand. Es cuando vos no soportás hacer algo. Ejemplo." | «Can’t stand» + «No soportar hacer algo» |
| 13,3 | — | línea blanca + blur + click |
| 13,3–17,2 | "I can't stand waiting in line. No soporto hacer fila." | par de ejemplo EN/ES |
| 17,2–21,3 | "La segunda tiene que ver con algo más emocional… can't bear" | subtítulos («emocional» en crema) + 🥺 + «Can’t bear» |
| 21,3–24,8 | "I can't bear seeing her crying. No soporto verla llorar." | ejemplo + 😢 |
| 24,8–27,6 | "Y la tercera es… can't take. Por ejemplo," | «Can’t take» + «No soportar más / Llegar al límite» + 😠→😡→🤬 |
| 27,6–34,1 | "This noise is driving me crazy. I can't take it anymore. Este ruido…" | ejemplo de 4 líneas |
| 34,1–43,5 | CTA (WA0089) | subtítulos con «guardá el video» (🔖), «escribime» (💬), «inglés real» en crema |
| 43,5–44,7 | "Bye." | «Bye!» gigante + 👋 |

## Audio
Voz sola, como en la referencia (no tiene música). Cadena: high-pass 90 Hz, denoise suave, compresión 3:1,
crossfades de 15 ms en cada corte, loudnorm −14 LUFS / −1,5 dBTP. SFX sintetizados con ffmpeg (sin derechos):
click en las 3 transiciones, pop en keywords, stickers y frases gigantes, thud al entrar el blanco y negro.

## Design decisions
- **Banda de texto en el pecho (49–65cqh)** en vez de arriba: la cara está arriba en estos clips. El borde de
  65 % es la zona segura de Reels que valida `hyperframes check`.
- El sticker de meme de la referencia (personaje dibujado) se reemplazó por emoji Noto (licencia OFL) para no usar
  material de terceros.
- «Can’t bear» queda solo 0,7 s porque en el audio la profe dice la expresión y enseguida el ejemplo; el significado
  ("algo más emocional") va antes, como subtítulo con 🥺.
- No hay grano ni color grade fuerte (solo +6 % de contraste y saturación): el look es de celular limpio, como la referencia.

## Verificación
- `npx hyperframes check`: 0 errores. Quedan avisos de "línea poco tiempo en pantalla" (normales en subtítulos
  sincronizados palabra por palabra), de zona segura de TikTok/Shorts (bordes más estrictos que Reels) y de estructura
  (sugerencia de sub-composiciones).
- Capturas revisadas en hook, gag, las 3 keywords, los 3 ejemplos, CTA y cierre.
- `verify-render.mjs` y contact sheet: ver `finalize.sh`.
