#!/usr/bin/env python3
"""Round 3b — the five motion-graphics reels with AI voiceover (Kokoro, ef_dora).

Same scenes as build_mg.VIDEOS; each scene gets one VO line and stretches to fit
it. With voice, the beat is removed (voice + animation SFX only). Output dirs
are the MG names with a "-voz" suffix. Brand names are spelled phonetically.
"""
import sys

import build_mg

VO = {
    "mg-01-decant-vs-frasco": [
        "¿Frasco entero, o decánt?",
        "Con el frasco pagás todo de una, y sin probarlo. Con un decánt pagás una fracción, "
        "lo probás en tu piel, y podés elegir varios.",
        "Lo sacamos directo del frasco original.",
        "Séiving Jab. Probá antes de comprar.",
    ],
    "mg-02-tres-pasos": [
        "Así se arma un decánt, en tres pasos.",
        "Uno: extraemos del frasco original, con jeringa.",
        "Dos: lo pasamos a un atomizador de vidrio.",
        "Tres: lo sellamos, y queda listo para usar.",
        "Séiving Jab. Tu decánt, listo para llevar.",
    ],
    "mg-03-ficha-jean-lowe": [
        "Ficha técnica: Yin Lou Inmortel.",
        "De Mesón Alhambra. Perfume de cien mililitros, fresco y cítrico, hecho en Emiratos Árabes.",
        "Fijate el holograma y el sello: así sabés que es original.",
        "Frasco completo: cien mililitros.",
        "Séiving Jab. Lujo sin pagar de más.",
    ],
    "mg-04-llego-tu-pedido": [
        "Pov: pediste un decánt de Bajarára King. Confirmado. Listo. Y llegó.",
        "Listo para usar, directo en tu piel.",
        "Séiving Jab. Pedilo hoy.",
    ],
    "mg-05-perfumes-arabes": [
        "Lujo, sin pagar de más.",
        "Yin Lou Inmortel, de Mesón Alhambra.",
        "Bajarára King.",
        "Frascos, y decánts.",
        "Perfumes árabes en Séiving Jab. Pedilo por mensaje.",
    ],
}

if __name__ == "__main__":
    for name in sys.argv[1:] or VO:
        spec = dict(build_mg.VIDEOS[name], vo=VO[name])
        build_mg.build(f"{name}-voz", spec)
