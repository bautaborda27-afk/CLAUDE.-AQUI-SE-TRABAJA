"""Shared edit plan: cut times, transitions and effect hits for the short film.

fx_tracks.py / fx_film.py turn it into the film layer, build_comp.py into the
HyperFrames text layer and build_audio.py into work/master.m4a (music + SFX),
so picture, text and sound always land on the same frames.
"""

FPS = 30
FILM = 256.0          # source length (s)
END_CARD = 2.5        # black "FIN" card after the film
TOTAL = FILM + END_CARD


def f(n):
    """Frame index -> seconds."""
    return round(n / FPS, 4)


# Hard cuts in the source (see build_base.py). 5479 is the jump cut inside the
# "YA TE ENCONTRÉ" note shot.
C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13 = (
    f(n) for n in (773, 2255, 3120, 3529, 4299, 4732, 5479, 5627, 5953, 6476, 6896, 7232, 7465))
SHOTS = [0.0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, FILM]

# Transition per cut. kind: zoom | whip | flash | glitch | dip | slam | open | close
TRANSITIONS = [
    ("open",   0.0),               # eyes open: bars part, pixelated -> sharp, fade up
    ("zoom",   C1),                # hallway -> classroom
    ("pixel",  C2),                # classroom -> protagonist close-up (pixel reveal)
    ("whip",   C3, "left"),        # close-ups -> reading the note
    ("flash",  C4),                # note -> wide desk (exposure flash)
    ("glitch", C5),                # bench -> empty bench (time skip)
    ("dip",    C6),                # stalker walks by -> face (dark dip + punch)
    ("slam",   C7),                # jump cut on "YA TE ENCONTRÉ"
    ("whip",   C8, "right"),       # note -> face
    ("zoom",   C9),                # face -> bathroom sinks
    ("glitch", C10),               # sinks -> the stalker shows up
    ("whip",   C11, "left"),       # confrontation -> he runs
    ("whip",   C12, "up"),         # -> stairs
    ("zoom",   C13),               # -> wide corridor chase
    ("close",  FILM),              # bars close, FIN
]

WHIP_HALF = 0.2       # each side of a whip (s)

# Moments inside shots
STING = 51.9          # tonal sting in the music (51.9-53.9)
STING_END = 53.9
HIT = 222.0           # chase music kicks in

# Kinetic text over the two legible notes: (word, start, red)
NOTE1 = {"start": 97.4, "end": 100.9, "lines": [
    [("TE", 97.5, False), ("BUSQUÉ", 97.75, False)],
    [("POR", 98.2, False), ("MUCHO", 98.45, False)],
    [("TIEMPO", 98.9, True)],
]}
NOTE2 = {"start": 179.2, "end": C7, "lines": [
    [("¡YA", 179.3, False), ("TE", 179.55, False)],
    [("ENCONTRÉ!", 179.95, True)],
]}

HEARTBEATS = [174.4, 175.3, 176.15, 176.95, 177.7, 178.4, 179.05]

# Digital-glitch layer windows (start, end)
GLITCHES = [(C5 - 0.3, C5 + 0.3), (179.95, 180.25), (C7 - 0.18, C7 + 0.17),
            (C10 - 0.27, C10 + 0.28), (HIT, HIT + 0.25), (FILM - 0.55, FILM)]

# Camera-shake bursts: (start, duration, amplitude px, roll deg)
SHAKES = [(98.9, 0.4, 10, 0.3), (179.95, 0.6, 22, 0.8), (C7, 0.45, 16, 0.6),
          (C10, 0.5, 18, 0.6), (HIT, 1.0, 26, 0.9), (C12, 0.4, 14, 0.5),
          (C13, 0.4, 14, 0.5), (FILM - 0.4, 0.4, 20, 0.7)]
CHASE = (C11, FILM, 6, 0.25)   # continuous light handheld shake during the chase

FIN_AT = FILM + 0.35
