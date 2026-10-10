# Edit report — Saving Hub: 2 reels (Jean Lowe Immortel · Bharara King decant)

**Disposition:** in_review (esperando feedback del cliente)
**Output:**
- `output/SavingHub_JeanLowe_Immortel.mp4` — 1080x1920, 22.10 s, h264/yuv420p 30 fps, AAC, -14 LUFS
- `output/SavingHub_Bharara_King_Decant.mp4` — 1080x1920, 22.50 s, h264/yuv420p 30 fps, AAC, -15 LUFS

**Style:** "Documental Reel" (skill `editar-video-estilo-documental`) sobre el workflow de `video-editing`
(HyperFrames init → check → snapshot → render → verify).

## Material
- `source/vid34.mp4` (152 s) — unboxing Maison Alhambra *Jean Lowe Immortel*, guantes negros.
- `source/vid31.mp4` (109 s) — Bharara *King*: caja, frasco y decantado con jeringa a vial.
- Ambos son 464x832 @ 59.94 fps, **sin voz** (VAD Silero: 0 s de habla) → audio ASMR del unboxing.

## Reel 1 — Jean Lowe Immortel
| ts | Plano (src) | Texto | SFX |
|----|-------------|-------|-----|
| 0.0–1.8 | caja a cámara (3.0) + pixelado→nítido | ¿LUJO FRANCÉS | click |
| 1.8–3.4 | caja frente (5.0) | A PRECIO **ÁRABE?** (punch + flash) | whoosh, impact |
| 3.4–5.4 | etiqueta Maison Alhambra (15.0) | MAISON **ALHAMBRA** | whoosh, click |
| 5.4–9.1 | pelando el film / abriendo (27, 50) | JEAN LOWE **IMMORTEL** | whoosh, click |
| 9.1–11.3 | tubo en mano (66) | **100** ML · EAU DE PARFUM | whoosh, click |
| 11.3–13.1 | tapa del tubo (77.5) | SUBÍ EL **VOLUMEN** | whoosh, click, riser |
| 13.1–15.3 | reveal del frasco (84.5) | MIRÁ ESE **COLOR** | whoosh, click |
| 15.3–17.7 | frasco close (95) | FRESCO. CÍTRICO. **ADICTIVO.** | whoosh, click |
| 17.7–19.5 | líquido close (102.5) | EL QUE TODOS TE VAN A **PREGUNTAR** | whoosh, click |
| 19.5–22.1 | frasco en base + logo SH (124) | SAVING **HUB** · LUJO SIN PAGAR DE **MÁS** · [PEDILO POR DM] | riser, impact, click |

## Reel 2 — Bharara King (decant)
| ts | Plano (src) | Texto | SFX |
|----|-------------|-------|-----|
| 0.0–1.8 | abriendo la caja (3.5) + pixelado→nítido | ¿GASTAR UNA **FORTUNA** (punch) | click, impact |
| 1.8–3.4 | caja abierta con frasco (7.0) | EN UN FRASCO **ENTERO?** (punch) | whoosh, impact |
| 3.4–6.5 | frasco en mano (15, 21) | BHARARA **KING** | whoosh, click |
| 6.5–8.1 | frasco a la mesa (40) | NO HACE **FALTA.** | whoosh, click |
| 8.1–9.9 | preparando (50) | PROBALO EN **DECANT** | whoosh, click |
| 9.9–14.3 | jeringa en el original (57, 64) | placa roja: DIRECTO DEL FRASCO ORIGINAL | whoosh, click |
| 14.3–16.3 | llenando el vial (76) | A TU **DECANT** | whoosh, click |
| 16.3–19.9 | tapando / spray (86, 100) | LISTO PARA **LLEVAR** | whoosh, click |
| 19.9–22.5 | frasco + decant + logo SH (106) | SAVING **HUB** · PROBÁ ANTES DE **COMPRAR** · [PEDILO POR DM] | riser, impact, click |

## Audio
- ASMR original de cada plano, comprimido y normalizado; master final a -14/-15 LUFS.
- SFX sintetizados con ffmpeg (rights-free): whoosh (cortes), impact (golpes de texto), click (entradas), riser (reveal y cierre).
- Un único `master.m4a` por reel. **Sin música** (no había pista con licencia disponible).

## Design decisions
- Paleta y tipografía del estilo del usuario (Anton, rojo #E0201B / blanco), no del pack `vibe-life`.
- Sin voz en off: el texto cuenta la historia y el ASMR queda como "cama" sonora (formato habitual en unboxings de perfumes).
- Textos en el tercio superior para no tapar el producto; scrim oscuro arriba porque la pared es blanca.
- Grano de film aplicado en un pase final con ffmpeg (sobre video y textos), bitrate limitado a ~9 Mbps.

## Verification
- `hyperframes lint`: 0 errores. Las advertencias son de estructura (track density / sub-compositions), no afectan el render.
- Snapshots de preview revisados (textos legibles, sin cortes, producto visible).
- `verify-render.mjs`: GATE PASS en ambos.
- Contact sheets: `work/*_final_sheet.png`.

## Pendiente / a confirmar
- ¿Precio, @usuario o WhatsApp para el cierre? Hoy dice "PEDILO POR DM".
- ¿Agregar música (tema propio o generada)?
- "¿LUJO FRANCÉS A PRECIO ÁRABE?" alude a que el Immortel es una alternativa a un perfume francés de lujo, sin nombrar la marca.

---

# Ronda 2 — ideas nuevas + test de hooks + voz IA

**Voz IA:** Kokoro-82M local (`hyperframes tts`, voz `ef_dora`, español, velocidad 1.08). Gratis y offline.
Los nombres propios se escriben fonéticamente para el TTS ("Séiving Jab", "Yin Lou Inmortel", "Bajarára", "decánt").
**En los videos con voz se quita el sonido original (ASMR)**: el audio es solo la voz IA y los SFX de edición (whooshes, impactos, riser). Subtítulos palabra por palabra, a la velocidad de la voz.
Todo se genera con `build_vo.py` y el pase final con `finalize.sh`.

| Video | Idea | Duración |
|-------|------|----------|
| `SavingHub_V2_JeanLowe_EsOriginal_VozIA` | "¿Cómo saber si tu perfume árabe es original?" — 1. holograma, 2. sellado con film, 3. info impresa → lo abrimos frente a cámara → cierre | 17.3 s |
| `SavingHub_V2_Decant_HookA_QueEsUnDecant_VozIA` | Hook A: "¿Qué es un decant? Mirá." | 15.4 s |
| `SavingHub_V2_Decant_HookB_ACiegas_VozIA` | Hook B: "No compres un perfume de lujo a ciegas." | 16.2 s |
| `SavingHub_V2_Decant_HookC_Fortuna_VozIA` | Hook C: "Este perfume cuesta una fortuna. Pero hay un truco." | 16.8 s |

**Test de hooks:** las 3 versiones del decant comparten los mismos planos (caja abriéndose con pixelado → nítido) y el mismo cuerpo:
"Así armamos tu decant → directo del frasco original, con jeringa → a un atomizador de vidrio → y listo →
probás Bharara King sin gastar de más → Saving Hub, pedilo por mensaje". **Solo cambian el texto y la voz del hook.**
Para medir: publicarlos con el mismo copy y horario (o como variantes de anuncio) y comparar la retención a los 3 s
y el % de reproducción completa.

Verificación: lint 0 errores, `verify-render.mjs` GATE PASS ×4 y contact sheets revisados.

---

# Ronda 3 — 5 reels motion graphics

Cada cuadro es una pieza diseñada, no footage a pantalla completa. Fondo negro con grilla o rojo, titulares en Anton
revelados con máscara, etiquetas en JetBrains Mono, clips del producto dentro de tarjetas animadas con marcas de esquina,
HUD fijo ("SAVING HUB" + sección) con barra de progreso, y transición con cortina roja y blanca entre escenas.
Audio: beat de 120 BPM sintetizado (libre de derechos, `mg_assets.py`) + SFX (whoosh, click, impact, riser). Sin voz.

| Video | Idea | Escenas | Duración |
|-------|------|---------|----------|
| `SavingHub_MG1_DecantVsFrasco` | ¿Frasco entero o decant? | título → tabla comparativa ✗/✓ con VS → tarjeta de la jeringa → logo | 14.5 s |
| `SavingHub_MG2_TresPasos` | Así se arma un decant | título → 01 EXTRAEMOS → 02 TRASVASAMOS → 03 SELLAMOS (barra de progreso segmentada) → logo | 14.0 s |
| `SavingHub_MG3_FichaJeanLowe` | Ficha técnica Jean Lowe Immortel | título → ficha (casa, tipo, 100 ML, perfil, origen) → holograma con marcas → contador 100 ML → logo | 15.5 s |
| `SavingHub_MG4_LlegoTuPedido` | POV: llegó tu decant | notificaciones tipo celular sobre el producto desenfocado → tarjeta del decant → logo | 12.0 s |
| `SavingHub_MG5_PerfumesArabes` | Lujo sin pagar de más | tipografía cinética + marquesina → tarjeta Jean Lowe → tarjeta Bharara → FRASCOS Y DECANTS → logo | 14.0 s |

El logo "SH" del cierre es una versión simplificada para el video (cuadro rojo con SH subrayado); se reemplaza por el oficial si lo pasan en PNG/SVG.
Verificación: lint 0 errores, snapshots revisados (tildes, estados iniciales, overflow), GATE PASS ×5, contact sheet `work/mg_all.png`.

## Ronda 3b — motion graphics con voz IA

`build_mg_vo.py`: las mismas 5 piezas con voz IA (Kokoro `ef_dora`), una frase por escena. Cada escena se alarga
(sobre la grilla de 0,5 s) para que entre su frase. **Con voz se quita la base musical**: queda voz + SFX de las animaciones.
Salidas: `output/SavingHub_MG*_VozIA.mp4` (12–17,5 s, -15/-16 LUFS). Las versiones sin voz siguen en `output/SavingHub_MG*.mp4`.
GATE PASS ×5.

## Corrección — voz duplicada en los videos con voz IA

**Problema:** en los 9 videos con voz IA se escuchaban dos voces encimadas.
**Causa:** `loudnorm` devuelve el bus de voz a 192 kHz en mono; al pasarlo a estéreo sin re-muestrear primero,
ffmpeg generaba dos canales desfasados entre sí (correlación L/R 0,065), que se escuchan como dos voces superpuestas.
**Arreglo:** `aresample=48000` después de `loudnorm`, antes de `aformat=stereo`, en `build_vo.py` y `build_mg.py`.
Se regeneró el audio de los 9 videos; la imagen no cambió.
**Control nuevo (`check_vo.py`):** exige correlación L/R > 0,98 y que cada frase aparezca una sola vez, en su
tiempo planeado (±40 ms). Las posiciones quedan en `edit-v2-*/vo.json` y `mg-*-voz/timeline.json`.
Resultado: los 9 videos pasan (L/R 1,000; todas las frases en su lugar).

---

# Ronda 4 — "Todo esto es un pedido mayorista" (armado de pedido, voz IA)

**Disposition:** in_review
**Output:** `output/SavingHub_V4_PedidoMayorista_VozIA.mp4` — 1080x1920, 20.0 s, h264/yuv420p 30 fps, AAC
**Fuente:** `source/vid_pedido.mp4` (WhatsApp, 111,5 s, 576x1024 vertical por metadata de rotación, 30 fps, sin voz).
Es un **pedido mayorista** (confirmado por el cliente). Se arma una caja grande: Asad (Lattafa), cajas varias, Club de Nuit Intense (Armaf), Vulcan, un cargador
2-en-1 con cable, papel kraft de relleno y cierre con cinta.

**Hook (0–2,9 s):** abre con el **final** — la caja ya llena, pixelada → nítida — y la voz dice
"Todo esto, es un pedido mayorista." (golpe + flash en **MAYORISTA**). Inmediatamente un **rebobinado**: 70 s del
video en reversa en 0,86 s con SFX de cinta y el texto **REBOBINEMOS**, y arranca el armado desde la caja vacía.
Es un loop abierto (¿cómo entra todo eso?) + pattern interrupt a los 2 s. El cierre vuelve al plano de la caja
llena, así el final empalma con el inicio cuando el reel se repite. Como es mayorista, el cierre le habla al
revendedor: "¿Querés revender? Escribinos por mensaje."

| ts | Voz IA | Texto (rojo = *) | Planos (src) |
|----|--------|------------------|--------------|
| 0.00–2.07 | Todo esto, es un pedido mayorista. | TODO ESTO ES UN PEDIDO *MAYORISTA | caja llena 75.4–77.3, pixelado→nítido |
| 2.07–2.93 | Rebobinemos. | *REBOBINEMOS | 77.3 → 7.0 en reversa (82x) |
| 2.93–5.33 | Primero, el Asad de Lattafa, bien al fondo. | PRIMERO, EL *ASAD DE LATTAFA, · BIEN AL *FONDO | caja vacía 7–9.7 (3x), Asad en mano 9.9, al fondo 10.7–12.2 |
| 5.33–7.93 | Después, cada caja en su lugar, bien apretada. | DESPUÉS, CADA CAJA · EN SU *LUGAR, · BIEN *APRETADA | 15.5–19.5, 22.5–26.5, 29–33 (≈4.6x) |
| 7.93–10.20 | Club de Nuit Intense, de Armaf. Y el Vulcan. | CLUB DE NUIT INTENSE, DE *ARMAF. · Y EL *VULCAN | 37.6, 40.5–44, 47.8, 50–54 |
| 10.20–12.07 | Y hasta el cargador, con su cable. | Y HASTA EL *CARGADOR, · CON SU *CABLE | 67.6 (cargador 2-en-1), 71.9 (cable) |
| 12.07–14.40 | Papel de relleno, para que llegue perfecto. | PAPEL DE RELLENO, · PARA QUE LLEGUE *PERFECTO | 85–90, 93–97, 99–103 (≈5x) |
| 14.40–16.13 | Cerramos, y listo para salir. | CERRAMOS, · Y LISTO PARA *SALIR | 103.5–107, 107–110.5 |
| 16.13–19.98 | Saving Hub. ¿Querés revender? Escribinos por mensaje. | SAVING **HUB** · ¿QUERÉS *REVENDER? · [ESCRIBINOS POR DM] | caja llena 75.4–77.3 (loop) |

## Audio
- Voz: Kokoro `ef_dora`, velocidad 1.08 (la misma de las rondas 2–3). Fonética para el TTS: "Asád de Latáfa",
  "Club de Nuí Inténs, de Armáf", "Vúlcan", "Séiving Jab", y "Serramos" (con C, Kokoro la pronuncia con la
  z española). Fonemas revisados con el tokenizer de Kokoro.
- Sin sonido original (igual que los demás videos con voz): voz IA + SFX (whoosh en cada corte, impacto en el
  hook, rebobinado nuevo `sfx/rewind.wav`, riser + impacto en el cierre). Master único, -14 LUFS en el pase final.

## Cambios en el pipeline
- `build_base.py`: un plano puede ser un rango `[desde, hasta]` que se acelera para llenar su tiempo, o se
  invierte si `hasta < desde` (rebobinado). Cada plano usa su propia entrada con `-ss`: con planos fuera de
  orden, una sola entrada hacía que ffmpeg guardara todo el video decodificado en memoria (se quedaba sin RAM).
- `build_vo.py`: con `"sync": True` el texto se escribe palabra por palabra igual que la voz y cada palabra
  entra en su momento estimado dentro de la frase (por largo de palabra + pausas en comas y puntos), en vez de
  a intervalos fijos. `|` fuerza una pantalla nueva de texto. `"sfx"` agrega un efecto al inicio de una línea.
  Los videos anteriores no usan estas opciones; no cambian.
- `build_audio.py`: SFX nuevo `rewind` (barrido descendente con trémolo sobre ruido), sintetizado, libre de derechos.

## Design decisions
- Mismo estilo "Documental Reel" de los reels anteriores (Anton gigante rojo/blanco palabra por palabra, Ken Burns,
  whips con blur, punch-in, grano, cierre SAVING HUB + "PEDILO POR DM").
- Nuevo: tramos acelerados (3–5x) para que el armado tenga ritmo sin perder qué producto se ve, y el rebobinado
  como transición del hook. No hay disolvencias ni transiciones de plantilla.
- Cierre para revendedores: tag "¿QUERÉS *REVENDER?" y botón "ESCRIBINOS POR DM" (en vez de "LUJO SIN PAGAR DE
  MÁS" / "PEDILO POR DM"). `build_vo.py` ahora acepta `"cta"` por video (default "PEDILO POR DM").

## Verification
- `hyperframes lint`: 0 errores (19 advertencias de estructura/sub-compositions, igual que los reels anteriores).
- Snapshots de preview revisados; se corrigió el plano del Asad (entraba recién a los 9,75 s del original:
  ahora aparece con la etiqueta cuando la voz lo nombra).
- `verify-render.mjs --duration 19.98`: GATE PASS (20.00 s). Loudness -14.1 LUFS, pico -3.0 dBFS.
- `check_vo.py`: L/R 1,000 y las 9 frases de voz en su lugar (±10 ms), sin voces duplicadas.
- Contact sheet `work/SavingHub_V4_PedidoMayorista_VozIA_sheet.png`: cada texto coincide con el producto en pantalla.
- La primera versión ("Todo esto, es un solo pedido", cierre "ARMÁ TU PEDIDO") se reemplazó por esta al confirmar
  que es mayorista.
- No se pudo transcribir la voz con Whisper (la red del entorno bloquea la descarga del modelo); la pronunciación
  se revisó por fonemas de Kokoro.

## A confirmar antes de publicar
- **Cargador y cable:** son cajas con logo de Apple ("2in1"). La voz no nombra la marca a propósito; confirmar
  que se pueden mostrar.
- **Datos personales:** en los planos usados no aparecen etiquetas de envío ni datos del cliente.

---

# Ronda 5 — "Abrimos esta caja de perfumes... y hay uno que no te esperás" (voz IA)

**Disposition:** reemplazada por la Ronda 5b (el cliente marcó que no era el estilo de Saving)
**Output:** `output/SavingHub_V5_CajaDePerfumes_VozIA.mp4` — 1080x1920, 16.3 s, h264/yuv420p 30 fps, AAC, -14 LUFS
**Fuente:** `source/vid_caja.mp4` (WhatsApp, 147 s, 576x1024 vertical por metadata de rotación, 30 fps, sin voz).
Se desarma una caja de mercadería tapada con bolsas negras, producto por producto, hasta dejarla vacía.

**Hook (0–3,2 s):** la caja tapada con la bolsa negra (pixelada → nítida); la mano levanta la bolsa justo cuando
la voz dice "perfumes". La frase abre un loop: "...y hay uno que no te esperás" (golpe + flash en **ESPERÁS**).
El pago llega a los 8,4 s: **Le Male Elixir de Jean Paul Gaultier**, el único de diseñador entre los árabes
(segundo golpe en **ELIXIR**). Entre medio, un producto por frase (~1 s cada uno) para sostener el ritmo.
Cierre con pregunta para comentarios: "¿Cuál te llevás?".

| ts | Voz IA | Texto (rojo = *) | Planos (src) |
|----|--------|------------------|--------------|
| 0.00–3.25 | Abrimos esta caja de perfumes... y hay uno que no te esperás. | ABRIMOS ESTA CAJA DE *PERFUMES · Y HAY UNO QUE NO TE *ESPERÁS | caja tapada 0.5–2.2, se levanta la bolsa 2.2–4.8 |
| 3.25–4.37 | Yara, de Lattafa. | YARA, DE *LATTAFA | 10.0 |
| 4.37–5.45 | Un set de regalo. | UN SET DE *REGALO | 75.5 (set rosa con miniaturas) |
| 5.45–6.41 | Bharara King. | BHARARA *KING | 106.8 |
| 6.41–7.25 | Velvet Oud. | *VELVET OUD | 122.3 |
| 7.25–8.45 | Hawas, de Rasasi. | *HAWAS, DE RASASI | 130.9 |
| 8.45–11.52 | Y el que no te esperabas: Jean Paul Gaultier, Le Male Elixir. | Y EL QUE NO TE *ESPERABAS: · JEAN PAUL GAULTIER, · LE MALE *ELIXIR | sacando la lata 58–60.6, lata 60.9, 64.9 |
| 11.52–12.76 | Y la caja, vacía. | Y LA CAJA, *VACÍA | 141.6–144.6 |
| 12.76–16.22 | Saving Hub. ¿Cuál te llevás? Pedilo por mensaje. | SAVING **HUB** · ¿CUÁL TE *LLEVÁS? · [PEDILO POR DM] | caja llena 19.8–21.2 |

## Audio
- Voz Kokoro `ef_dora` 1.08, sin sonido original; SFX de edición (whoosh por corte, impactos en los dos golpes,
  riser + impacto en el cierre).
- Fonética para el TTS: "Latáfa", "Bajarára King", "Vélvet Úd", "Jauás, de Rasási", "Yan Pol Goltié, Le Mal Elixír",
  "vasía" (con C, Kokoro usa la z española). Fonemas revisados con el tokenizer de Kokoro.

## Design decisions
- Mismo estilo "Documental Reel" y mismo pipeline (`build_vo.py`, video `edit-v5-caja`); solo planos a velocidad
  normal salvo la bolsa del hook y la caja vaciándose.
- Nombres en pantalla: solo los que se leen en las cajas (YARA / Lattafa, BHARARA KING, VELVET OUD, HAWAS For Him,
  Jean Paul Gaultier LE MALE ELIXIR). Las cajas con "X" (turquesa y blancas) no se nombran.

## Entorno
- El auto-update de HyperFrames (0.8.140 → 0.8.142) dejó `hyperframes.mjs` sin permiso de ejecución; se corrigió con
  `chmod +x`. Este proyecto queda fijado a 0.8.142.

## Verification
- `hyperframes lint`: 0 errores (14 advertencias de estructura).
- Snapshots de preview revisados: cada producto se ve con su etiqueta cuando la voz lo nombra.
- `verify-render.mjs --duration 16.22`: GATE PASS (16.30 s). Loudness -14.0 LUFS, pico -3.3 dBFS.
- `check_vo.py`: L/R 1,000 y las 9 frases en su lugar (±10 ms), sin voces duplicadas.
- Cuadros a mitad de cada plano (`work/SavingHub_V5_CajaDePerfumes_VozIA_midshots.png`): producto y texto coinciden.
  En el render de 0.8.142 la imagen cambia 1–2 cuadros (≤ 0,07 s) después que el texto en cada corte; no se nota
  a velocidad normal.

## A confirmar antes de publicar
- "Hawas, de Rasasi": en la cara visible de la caja se lee "HAWAS For Him"; la marca Rasasi se agregó por el nombre
  del perfume. Si fuera otra casa, se cambia la frase.
- "Un set de regalo": es la caja rosa con miniaturas (logo de Yara). Si tiene otro nombre comercial, se ajusta.

---

# Ronda 5b — misma caja, en el estilo de savings.hub

**Disposition:** in_review
**Output:** `output/SavingsHub_V5_CajaDePerfumes_VozIA.mp4` — 1080x1920, 16.1 s, h264/yuv420p 30 fps, AAC, -14 LUFS
**Por qué:** el cliente indicó que el estilo Documental (Anton gigante rojo/blanco, grano, whips) **no es el estilo
de Saving** y mandó capturas de su reel "Erba Pura G5" (guardadas en `referencias/`). Se tomó de ahí el estilo,
se guardó como pack fijo (`.claude/skills/video-editing/styles/savings-hub/FRAME.md`) y se generó con un builder
nuevo, `build_sh.py`. La voz, el guion y los planos son los de la Ronda 5.

**Estilo (medido en las capturas):** tinta #110F0D con grilla, papel #F2ECE0, dorado #E1B857, bordó #842A36,
pill de costura #8E1A2E. Space Grotesk 700 para subtítulos y titulares, Instrument Serif itálica para la palabra
acento, JetBrains Mono espaciada para los pills. Imagen limpia (sin grano), grading natural.

| ts | Layout | Texto | Planos (src) |
|----|--------|-------|--------------|
| 0.00–1.64 | tarjeta sobre grilla oscura + pill **LA APERTURA** | Abrimos esta caja / de *perfumes...* | caja tapada 0.5–2.2 |
| 1.64–3.25 | la tarjeta crece a pantalla completa (0,55 s) | barras: y hay uno que / no te *esperás.* | se levanta la bolsa 2.2–4.8 |
| 3.25–6.41 | pantalla completa | Yara, de *Lattafa.* · Un set de *regalo.* · Bharara *King.* | 10.0 · 75.5 · 106.8 |
| 6.41–8.17 | split + pill bordó **VELVET OUD + HAWAS** | *Velvet Oud.* · *Hawas,* de Rasasi. | arriba 122.3 / abajo 130.9 |
| 8.17–11.24 | tarjeta sobre grilla oscura + pill **LA SORPRESA** | Y el que no te / *esperabas:* · Jean Paul Gaultier, · titular Le Male *Elixir* (serif dorada + subrayado) | 58–60.6 · 60.9 · 64.9 |
| 11.24–12.48 | pantalla completa | Y la caja, *vacía.* | 141.6–144.6 |
| 12.48–16.09 | cierre en papel: tarjeta inclinada | ¿Cuál te *llevás?* (serif bordó + subrayado) · [ESCRIBINOS · SAVINGS.HUB] | caja llena 19.8–21.2 |

## Audio
- Voz Kokoro `ef_dora` 1.08 (la marca se pronuncia "Séivings Jab"), sin sonido original.
- SFX suaves: click en cada subtítulo y pill, whoosh bajo en cortes y cambios de layout, impacto suave en
  "Elixir", riser + impacto al entrar el cierre.

## Cambios en el pipeline
- `build_sh.py` (nuevo): layouts tarjeta / pantalla completa / split / cierre, dos videos (`base.mp4` y
  `base_b.mp4` para la mitad de abajo del split), subtítulos por frase sincronizados con la voz.
- `build_base.py`: `grade`, `pixel_reveal` y `basename` opcionales (los reels anteriores no cambian).
- `finalize.sh`: `GRAIN=0` saltea el grano (el estilo de la marca es limpio).
- Se borró el render Documental de la Ronda 5 (`SavingHub_V5_CajaDePerfumes_VozIA.mp4`) y su proyecto, para que no
  se publique por error; sigue en el historial del branch.

## Verification
- `hyperframes lint`: 0 errores (19 advertencias de estructura).
- Snapshots revisados contra las capturas de referencia (pills, barras, split, cierre en papel).
- `verify-render.mjs --duration 16.09`: GATE PASS (16.10 s). Loudness -14.0 LUFS, pico -3.1 dBFS, sin grano.
- `check_vo.py`: L/R 1,000 y las 8 frases de voz en su lugar (±10 ms), sin voces duplicadas.
- Cuadros a mitad de cada plano (`work/SavingsHub_V5_CajaDePerfumes_VozIA_midshots.png`): producto, texto y layout
  coinciden en todos.
- El cliente confirmó el estilo ("Ese es el estilo").

---

# Ronda 6 — "Así venimos este mes" (resumen del mes, estilo savings.hub)

**Disposition:** in_review
**Output:** `output/SavingsHub_V6_ResumenDelMes_VozIA.mp4` — 1080x1920, 19.5 s, h264/yuv420p 30 fps, AAC, -14 LUFS, sin grano
**Material:** el cliente pasó 6 videos. Los 4 que ya habíamos editado (V5 caja, V4 mayorista, V2 decant hooks A/B) se
reconstruyeron desde sus **originales sin texto** (`source/vid_caja.mp4`, `vid_pedido.mp4`, `vid31.mp4`) para no
apilar textos ni estilos viejos. Los 2 nuevos son reels propios de la cuenta, ya editados y con títulos quemados:
`source/revendedor_30000.mp4` ("PEDIDO · Revendedor: $30.000", bolsa kraft con sticker SH) y
`source/velvet_oud.mp4` ("Unboxing · VELVET OUD"). En esos se hace zoom (1,15–1,5x, foco abajo) para dejar los
títulos fuera de cuadro y re-titular en el estilo de la marca.

| ts | Layout | Voz / texto | Planos |
|----|--------|-------------|--------|
| 0.00–2.28 | tarjeta + pill **RESUMEN DEL MES** → crece a pantalla completa | Así venimos este *mes* · en Savings *Hub.* | adelanto de 6 planos de 0,38 s: caja llena, Velvet Oud, jeringa, caja mayorista, pedido revendedor, Le Male |
| 2.28–5.15 | tarjeta + pill **LLEGÓ MERCADERÍA** → crece | Llegó *mercadería:* · Yara, Hawas, y hasta Le Male *Elixir.* | bolsa negra, Yara, Hawas, Le Male (vid_caja) |
| 5.15–7.65 | split + pill **FRASCO + DECANT** | Armamos *decants,* · directo del frasco *original.* | arriba jeringa en el original (vid31 57) / abajo llenando el atomizador (vid31 76) |
| 7.65–9.99 | tarjeta + pill **UNBOXING** | Abrimos el *Velvet Oud...* · y mirá ese *color.* | tubo, botella saliendo, jugo dorado (velvet_oud) |
| 9.99–12.64 | pantalla completa | Armamos un pedido *mayorista,* · lleno hasta *arriba.* | armado rápido, relleno, caja llena (vid_pedido) |
| 12.64–15.29 | tarjeta + pill **REVENDEDORES** → crece | Y pedidos de *revendedores,* · como este de *$30.000.* | revendedor_30000 |
| 15.29–19.41 | cierre en papel | "Y el mes recién empieza. Savings Hub. ¿Qué traemos ahora?" · ¿Qué *traemos?* · [ESCRIBINOS · SAVINGS.HUB] | bolsa kraft con el sticker SH |

## Cambios en el pipeline
- `build_base.py`: un plano puede venir de otro video (`{"src", "at", "zoom", "fy"}`), con zoom para sacar títulos
  quemados.
- `build_sh.py`: config `RESUMEN`; la geometría sigue al estado real (una tarjeta que creció ya está a pantalla
  completa); la marca de palabra clave acepta `*palabra*`.
- **Corrección de animación (afecta también al V5):** los elementos con entrada demorada (2ª línea de subtítulo,
  pills, texto del cierre) se veían completos uno o más cuadros antes de su animación y después "saltaban". Ahora
  arrancan ocultos desde el CSS. El V5 se volvió a renderizar con la corrección.

## A confirmar
- "$30.000" se toma tal cual del título del video del revendedor (la voz dice "treinta mil", sin moneda).
- Velvet Oud: la etiqueta solo dice "VELVET OUD · eau de parfum"; no se nombra la casa.

## Verification
- `hyperframes lint`: 0 errores (advertencias de estructura). Snapshots revisados, incluido el cuadro 0 y los
  instantes donde antes había destellos (2ª línea de subtítulo, cierre).
- `verify-render.mjs`: GATE PASS (19.50 s). `check_vo.py`: L/R 1,000, 7 frases en su lugar. -14.1 LUFS, pico -3.0 dBFS.
- Fonemas de las 7 frases revisados: ninguna con θ.
- Cuadros a lo largo del video: `work/SavingsHub_V6_ResumenDelMes_VozIA_midshots.png`.
- Memoria: no había memoria guardada en el entorno; se creó `CLAUDE.md` (raíz del repo) con las reglas de Saving y el
  video se contrastó contra ellas.
