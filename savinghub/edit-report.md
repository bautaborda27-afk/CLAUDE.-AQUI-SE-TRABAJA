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
