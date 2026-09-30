#!/usr/bin/env python3
"""Buscar íconos de línea (Tabler, 5.166) por nombre en inglés o palabra en español.

    python3 iconos.py perfume          # -> perfume, spray, bottle...
    python3 iconos.py persona lapiz    # varias palabras a la vez
"""
import json
import sys
import unicodedata
from pathlib import Path

ICONS = json.loads((Path(__file__).resolve().parent.parent / "assets/icons/tabler-outline.json").read_text())

ES = {
    "persona": ["user", "users", "man", "woman", "user-circle"], "gente": ["users", "users-group"],
    "lapiz": ["pencil", "pencil-heart", "writing", "edit"], "pincel": ["brush", "paint"],
    "perfume": ["perfume", "spray", "bottle", "droplet"], "gota": ["droplet", "droplets"],
    "regalo": ["gift", "gift-card"], "caja": ["package", "box"], "envio": ["truck", "truck-delivery", "package"],
    "bolsa": ["shopping-bag"], "carrito": ["shopping-cart"], "tienda": ["building-store"],
    "corazon": ["heart"], "estrella": ["star", "stars", "sparkles"], "brillo": ["sparkles", "diamond"],
    "diamante": ["diamond"], "corona": ["crown"], "hoja": ["leaf", "plant"], "flor": ["flower", "rosette"],
    "fuego": ["flame"], "reloj": ["clock", "hourglass"], "check": ["check", "circle-check", "rosette-discount-check"],
    "ubicacion": ["map-pin"], "telefono": ["phone"], "mensaje": ["message-circle", "brand-whatsapp"],
    "instagram": ["brand-instagram"], "whatsapp": ["brand-whatsapp"], "camara": ["camera"], "paleta": ["palette"],
    "tijera": ["scissors"], "regla": ["ruler"], "pluma": ["feather", "writing"], "luna": ["moon"], "sol": ["sun"],
    "cafe": ["coffee"], "casa": ["home"], "tarjeta": ["credit-card"], "precio": ["tag", "discount"],
    "rayo": ["bolt"], "objetivo": ["target"], "crecer": ["trending-up", "chart-bar"], "premio": ["award", "medal", "trophy"],
    "seguro": ["shield-check", "lock"], "mail": ["mail", "send"], "calendario": ["calendar"], "ojo": ["eye"],
    "mano": ["hand-finger", "hand-click"], "sonrisa": ["mood-smile"], "idea": ["bulb"], "cohete": ["rocket"],
    "libro": ["book"], "musica": ["music"], "microfono": ["microphone"], "video": ["video", "player-play"],
}


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


for word in sys.argv[1:] or ["perfume"]:
    w = norm(word)
    hits = [n for n in ES.get(w, []) if n in ICONS]
    hits += [n for n in ICONS if w in n and n not in hits]
    print(f"{word}: {', '.join(hits[:25]) or 'sin resultados (probá en inglés)'}")
