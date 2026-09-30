---
name: motion-elegante
description: Motion graphics lentos, elegantes y estéticos que se adaptan a la marca del cliente (colores, tipografías, logo) — elementos que entran y salen suave, íconos de línea que se dibujan solos (persona, lápiz, perfume y 5.166 más), títulos serif con palabra de acento en itálica, conteos, pasos, frases y cierre con logo + CTA. Renderiza con HyperFrames en vertical (Reels/TikTok), horizontal (YouTube) o cuadrado. Usar cuando pidan "motion graphics", "motion elegante/lindo/estético/premium", "animación con íconos", "video de marca", "reel animado sin cara", o un MG como los de SavingHub pero más cuidado. No usar para editar footage con voz (eso es /video-editing) ni subtítulos (/embedded-captions).
---

# Motion elegante

Genera un proyecto HyperFrames completo desde dos archivos JSON: la **marca** y el **guion de escenas**. El movimiento es siempre el mismo sistema (lento, suave, con entrada y salida); lo que cambia con cada cliente es la identidad visual.

## Flujo

1. **Marca** → `motion-elegante/marcas/<marca>/brand.json` (copiar de `brands/_plantilla.json`).
   Pedir o deducir: nombre, 5 colores, tipografías, logo. Si el cliente no tiene tipografías propias, usar las incluidas.
2. **Guion** → `motion-elegante/<proyecto>/spec.json` (ver `examples/spec-ejemplo.json`). Elegir escenas de la tabla de abajo; 4–7 escenas, 20–35 s en total.
3. **Íconos** → buscarlos con `python3 .claude/skills/motion-elegante/scripts/iconos.py persona lapiz perfume`.
4. **Generar** → `python3 .claude/skills/motion-elegante/scripts/build.py motion-elegante/<proyecto>/spec.json`
5. **Validar** → en la carpeta del proyecto: `npx --yes hyperframes@0.8.97 lint` (0 errores; las advertencias `nested_structure_needs_subcomposition` son sólo de organización en Studio).
6. **Revisar** → `npx --yes hyperframes@0.8.97 snapshot --at <mitad de cada escena> --no-end --describe false` y mirar `snapshots/contact-sheet.jpg`. Revisar que nada se corte, se pise o quede chico.
7. **Render** → `npx --yes hyperframes@0.8.97 render` → `renders/*.mp4`. Opcional: `node .claude/skills/video-editing/scripts/verify-render.mjs <mp4>`.
8. Después de cambiar código de la habilidad: `graphify update .`

## brand.json

```json
{
  "nombre": "Saving Hub",
  "colores": { "fondo": "#0D0C0B", "superficie": "#1A1817", "texto": "#F4EFE8", "acento": "#E0201B", "suave": "#9A928A" },
  "fuentes": {
    "titulo": { "archivo": "Anton.woff2", "italica": "cormorant-garamond-latin-500-italic.woff2" },
    "texto":  { "archivo": "manrope-latin-400-normal.woff2", "negrita": "manrope-latin-600-normal.woff2" }
  },
  "estilo": { "titulos_mayuscula": true },
  "logo": { "tipo": "icono", "icono": "perfume", "texto": "Saving Hub" }
}
```

- **colores**: `fondo` (base), `superficie` (detrás de fotos), `texto`, `acento` (UN solo color de marca: palabra en itálica, anillos, líneas), `suave` (textos secundarios). Buen contraste texto/fondo siempre.
- **fuentes**: `.woff2`. Se buscan primero en la carpeta de la marca y después en `assets/fonts/` (incluidas: Cormorant Garamond 500/600 normal+itálica, Manrope 400/600, Anton, JetBrains Mono Bold). `italica` es la fuente de la palabra de acento: una serif itálica queda elegante incluso con títulos en Anton.
- **logo**: `{"tipo":"texto"}` (sólo nombre), `{"tipo":"icono","icono":"feather"}` (ícono dibujado + nombre) o `{"tipo":"archivo","archivo":"logo.svg"}` (logo real del cliente, en la carpeta de la marca; preferir SVG o PNG transparente).

## spec.json

```json
{ "marca": "../marcas/savinghub/brand.json", "formato": "vertical", "etiqueta": "Perfumes árabes",
  "musica": "ambiente", "hud": true,
  "escenas": [ { "tipo": "titulo", "duracion": 4, "kicker": "…", "lineas": ["Lujo", "*sin pagar*", "de más"], "sub": "…" } ] }
```

`formato`: `vertical` 1080×1920 · `horizontal` 1920×1080 · `cuadrado` 1080×1080. `hud` muestra marca + etiqueta arriba y barra de progreso abajo.

`musica`: un archivo propio (se recorta al largo del video y se le hace fade) o `"ambiente"`, que sintetiza un colchón sonoro suave, libre de derechos, normalizado a volumen de fondo. Sin `musica` el video sale mudo, y en ese caso `verify-render.mjs` falla el chequeo de audio. Para Reels conviene cambiar el ambiente por música en tendencia al subirlo.

**Acento**: en cualquier texto, `*palabra*` sale en itálica y color de acento. Máximo una por escena.

| tipo | campos | duración por defecto | qué hace |
|---|---|---|---|
| `titulo` | `lineas` (lista), `kicker`, `sub` | 4 s | título grande línea por línea + línea de acento |
| `icono` | `icono`, `titulo`, `kicker`, `sub` | 4 s | un ícono grande que se dibuja dentro de un anillo |
| `iconos` | `titulo`, `items: [{icono, texto}]` (2–4), `kicker` | 5 s | varios íconos escalonados (columna en vertical, fila en horizontal) |
| `pasos` | `titulo`, `items: [{icono, texto}]` (3–5), `kicker` | 6 s | lista numerada con línea que la recorre |
| `dato` | `valor`, `texto`, `prefijo`, `sufijo`, `decimales`, `porcentaje` (0–1), `kicker` | 4 s | número que cuenta + anillo que se completa |
| `imagen` | `archivo` (.jpg/.png/.mp4), `titulo`, `sub`, `kicker` | 4.5 s | foto o video en un marco que se abre, con zoom lento |
| `frase` | `texto`, `autor` | 5 s | cita palabra por palabra |
| `cierre` | `tagline`, `cta` | 4.5 s | logo + nombre letra por letra + CTA |

Rutas de `archivo`/`musica` son relativas a la carpeta del proyecto (conviene `assets/`).

## Sistema de movimiento (no romperlo)

- **Lento**: entradas de 1.2–1.8 s con `expo.out`; nada rebota (`back`/`elastic` prohibidos).
- **Entra y sale**: cada bloque entra desenfocado → nítido y sale subiendo + desenfocándose en los últimos 0.9 s de su escena; los íconos se dibujan al entrar y se desdibujan al salir. Entre escenas queda un respiro de fondo vacío.
- **Respira**: cada escena crece 3 % durante toda su duración; la luz de fondo se desplaza muy lento.
- **Escalonado**: los elementos de una escena llegan en orden de lectura (kicker → título → detalle), nunca todos juntos.
- **Un acento por escena**, mucho aire, todo centrado. Grano y viñeta sutiles para textura.
- Si una escena se siente apurada, subir `duracion` antes que acortar animaciones.

## Reglas HyperFrames que el generador ya cumple

Un solo `gsap.timeline({paused:true})` en `window.__timelines["main"]`; nada aleatorio ni con reloj; no se animan `.clip` directamente; un `<video data-start>` nunca va dentro de otra escena con `data-start` (el video vive en una capa aparte alineada con la escena). Si se edita `index.html` a mano, se pierde al regenerar: cambiar el spec o `build.py`.

## Archivos

- `scripts/build.py` — generador (escenas = métodos de `Comp`; CSS en `css()`).
- `scripts/iconos.py` — buscador de íconos (español o inglés).
- `assets/icons/tabler-outline.json` — 5.166 íconos de línea Tabler (MIT).
- `assets/fonts/` — tipografías incluidas (OFL).
- `brands/_plantilla.json`, `examples/spec-ejemplo.json` — puntos de partida.
- Demos: `motion-elegante/demo-savinghub/` (vertical, oscuro) y `motion-elegante/demo-atelier/` (horizontal, claro).
