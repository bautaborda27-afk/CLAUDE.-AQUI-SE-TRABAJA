---
# ============================================================================
# FRAME.md — "Inglés Reel" (clase de inglés a cámara, 9:16)
# Estilo extraído de un reel de referencia de una profe de inglés para hispanohablantes
# (frase en español → cómo se dice en inglés → 3 expresiones con ejemplo).
# Frontmatter = fuente normativa. Tamaños en cqw/cqh sobre 1080x1920 (1cqw = 10.8px).
# ============================================================================

colors:
  # El "fondo" es SIEMPRE el video de la persona hablando a cámara (A-roll full-frame).
  ink: "#111111"            # contorno de TODO texto + sombra
  white: "#FFFFFF"          # español: significados, traducciones, subtítulos
  cream: "#FADEB2"          # LA voz de acento: expresión en inglés y palabra clave (muestreado del original)
  wrong: "#E3262E"          # SOLO para la traducción incorrecta (gag del error común)
  card: "rgba(255,255,255,0.94)"   # tarjeta del título del hook
  flash: "#FFFFFF"          # línea/destello de la transición

typography:
  # Poppins ExtraBold/Bold + Roboto Medium, woff2 locales en styles/ingles-reel/fonts/
  title-card:
    fontFamily: "Poppins, sans-serif"
    fontWeight: 800
    fontSize: "8.6cqw"
    lineHeight: 1.08
    letterSpacing: "-0.01em"
  big-phrase:               # frase gigante centrada del hook ("¡No te soporto!")
    fontFamily: "Poppins, sans-serif"
    fontWeight: 800
    fontSize: "16cqw"
    lineHeight: 0.98
    letterSpacing: "-0.02em"
  keyword:                  # la expresión en inglés ("Can't stand")
    fontFamily: "Poppins, sans-serif"
    fontWeight: 800
    fontSize: "11.5cqw"
    lineHeight: 1.0
    letterSpacing: "-0.02em"
  meaning:                  # significado en español debajo de la keyword
    fontFamily: "Roboto, sans-serif"
    fontWeight: 500
    fontSize: "7cqw"
    lineHeight: 1.06
    letterSpacing: "-0.01em"
  example:                  # par de ejemplo “EN” / “ES”
    fontFamily: "Poppins, sans-serif"
    fontWeight: 700
    fontSize: "6cqw"          # 5–5.5cqw si el ejemplo es largo (4 líneas)
    lineHeight: 1.14
    letterSpacing: "-0.045em"
  caption:                  # subtítulo palabra por palabra de la narración
    fontFamily: "Poppins, sans-serif"
    fontWeight: 700
    fontSize: "8.2cqw"
    lineHeight: 1.04
    letterSpacing: "-0.04em"
  wrong:                    # traducción incorrecta, en rojo
    fontFamily: "Poppins, sans-serif"
    fontWeight: 800
    fontSize: "9cqw"
    lineHeight: 1.0
    letterSpacing: "-0.03em"

stroke:                     # contorno exterior (paint-order: stroke fill), siempre {colors.ink}
  big-phrase: "2.2cqw"
  title-card: "1.3cqw"
  keyword: "1.7cqw"
  meaning: "1.1cqw"
  example: "1.0cqw"
  caption: "1.2cqw"
  wrong: "1.0cqw"           # en blanco, no ink
  shadow: "0 0.5cqw 1.2cqw rgba(0,0,0,.35)"

rounded:
  card: "4.4cqw"

spacing:
  # Zona libre de Reels (la que valida `hyperframes check`): y 14–65 %, x 6–94 %.
  # Debajo del 65 % van usuario, caption y botones; nada de lectura ahí.
  safe-top: "14cqh"
  safe-bottom: "65cqh"      # borde inferior del texto (no el superior)
  safe-x: "6cqw"
  text-band-top: "15cqh"    # banda de texto si la cara está en la mitad/abajo del cuadro (como el original)
  text-band-chest: "49cqh"  # banda de texto si la cara está arriba (selfie desde abajo): 49–65cqh

components:
  title-card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
    padding: "2.6cqw 5.2cqw 3cqw"
    shadow: "0 1cqw 3cqw rgba(0,0,0,.25)"
    line1: "frase en español, {colors.cream} + contorno ink"
    line2: "'In English', {colors.white} + contorno ink"
  keyword-block:
    keyword: "{typography.keyword} {colors.cream}"
    meaning: "{typography.meaning} {colors.white}, 1–2 líneas, aparece cuando la voz lo dice"
  example-pair:
    en: "{typography.example} {colors.white} entre comillas, la expresión en {colors.cream}"
    es: "{typography.example} {colors.white} entre comillas, en la línea de abajo"
  sticker:
    size: "20–26cqw"
    position: "al costado del bloque de texto, nunca sobre la cara"
    source: "styles/ingles-reel/stickers/*.png (Noto Color Emoji, OFL)"
  transition-line:
    color: "{colors.flash}"
    width: "1.1cqw"
    angle: "-24deg"
    duration: "0.22s"
---

# FRAME.md — Inglés Reel, a escala de cuadro

> **La cara cuenta, el texto enseña.** Video a cámara en pantalla completa, cortado al hueso,
> con tipografía gruesa de contorno negro y **un solo color de acento (crema) para el inglés**.

## Overview

Reel educativo de ~40 s: una persona habla a cámara (selfie, auto, calle, shopping) y explica
cómo se dice una frase cotidiana en inglés. No hay B-roll ni fondos gráficos: **el A-roll es la
imagen todo el tiempo** y el diseño vive en los textos superpuestos, los stickers emoji y el corte.
Firmas no negociables:

1. **Jump cuts sin aire**: se eliminan todas las pausas, respiraciones, muletillas y tomas falsas.
   En el original no hay un solo silencio de más de 0,15 s después del primer segundo.
2. **Punch-ins**: el encuadre alterna entre normal (100 %) y cerrado (110–118 %) en cada corte,
   con un zoom fuerte en el momento clave (la frase del hook, el final). Así los cortes se ven a propósito
   y no como saltos.
3. **Texto blanco/crema, Poppins grueso, contorno negro grueso**: el inglés va en crema `#FADEB2`,
   el español en blanco. Nada más tiene color, salvo el rojo del error.
4. **El gag del error común**: cuando dice la traducción literal equivocada, la imagen pasa a
   **blanco y negro**, la voz suena **apagada (filtro pasa-bajos)** y aparece el texto equivocado **en rojo**.
   Vuelve a color de golpe con el "no".
5. **Transición línea blanca** (con un "click") entre la explicación y el ejemplo de cada expresión.

No es: motion graphics con fondos, tarjetas de colores, música de fondo ni subtítulos de cada palabra
todo el tiempo. Cuando el texto enseña algo (keyword, ejemplo), la narración no lleva subtítulo.

**Craft bar**

- **Squint test** — en cada momento manda UN bloque de texto (la keyword o el ejemplo), 3× más grande que cualquier otro.
- **Silence test** — el texto ocupa una banda (≈ 20–25 % de la altura); el resto es la persona.
- **Restraint test** — el crema solo marca inglés. El rojo solo marca el error. Un sticker por expresión.
- **Reference bar** — se tiene que leer en 1 s sin sonido. Falla si un texto tapa la cara, si hay pausas
  muertas, o si el texto aparece antes o después de que la voz lo diga.

## Estructura (plantilla de beats)

| # | Beat | Qué se ve | Duración típica |
|---|------|-----------|-----------------|
| 1 | **Hook — título** | Tarjeta blanca redondeada: «¡Frase en español!» (crema) / «In English» (blanco). Pop de entrada. | 0–1,5 s |
| 2 | **Hook — frase gigante** | Cuando la voz dice la frase: «¡No te soporto!» enorme y centrada, letra por letra, + punch-in fuerte. | 1–2 s |
| 3 | **Error común** | B&N + voz apagada + traducción literal en rojo con signo de pregunta («I don't support you?»). | 1–2,5 s |
| 4 | **Promesa** | Subtítulo palabra por palabra: «Te voy a dejar **3 maneras** de decirlo» (lo clave en crema). | 1,5–2,5 s |
| 5 | **Expresión N — keyword** | «Can't stand» (crema, grande) aparece cuando la dice; debajo el significado en blanco cuando lo explica. Sticker emoji que refuerza la emoción. | 2–4 s |
| 6 | **Transición** | Línea blanca diagonal que barre + blur 0,15 s + click. | 0,2 s |
| 7 | **Expresión N — ejemplo** | “I **can't stand** waiting in line” / “No soporto hacer fila”. La línea en español entra cuando la dice. | 3–4 s |
| … | repetir 5–7 por cada expresión (en el original: 3) | | |
| 8 | **CTA / cierre** | Subtítulo palabra por palabra con lo accionable en crema («guardá el video», «escribime») + sticker. Cierre en frase gigante (o loop al hook). | 3–8 s |

Duración total objetivo: **35–45 s**.

## Corte y ritmo

- **Quitar pausas** de más de ~0,25 s. Dejar 0,06 s antes de la primera sílaba y 0,10 s después de la última.
  Crossfade de audio de 15 ms en cada corte para que no haya clicks.
- **Muletillas y tomas falsas afuera**: "eh", "um", "okay", frases repetidas, "por ejemplo" que no lleva a nada.
  Si hay dos tomas del mismo texto, se queda la última completa.
- **Pausa dramática controlada**: antes de decir la expresión en inglés («La primera es… *can't stand*») se
  deja un respiro de 0,12–0,15 s; ese corte es el punch-in.
- **Encuadre por plano**: alternar escala 1.00 ↔ 1.10–1.14 en cada corte (cambio seco, sin easing). Punch-in
  fuerte (1.18–1.22) en la frase del hook y en el remate. Dentro de un plano largo (> 2,5 s) se permite
  un push lento 1.00 → 1.04, siempre con ease, nunca lineal ni con temblor.
- **Duración de plano**: 0,8–4 s. Nunca un plano fijo de más de 4 s sin un cambio (corte, zoom o texto nuevo).

## Textos (componentes)

Todo texto lleva **contorno exterior negro** (`paint-order: stroke fill`) + sombra suave; nunca caja de fondo
(excepto la tarjeta del título del hook).

- **Tarjeta del título (hook)** — blanca 94 %, esquinas 4,4cqw, sombra suave. Dos líneas centradas: frase en
  español en crema, «In English» en blanco, ambas con contorno negro. Entra con pop (escala 0,7 → 1,05 → 1).
- **Frase gigante** — Poppins 800 a 17cqw, blanca, contorno 2,2cqw, dos líneas centradas en la banda media/baja.
  Letras que aparecen de a una (stagger 35–45 ms, cada letra pop 0,6 → 1). Siempre con punch-in.
- **Keyword** — Poppins 800 a ~11,5cqw en crema. Pop de entrada. Si se cambia de expresión, la anterior sale
  hacia arriba (0,12 s) y la nueva cae desde arriba.
- **Significado** — Roboto 500 a ~7,6cqw en blanco, 1–2 líneas, justo debajo de la keyword. Entra palabra por palabra
  siguiendo la voz.
- **Ejemplo** — dos líneas entre comillas, Poppins 700 a ~5,6cqw con tracking apretado. Inglés arriba (blanco con
  la expresión en crema), español abajo (blanco). Cada línea entra cuando la voz la empieza (pop corto o palabra por palabra).
  Se permite un emoji al final de la línea en español.
- **Subtítulo de narración** — Poppins 700 a ~8,2cqw, blanco, palabra por palabra sincronizado (cada palabra aparece
  en su sílaba inicial), 1–3 líneas, centrado. Se usa solo en los tramos sin keyword/ejemplo (intro, promesa, CTA).
  La palabra importante va en crema.
- **Error (rojo)** — Poppins 800 a ~9cqw, rojo `#E3262E`, contorno blanco 1cqw + sombra. Entra con pop + leve sacudida.
- **Stickers** — emoji grandes (20–26cqw) al costado del bloque de texto. Entran con pop + rotación ±8°. Pueden
  **escalar en intensidad** (😠 → 😡 → 🤬) en tres pasos de 0,35 s para "llegar al límite".

### Dónde va el texto (regla de la cara)

El bloque de texto va en la **zona libre opuesta a la cara**, dentro de la zona segura de Reels
(**y 14–65 %, x 6–94 %**; debajo del 65 % están el usuario, la descripción y los botones):

- Cara en el centro o abajo del cuadro (cámara a la altura de los ojos, como en el original) → **banda superior** (15–32cqh).
- Cara en el tercio superior (selfie desde abajo, techo visible) → **banda del cuello/pecho** (49–65cqh).
  En ese caso el zoom de los punch-ins va con origen `50% 45%` para que el mentón no baje sobre el texto.
- La frase gigante del hook puede tapar el mentón un instante (el original lo hace), nunca los ojos.
- TikTok y Shorts tienen el borde derecho más estrecho abajo; si el reel se va a subir ahí también, achicar el texto
  de la banda del pecho para que termine antes del 72 % del ancho.

## Movimiento y timing

- Personalidad **punchy**: entradas con `back.out(2)` 0,16–0,22 s; salidas secas (corte o slide-up 0,12 s).
- **Sincronía con la voz** es la regla #1: cada palabra/línea aparece en el frame en que empieza a sonar (±2 frames).
- La keyword y su significado se quedan en pantalla hasta la transición al ejemplo.
- Transición entre explicación y ejemplo: línea blanca de 1,1cqw a −24° que cruza el cuadro en 0,22 s + blur
  de 6 px que vuelve a 0 en 0,15 s + "click".
- Gag del error: `grayscale(1) contrast(1.1)` durante toda la frase equivocada; vuelve a color de golpe.

## Audio

- **Solo voz**, limpia y al frente: high-pass 80 Hz, reducción de ruido suave, compresión leve, **−14 LUFS**,
  pico −1,5 dBTP. Sin música de fondo (el original no tiene).
- **Voz apagada en el error**: pasa-bajos ~1,4 kHz + −3 dB mientras dura el B&N.
- **SFX** (siempre por debajo de la voz, −20 a −14 dB): click corto en cada transición de línea blanca, pop suave
  cuando entra una keyword/sticker. Nada de whooshes largos ni risers.

## Do's and Don'ts

**Do**
- Cortar todas las pausas y alternar el encuadre en cada corte.
- Usar crema solo para el inglés; español siempre en blanco.
- Poner el significado debajo de la keyword y el ejemplo como par EN/ES entre comillas.
- Respetar las zonas seguras de Instagram y no tapar nunca la cara.
- Un sticker emoji por expresión, que refuerce la emoción (😢 emocional, 😡 límite).

**Don't**
- No dejar silencios, "eh", "okay" ni tomas falsas.
- No poner música de fondo ni cajas de color detrás del texto.
- No subtitular palabra por palabra mientras hay keyword o ejemplo en pantalla.
- No usar más de un color de acento, ni texto sin contorno.
- No usar zooms lineales o temblorosos; los punch-ins son secos y los push lentos llevan ease.

## Aspect ratio

Pensado para **9:16 (1080×1920)**. En 4:5 (1080×1350) se mantiene todo igual y la banda de texto se pega
al borde opuesto a la cara. Ningún texto de lectura baja de 5cqw.

## Cómo usarlo

Proyecto de ejemplo y builder reutilizable: `ingles/` en la raíz del repo
(`ingles/README.md`). Un reel nuevo = un `reel.json` (cortes + beats de texto) → `build_reel.py` → `hyperframes render`
→ `finalize.sh`.
