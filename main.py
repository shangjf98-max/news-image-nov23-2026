#!/usr/bin/env python3
"""One-day news image for Monday 23 November 2026 (make.fun news-image-20261123).

Draws a 1024x1024 newspaper front page with Python 3.13 standard library only.
No fonts, no image files, no network. Renders at 3x supersampling and
box-filters down to 1024x1024 so edges are anti-aliased.

Glyphs are hand-built vector strokes on a 10-wide / 14-tall grid
(cap height y 0..10, baseline y 10, descenders to y 13). The same stroke
data renders as serif (thick/thin contrast + automatic serif ticks on
vertical stems) or as clean sans (uniform stroke, no ticks).
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw

SS = 3                      # supersampling factor
W = H = 1024                # final size
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette
PAPER   = (247, 242, 231)   # warm newsprint
PAPER2  = (240, 233, 216)   # slightly darker panel
INK     = (26, 26, 34)      # near-black text
NAVY    = (20, 38, 77)      # dark blue panels
NAVY2   = (28, 52, 102)
RED     = (179, 38, 30)     # rules, stamps, emphasis
GOLD    = (201, 162, 39)
WHITE   = (250, 248, 243)
GREY    = (110, 108, 100)
LGREY   = (150, 147, 138)
SKY     = (140, 180, 210)
SEA     = (52, 96, 140)
GREEN   = (31, 122, 77)
AMBER   = (199, 127, 26)
PURPLE  = (122, 63, 160)
BLUE    = (46, 95, 163)
SLATE   = (90, 107, 122)
TEAL    = (32, 120, 118)

REGION_COLORS = {
    "AMERICAS": BLUE, "EUROPE": GREEN, "MIDDLE EAST": RED,
    "AFRICA": AMBER, "ASIA": PURPLE, "WORLD": SLATE,
}

# ------------------------------------------------------- vector glyph data
# Each glyph: list of items.  A stroke is ([(x, y), ...], width).
# A dot is ("c", cx, cy, r).  Grid: x 0..10, cap top y 0, baseline y 10.
def _st(pts, w):
    return (pts, w)

CAPS = {
"A": [([(1, 10), (5, 0), (9, 10)], 1.7), ([(3.2, 6.5), (6.8, 6.5)], 1.0)],
"B": [([(1, 0), (1, 10)], 1.7),
     ([(1, 0), (6, 0), (8, 1.5), (6.5, 4.8), (1, 4.8)], 1.1),
     ([(1, 5.2), (6.5, 5.2), (8.5, 7), (7, 10), (1, 10)], 1.1)],
"C": [([(8, 1.5), (5, 0), (2, 1.5), (1, 5), (2, 8.5), (5, 10), (8, 8.5)], 1.5)],
"D": [([(1, 0), (1, 10)], 1.7),
     ([(1, 0), (6, 0), (8.5, 2.5), (8.5, 7.5), (6, 10), (1, 10)], 1.2)],
"E": [([(1, 0), (1, 10)], 1.7), ([(1, 0), (8, 0)], 1.1),
     ([(1, 5), (6.5, 5)], 1.0), ([(1, 10), (8, 10)], 1.1)],
"F": [([(1, 0), (1, 10)], 1.7), ([(1, 0), (8, 0)], 1.1),
     ([(1, 5), (6.5, 5)], 1.0)],
"G": [([(8, 1.5), (5, 0), (2, 1.5), (1, 5), (2, 8.5), (5, 10), (8, 8.5),
        (8, 6), (5.5, 6)], 1.5)],
"H": [([(1, 0), (1, 10)], 1.7), ([(9, 0), (9, 10)], 1.7), ([(1, 5), (9, 5)], 1.0)],
"I": [([(5, 0), (5, 10)], 1.7), ([(2.5, 0), (7.5, 0)], 1.0),
     ([(2.5, 10), (7.5, 10)], 1.0)],
"J": [([(7, 0), (7, 8), (5, 10), (2.5, 10), (1, 8)], 1.5),
     ([(4.5, 0), (9.5, 0)], 1.0)],
"K": [([(1, 0), (1, 10)], 1.7), ([(8, 0), (2, 5.5), (8, 10)], 1.3)],
"L": [([(1, 0), (1, 10)], 1.7), ([(1, 10), (8, 10)], 1.1)],
"M": [([(1, 10), (1, 0), (5, 6), (9, 0), (9, 10)], 1.6)],
"N": [([(1, 10), (1, 0), (9, 10), (9, 0)], 1.6)],
"O": [([(5, 0), (8, 1.5), (9, 5), (8, 8.5), (5, 10), (2, 8.5), (1, 5),
        (2, 1.5), (5, 0)], 1.5)],
"P": [([(1, 0), (1, 10)], 1.7),
     ([(1, 0), (6.5, 0), (8.5, 2), (7, 5), (1, 5)], 1.2)],
"Q": [([(5, 0), (8, 1.5), (9, 5), (8, 8.5), (5, 10), (2, 8.5), (1, 5),
        (2, 1.5), (5, 0)], 1.5), ([(6, 7), (9.5, 11)], 1.1)],
"R": [([(1, 0), (1, 10)], 1.7),
     ([(1, 0), (6.5, 0), (8.5, 2), (7, 5), (1, 5)], 1.2),
     ([(5, 5.5), (9, 10)], 1.2)],
"S": [([(8, 1.5), (5.5, 0), (2.5, 0.8), (1.5, 3), (3, 5.2), (7, 5.8),
        (8.5, 8), (6, 10), (3, 10), (1.5, 8.5)], 1.4)],
"T": [([(1, 0), (9, 0)], 1.2), ([(5, 0), (5, 10)], 1.7)],
"U": [([(1, 0), (1, 7.5), (3, 10), (7, 10), (9, 7.5), (9, 0)], 1.6)],
"V": [([(1, 0), (5, 10), (9, 0)], 1.6)],
"W": [([(1, 0), (2.5, 10), (5, 4), (7.5, 10), (9, 0)], 1.6)],
"X": [([(1, 0), (9, 10)], 1.5), ([(9, 0), (1, 10)], 1.5)],
"Y": [([(1, 0), (5, 5.5), (9, 0)], 1.5), ([(5, 5.5), (5, 10)], 1.6)],
"Z": [([(1, 0), (9, 0), (1, 10), (9, 10)], 1.2)],
}

LOWER = {
"a": [([(7.5, 4.5), (4, 4), (2, 6), (2, 8), (4, 10), (7, 10), (8.5, 8),
        (8.5, 5)], 1.2), ([(8.5, 4), (8.5, 10)], 1.4)],
"b": [([(1.5, 0), (1.5, 10)], 1.6),
     ([(1.5, 5), (5, 4), (7.5, 6), (7, 9), (4, 10.5), (1.5, 9.5)], 1.2)],
"c": [([(8, 5.5), (5.5, 4), (3, 5), (2, 7.5), (3.5, 9.5), (6, 10), (8, 9)], 1.3)],
"d": [([(8.5, 0), (8.5, 10)], 1.6),
     ([(8.5, 5), (5, 4), (2.5, 6), (3, 9), (6, 10.5), (8.5, 9.5)], 1.2)],
"e": [([(8, 7), (6, 4), (3, 4.5), (1.8, 7), (3, 9.8), (6, 10), (8, 8.5)], 1.3),
     ([(1.8, 7), (8, 7)], 1.0)],
"f": [([(6, 4), (5, 1), (3, 2)], 1.3), ([(5, 0), (5, 10)], 1.5),
     ([(2.5, 5.5), (7.5, 5.5)], 1.0)],
"g": [([(7, 4.5), (4, 4), (2, 6), (2, 8), (4, 10), (7, 10), (8.5, 8),
        (8.5, 5)], 1.2),
     ([(8.5, 4), (8.5, 10), (7, 13), (4, 13), (2, 11)], 1.2)],
"h": [([(1.5, 0), (1.5, 10)], 1.6),
     ([(1.5, 5.5), (4, 4), (7, 4.5), (8, 6.5), (8, 10)], 1.3)],
"i": [([(5, 4), (5, 10)], 1.5), ("c", 5, 1.8, 1.0)],
"j": [([(6, 4), (6, 11), (4.5, 13), (2.5, 13)], 1.4), ("c", 6, 1.8, 1.0)],
"k": [([(1.5, 0), (1.5, 10)], 1.6), ([(7.5, 4), (3, 6.5), (8, 10)], 1.3)],
"l": [([(4.5, 0), (4.5, 10)], 1.6)],
"m": [([(1.5, 10), (1.5, 4)], 1.5), ([(1.5, 5), (4, 4), (6, 5.5), (6, 10)], 1.3),
     ([(6, 5), (8, 4), (9.5, 5.5), (9.5, 10)], 1.3)],
"n": [([(1.5, 10), (1.5, 4)], 1.5),
     ([(1.5, 5), (4, 4), (7, 4.5), (8.5, 6.5), (8.5, 10)], 1.3)],
"o": [([(5, 4), (7.5, 5), (8.5, 7), (7, 9.5), (5, 10), (2.5, 9.5),
        (1.5, 7), (2.5, 5), (5, 4)], 1.3)],
"p": [([(1.5, 4), (1.5, 13)], 1.6),
     ([(1.5, 5), (5, 4), (7.5, 6), (7, 9), (4, 10.5), (1.5, 9.5)], 1.2)],
"q": [([(8.5, 4), (8.5, 13)], 1.6),
     ([(8.5, 5), (5, 4), (2.5, 6), (3, 9), (6, 10.5), (8.5, 9.5)], 1.2)],
"r": [([(1.5, 10), (1.5, 4)], 1.5), ([(1.5, 5.5), (4, 4), (7, 4.5)], 1.2)],
"s": [([(7.5, 5.2), (5, 4), (2.5, 4.8), (1.8, 6.8), (3.5, 8.2), (6.5, 8.2),
        (7.5, 9.5), (5.5, 10.5), (3, 10.2)], 1.2)],
"t": [([(5, 0), (5, 10)], 1.5), ([(2.5, 5.5), (7.5, 5.5)], 1.0),
     ([(5, 10), (7, 11.5)], 1.1)],
"u": [([(1.5, 4), (1.5, 8), (3.5, 10), (6.5, 10), (8.5, 8), (8.5, 4)], 1.4)],
"v": [([(1, 4), (5, 10), (9, 4)], 1.4)],
"w": [([(1, 4), (2.5, 10), (5, 5.5), (7.5, 10), (9, 4)], 1.4)],
"x": [([(1.5, 4), (8.5, 10)], 1.3), ([(8.5, 4), (1.5, 10)], 1.3)],
"y": [([(1, 4), (5, 10), (9, 4)], 1.4), ([(5, 10), (7.5, 13), (8.5, 13)], 1.3)],
"z": [([(1.5, 4), (8.5, 4), (1.5, 10), (8.5, 10)], 1.2)],
}

DIGITS = {
"0": [([(5, 0), (8, 1.5), (9, 5), (8, 8.5), (5, 10), (2, 8.5), (1, 5),
        (2, 1.5), (5, 0)], 1.5)],
"1": [([(6, 0), (6, 10)], 1.7), ([(6, 0), (3, 2.5)], 1.1),
     ([(3.5, 10), (8.5, 10)], 1.0)],
"2": [([(1.5, 2), (4, 0), (7, 0), (8.5, 2), (8, 4.5), (3, 10), (9, 10)], 1.4)],
"3": [([(2, 0.5), (6, 0), (8, 2), (6, 4.5), (3, 5), (7, 5.5), (8.5, 7.5),
        (6.5, 10), (2.5, 10)], 1.4)],
"4": [([(7, 0), (7, 10)], 1.6), ([(1, 7), (7, 7)], 1.2), ([(7, 0), (1.5, 7)], 1.2)],
"5": [([(8, 0), (1.5, 0), (1.5, 4.5), (6, 4.5), (8.5, 7), (7, 10), (3, 10),
        (1.5, 8)], 1.4)],
"6": [([(8, 1), (6, 0), (2.5, 1.5), (1.5, 5), (2.5, 8.5), (5, 10), (7.5, 8.5),
        (8, 6), (6, 4.5), (3.5, 5)], 1.4)],
"7": [([(1.5, 0), (8.5, 0)], 1.2), ([(8.5, 0), (3, 10)], 1.4)],
"8": [([(5, 0), (7.5, 1.5), (8, 3.5), (6, 5), (4, 5), (2, 3.5), (2.5, 1.5),
        (5, 0)], 1.2),
     ([(5, 5), (7.5, 6.5), (8, 8), (6, 10), (4, 10), (2, 8), (2.5, 6.5),
       (5, 5)], 1.2)],
"9": [([(2, 9), (4, 10), (7.5, 8.5), (8.5, 5), (7.5, 1.5), (5, 0), (2.5, 1.5),
        (2, 4), (4, 5.5), (6.5, 5)], 1.4)],
}

PUNCT = {
" ": [],
".": [("c", 5, 9.6, 0.95)],
",": [("c", 5, 9.6, 0.95), ([(5, 10), (4, 12.2)], 1.0)],
":": [("c", 5, 4.2, 0.95), ("c", 5, 9.6, 0.95)],
";": [("c", 5, 4.2, 0.95), ("c", 5, 9.6, 0.95), ([(5, 10), (4, 12.2)], 1.0)],
"!": [([(5, 0), (5, 7.2)], 1.6), ("c", 5, 9.6, 1.0)],
"?": [([(2.5, 2.5), (4, 0.5), (7, 0.5), (8, 2.5), (7, 4.5), (5, 5.5), (5, 7)], 1.3),
     ("c", 5, 9.6, 1.0)],
"'": [([(5.5, 0), (4.5, 3.5)], 1.3)],
'"': [([(3, 0), (2.5, 3)], 1.3), ([(7, 0), (6.5, 3)], 1.3)],
"(": [([(7, 0), (4, 2.5), (4, 7.5), (7, 10)], 1.3)],
")": [([(3, 0), (6, 2.5), (6, 7.5), (3, 10)], 1.3)],
"-": [([(1.5, 6.5), (8.5, 6.5)], 1.1)],
"\u2013": [([(1, 6.5), (9, 6.5)], 1.1)],
"\u2014": [([(0.5, 6.5), (10.5, 6.5)], 1.1)],
"\u00b7": [("c", 5, 5.5, 0.85)],
"/": [([(8, 0), (2, 10)], 1.2)],
"%": [([(8.5, 0), (1.5, 10)], 1.1), ("c", 3, 2.5, 1.3), ("c", 7, 7.5, 1.3)],
"&": [([(7, 2), (4, 0), (2, 2), (3, 4.5), (7, 4.5), (8.5, 6.5), (5, 10),
        (2, 10)], 1.2)],
"$": [([(8, 1.5), (5.5, 0), (2.5, 0.8), (1.5, 3), (3, 5.2), (7, 5.8),
        (8.5, 8), (6, 10), (3, 10), (1.5, 8.5)], 1.3),
     ([(5, -0.5), (5, 11)], 1.0)],
"+": [([(5, 2), (5, 9)], 1.2), ([(1.5, 5.5), (8.5, 5.5)], 1.2)],
"=": [([(1.5, 4), (8.5, 4)], 1.1), ([(1.5, 7.5), (8.5, 7.5)], 1.1)],
"*": [([(5, 1), (5, 9)], 1.0), ([(1.5, 3.5), (8.5, 6.5)], 1.0),
     ([(8.5, 3.5), (1.5, 6.5)], 1.0)],
"#": [([(3, 0), (3, 10)], 1.0), ([(7, 0), (7, 10)], 1.0),
     ([(1, 3.5), (9, 3.5)], 1.0), ([(1, 7), (9, 7)], 1.0)],
}

GLYPHS = {}
GLYPHS.update(CAPS)
GLYPHS.update(LOWER)
GLYPHS.update(DIGITS)
GLYPHS.update(PUNCT)

# advance width per glyph (grid units), from ink extents, condensed
XS = 0.78  # horizontal condense factor: real serif is narrower than the grid
ADV = {}
for _ch, _items in GLYPHS.items():
    _mn, _mx = 10.0, 0.0
    for _it in _items:
        if _it[0] == "c":
            _mn = min(_mn, _it[1] - _it[3])
            _mx = max(_mx, _it[1] + _it[3])
        else:
            for (_px, _py) in _it[0]:
                _mn = min(_mn, _px)
                _mx = max(_mx, _px)
    ADV[_ch] = max(3.0, (_mx + 0.8) * XS + 0.8)
ADV[" "] = 3.8
ADV["."] = 4.6
ADV[","] = 4.6
ADV[":"] = 4.6
ADV[";"] = 4.6
ADV["!"] = 4.8
ADV["'"] = 4.2
ADV['"'] = 6.2
ADV["("] = 5.6
ADV[")"] = 5.6
ADV["-"] = 6.8
ADV["\u2013"] = 7.4
ADV["\u2014"] = 8.8
ADV["\u00b7"] = 4.4
ADV["/"] = 6.8
ADV["?"] = 7.2
ADV["i"] = 5.8
ADV["j"] = 5.8
ADV["l"] = 5.4
ADV["t"] = 6.8
ADV["f"] = 6.8
ADV["1"] = 7.4
ADV["I"] = 6.8

# ------------------------------------------------------------- font engine
# size = cap height in final (1024-scale) pixels.  u = grid unit in SS px.

def _clean(text):
    return (text.replace("\u2019", "'").replace("\u2018", "'")
                .replace("\u201c", '"').replace("\u201d", '"')
                .replace("\u00fa", "u").replace("\u00e9", "e")
                .replace("\u00fc", "u").replace("\u00e7", "c"))

def text_width(text, size, serif=True):
    """Width in final px of one line at cap-height `size`."""
    u = size / 10.0
    total = 0.0
    for ch in _clean(text):
        total += ADV.get(ch, 9.0)
    return total * u

def draw_glyph(dr, ox, base_y, u, items, color, serif):
    """Draw one glyph. ox, base_y in SS px; u = SS px per grid unit."""
    ux = u * XS  # condensed horizontal unit
    for it in items:
        if it[0] == "c":
            _, cx, cy, r = it
            x0 = ox + (cx - r) * ux
            y0 = base_y + (cy - 10 - r) * u
            x1 = ox + (cx + r) * ux
            y1 = base_y + (cy - 10 + r) * u
            dr.ellipse([x0, y0, x1, y1], fill=color)
            continue
        pts, w = it
        width = w if serif else 1.05
        lw = max(1, int(round(width * u)))
        xy = [(ox + px * ux, base_y + (py - 10) * u) for (px, py) in pts]
        dr.line(xy, fill=color, width=lw, joint="curve")
        if serif and len(pts) == 2 and w >= 1.25:
            (x1, y1), (x2, y2) = pts
            if abs(x1 - x2) < 0.01:  # vertical stem: add serif ticks
                tw = max(1, int(round(0.65 * u)))
                tick = 1.35 * ux
                for yy in (y1, y2):
                    cy = base_y + (yy - 10) * u
                    cx = ox + x1 * ux
                    dr.line([(cx - tick, cy), (cx + tick, cy)],
                            fill=color, width=tw)

def draw_text(dr, x, y, text, size, color, serif=True, align="l"):
    """Draw one line. x, y in final px; y = top of cap height."""
    text = _clean(text)
    w = text_width(text, size, serif)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    u = size / 10.0 * SS
    ox = x * SS
    base_y = (y + size) * SS
    for ch in text:
        items = GLYPHS.get(ch)
        if items is None:
            ch = "?"
            items = GLYPHS["?"]
        if items:
            draw_glyph(dr, ox, base_y, u, items, color, serif)
        ox += ADV.get(ch, 9.0) * u
    return w

def draw_text_italic(dr, x, y, text, size, color, serif=True, align="l"):
    """Fake italic: render on a layer, shear it, paste back."""
    text = _clean(text)
    w = text_width(text, size, serif)
    pad = int(size * 0.45) + 4
    lw = int((w + pad * 2) * SS)
    lh = int((size * 1.9) * SS)
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ldr = ImageDraw.Draw(layer)
    draw_text(ldr, pad, int(size * 0.35), text, size, color + (255,),
              serif=serif, align="l")
    shear = 0.18
    layer = layer.transform(
        (lw, lh), Image.AFFINE, (1, -shear, 0, 0, 1, 0),
        resample=Image.BICUBIC)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    px = int(x * SS) - int(pad * SS * 0.5)
    py = int(y * SS) - int(size * 0.35 * SS)
    dr._image.paste(layer, (px, py), layer)
    return w

def wrap_text(text, size, max_w, serif=True):
    """Greedy word wrap; returns list of lines."""
    words = _clean(text).split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, size, serif) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def draw_para(dr, x, y, lines, size, color, serif=True, lh=None, align="l"):
    if lh is None:
        lh = size * 1.28
    for ln in lines:
        draw_text(dr, x, y, ln, size, color, serif=serif, align=align)
        y += lh
    return y

# ---------------------------------------------------------------- painter
def shade(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)

class Page:
    def __init__(self):
        self.img = Image.new("RGB", (W * SS, H * SS), PAPER)
        self.dr = ImageDraw.Draw(self.img)

    # -- coordinates in final px, scaled internally
    def rect(self, x, y, w, h, fill, outline=None, ow=1):
        self.dr.rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS],
                          fill=fill, outline=outline,
                          width=max(1, int(ow * SS)) if outline else 1)

    def rrect(self, x, y, w, h, r, fill, outline=None):
        self.dr.rounded_rectangle(
            [x * SS, y * SS, (x + w) * SS, (y + h) * SS],
            radius=r * SS, fill=fill,
            outline=outline, width=max(1, SS) if outline else 1)

    def line(self, pts, fill, w=1):
        self.dr.line([(px * SS, py * SS) for (px, py) in pts], fill=fill,
                     width=max(1, int(w * SS)), joint="curve")

    def poly(self, pts, fill, outline=None):
        self.dr.polygon([(px * SS, py * SS) for (px, py) in pts],
                        fill=fill, outline=outline)

    def ellipse(self, x, y, w, h, fill, outline=None):
        self.dr.ellipse([x * SS, y * SS, (x + w) * SS, (y + h) * SS],
                        fill=fill, outline=outline)

    def circle(self, cx, cy, r, fill, outline=None):
        self.ellipse(cx - r, cy - r, 2 * r, 2 * r, fill, outline)

    def vgrad(self, x, y, w, h, c1, c2):
        """Vertical gradient (adds many intermediate shades)."""
        steps = max(2, int(h * SS / 4))
        for i in range(steps):
            t = i / (steps - 1)
            col = tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))
            self.rect(x, y + i * h / steps, w, h / steps + 1, col)

    def hline(self, x, y, w, fill, h=1):
        self.rect(x, y, w, h, fill)

    def text(self, x, y, s, size, color, serif=True, align="l"):
        return draw_text(self.dr, x, y, s, size, color, serif, align)

    def itext(self, x, y, s, size, color, serif=True, align="l"):
        return draw_text_italic(self.dr, x, y, s, size, color, serif, align)

    def para(self, x, y, lines, size, color, serif=True, lh=None, align="l"):
        return draw_para(self.dr, x, y, lines, size, color, serif, lh, align)

    def stamp(self, x, y, s, size, color, bg=None, angle=-7):
        """Small rotated label (like a rubber stamp). x, y = centre, final px."""
        w = text_width(s, size, serif=False) + size * 1.1
        h = size * 1.9
        lw, lh = int(w * SS), int(h * SS)
        layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        ldr = ImageDraw.Draw(layer)
        if bg is not None:
            ldr.rectangle([0, 0, lw - 1, lh - 1], fill=bg + (255,),
                          outline=color + (255,), width=max(1, SS))
        draw_text(ldr, size * 0.55, size * 0.42, s, size, color + (255,),
                  serif=False, align="l")
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
        px = int(x * SS - layer.width / 2)
        py = int(y * SS - layer.height / 2)
        self.img.paste(layer, (px, py), layer)

    def finish(self, path):
        small = self.img.resize((W, H), Image.BOX)
        # deterministic paper grain: seeded +-6 noise tile (adds colour depth)
        import random as _random
        from PIL import ImageChops as _IC
        rng = _random.Random(20261123)
        tile = Image.new("L", (128, 128))
        tile.putdata([128 + rng.randint(-6, 6) for _ in range(128 * 128)])
        noise = Image.new("L", (W, H))
        for ty in range(0, H, 128):
            for tx in range(0, W, 128):
                noise.paste(tile, (tx, ty))
        bands = []
        for band in small.split():
            bands.append(_IC.add(band, noise, scale=1.0, offset=-128))
        small = Image.merge("RGB", bands)
        small.save(path, "PNG", optimize=True)
        return small

# ------------------------------------------------------------ illustrations
# Every scene draws place + subject + action + a text label, inside the
# given box (final px).  A number badge and a place strip are added by
# the caller via art_label().

def art_label(pg, x, y, w, h, num, place):
    """Bottom place strip + top-left number badge over a finished scene."""
    pg.rect(x, y + h - 13, w, 13, (20, 20, 26))
    pg.text(x + 5, y + h - 11.5, place, 9.5, WHITE, serif=False)
    pg.circle(x + 13, y + 12, 10, RED)
    pg.text(x + 13, y + 3.5, str(num), 12, WHITE, serif=False, align="c")

def _windows(pg, x, y, w, h, cols, rows, lit):
    for r in range(rows):
        for c in range(cols):
            wx = x + 4 + c * ((w - 8) / cols)
            wy = y + 4 + r * ((h - 8) / rows)
            pg.rect(wx, wy, (w - 8) / cols - 3, (h - 8) / rows - 3,
                    GOLD if lit[(r * cols + c) % len(lit)] else (60, 70, 95))

# ---- leads (w ~324, h ~118) ----
def art_nvidia(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, NAVY, shade(NAVY, 0.8))
    for i, bh in enumerate((34, 52, 26, 44)):
        bx = x + 14 + i * 30
        pg.rect(bx, y + h - 14 - bh, 20, bh, (24, 48, 92))
        _windows(pg, bx, y + h - 14 - bh, 20, bh, 2, 3, (1, 0, 1))
    pg.rect(x + 150, y + 10, 160, h - 22, (16, 30, 62))
    bars = [10, 17, 14, 24, 32, 42]
    for i, bh in enumerate(bars):
        pg.rect(x + 162 + i * 24, y + h - 8 - bh, 15, bh, GREEN if i == 5 else GOLD)
    pg.line([(x + 162, y + h - 18), (x + 210, y + h - 34), (x + 258, y + h - 32),
             (x + 300, y + 16)], (120, 220, 140), w=3)
    pg.poly([(x + 300, y + 16), (x + 288, y + 14), (x + 298, y + 26)], (120, 220, 140))
    pg.stamp(x + w - 52, y + 22, "+31%", 15, WHITE, bg=GREEN, angle=-6)

def art_libya(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (24, 34, 58), shade((24, 34, 58), 0.8))
    for sx in (30, 90, 160, 240, 300):
        pg.circle(x + sx, y + 14 + (sx % 23), 1.6, WHITE)
    pg.rect(x, y + h - 34, w, 34, SEA)
    pg.line([(x, y + h - 34), (x + w, y + h - 34)], (120, 170, 200), w=2)
    pg.poly([(x + 60, y + h - 34), (x + 70, y + h - 62), (x + 74, y + h - 62),
             (x + 78, y + h - 48), (x + 200, y + h - 48), (x + 210, y + h - 34)],
            (70, 78, 88))
    pg.rect(x + 120, y + h - 76, 26, 30, (88, 96, 108))
    pg.line([(x + 133, y + h - 76), (x + 133, y + h - 92)], (88, 96, 108), w=3)
    pg.circle(x + 218, y + h - 44, 13, (255, 150, 40))
    pg.circle(x + 218, y + h - 44, 7, (255, 210, 90))
    for ang in range(0, 360, 45):
        import math
        dx = math.cos(math.radians(ang)) * 14
        dy = math.sin(math.radians(ang)) * 14
        pg.line([(x + 218, y + h - 44), (x + 218 + dx, y + h - 44 + dy)],
                (255, 150, 40), w=2)
    pg.circle(x + 250, y + h - 44, 8, (120, 120, 126))
    pg.circle(x + 262, y + h - 52, 6, (140, 140, 146))
    pg.poly([(x + 30, y + h - 22), (x + 44, y + h - 26), (x + 58, y + h - 22)],
            (40, 44, 52))
    pg.line([(x + 30, y + h - 20), (x + 90, y + h - 12)], (160, 190, 210), w=1)
    pg.stamp(x + w - 56, y + 20, "7 DRONES", 12, WHITE, bg=RED, angle=-6)

def art_eu(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (24, 52, 112), shade((24, 52, 112), 0.8))
    import math
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        pg.circle(x + 58 + math.cos(ang) * 22, y + 30 + math.sin(ang) * 22,
                  2.8, GOLD)
    pg.circle(x + 58, y + 30, 9, GOLD)
    pg.text(x + 58, y + 24, "EU", 10, NAVY, serif=False, align="c")
    pg.rect(x + 150, y + h - 40, 150, 40, (232, 226, 210))
    pg.rect(x + 150, y + h - 48, 150, 8, (200, 192, 172))
    for cx in range(158, 296, 24):
        pg.rect(cx, y + h - 34, 6, 28, (120, 112, 96))
    pg.rect(x + 150, y + h - 34, 150, 6, (120, 112, 96))
    pg.text(x + 225, y + h - 28, "BANK", 11, NAVY, serif=False, align="c")
    pg.stamp(x + w - 58, y + 22, "60 BANKS", 12, WHITE, bg=RED, angle=-6)
    pg.text(x + w - 8, y + 4, "22ND PACKAGE", 10, WHITE, serif=False,
            align="r")

# ---- cards (w ~241, h ~50) ----
def art_dymer(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (22, 26, 48), shade((22, 26, 48), 0.8))
    pg.circle(x + w - 22, y + 10, 6, (220, 220, 200))
    pg.rect(x + 14, y + 8, 74, h - 8, (150, 138, 112))
    _windows(pg, x + 14, y + 8, 74, h - 8, 4, 3, (1, 0, 1, 1, 0, 1))
    pg.poly([(x + 88, y + 8), (x + 118, y + 8), (x + 112, y + 20),
             (x + 100, y + 16), (x + 92, y + 26), (x + 88, y + 18)], (90, 82, 66))
    pg.line([(x + 130, y + 6), (x + 170, y + 22), (x + 205, y + 22)], GOLD, w=2)
    pg.line([(x + 170, y + 22), (x + 170, y + 38)], GOLD, w=1)
    pg.circle(x + 200, y + 30, 9, (255, 170, 60))
    pg.circle(x + 200, y + 30, 4, (255, 220, 120))
    pg.text(x + w - 6, y + 2, "11 DEAD", 11, WHITE, serif=False, align="r")

def art_gomez(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (214, 206, 188), shade((214, 206, 188), 0.8))
    pg.poly([(x + 70, y + 6), (x + 110, y + 6), (x + 118, y + 22),
             (x + 62, y + 22)], WHITE)
    pg.rect(x + 62, y + 22, 56, 6, WHITE)
    for cx in range(66, 116, 12):
        pg.rect(cx, y + 28, 4, 14, WHITE)
    pg.rect(x + 58, y + 42, 64, 4, WHITE)
    pg.rect(x + 150, y + 30, 60, 12, (120, 84, 52))
    pg.line([(x + 150, y + 24), (x + 210, y + 24)], (120, 84, 52), w=3)
    pg.stamp(x + 196, y + 14, "RESIGNS", 11, WHITE, bg=RED, angle=-8)
    pg.text(x + 28, y + 4, "DEC 1", 11, RED, serif=False)

def art_megaspeed(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (18, 24, 44), shade((18, 24, 44), 0.8))
    pg.rect(x + 60, y + 8, 90, 28, (30, 44, 66))
    for px in range(66, 146, 12):
        pg.line([(x + px, y + 8), (x + px, y + 4)], GOLD, w=2)
        pg.line([(x + px, y + 36), (x + px, y + 40)], GOLD, w=2)
    pg.rect(x + 92, y + 18, 26, 10, GOLD)
    pg.text(x + 105, y + 21, "AI", 9, NAVY, serif=False, align="c")
    pg.circle(x + 200, y + 25, 14, RED)
    pg.line([(x + 190, y + 15), (x + 210, y + 35)], WHITE, w=3)
    pg.line([(x + 210, y + 15), (x + 190, y + 35)], WHITE, w=3)
    pg.text(x + 28, y + 4, "SINGAPORE", 10, WHITE, serif=False)
    pg.text(x + w - 8, y + 2, "ENTITY LIST", 10, GOLD, serif=False, align="r")

def art_treasury(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (232, 226, 210), shade((232, 226, 210), 0.8))
    pg.poly([(x + 70, y + 4), (x + 120, y + 4), (x + 132, y + 16),
             (x + 58, y + 16)], (200, 192, 172))
    for cx in range(66, 126, 14):
        pg.rect(cx, y + 16, 5, 22, (150, 142, 122))
    pg.rect(x + 58, y + 38, 74, 5, (150, 142, 122))
    pg.circle(x + 170, y + 26, 12, GOLD)
    pg.text(x + 170, y + 18, "$", 14, NAVY, serif=False, align="c")
    pg.circle(x + 196, y + 34, 8, GOLD)
    pg.circle(x + 210, y + 40, 6, GOLD)
    pg.stamp(x + 205, y + 12, "24+", 11, WHITE, bg=RED, angle=-7)

def art_trumpeo(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (206, 216, 228), shade((206, 216, 228), 0.8))
    pg.rect(x + 20, y + 14, 70, 28, WHITE)
    pg.poly([(x + 38, y + 2), (x + 72, y + 2), (x + 76, y + 14), (x + 34, y + 14)],
            WHITE)
    for cx in range(28, 84, 12):
        pg.rect(cx, y + 22, 4, 18, (180, 186, 196))
    pg.rect(x + 110, y + 8, 64, 34, WHITE)
    for ly in range(14, 38, 6):
        pg.line([(x + 116, y + ly), (x + 168, y + ly)], LGREY, w=1)
    pg.line([(x + 178, y + 40), (x + 196, y + 12)], INK, w=2)
    pg.stamp(x + 200, y + 12, "ORDER", 11, WHITE, bg=RED, angle=-7)

def art_belgium(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (168, 196, 220), shade((168, 196, 220), 0.8))
    pg.rect(x + 14, y + 26, 60, 16, (140, 150, 160))
    pg.rect(x + 34, y + 6, 8, 22, (140, 150, 160))
    pg.poly([(x + 100, y + 20), (x + 150, y + 20), (x + 158, y + 26),
             (x + 96, y + 26)], WHITE)
    pg.poly([(x + 148, y + 20), (x + 168, y + 12), (x + 168, y + 26)], WHITE)
    pg.line([(x + 100, y + 32), (x + 160, y + 32)], (120, 128, 136), w=1)
    for i in range(6):
        pg.circle(x + 190 + i * 8, y + 38, 2.5, INK)
    pg.text(x + w - 8, y + 2, "404 FLIGHTS", 11, RED, serif=False, align="r")
    pg.line([(x + 96, y + 12), (x + 172, y + 34)], RED, w=3)

def art_cucuta(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (30, 38, 66), shade((30, 38, 66), 0.8))
    pg.rect(x + 12, y + 16, 70, 26, (52, 96, 140))
    pg.rect(x + 12, y + 10, 70, 6, (30, 60, 96))
    pg.text(x + 47, y + 20, "POLICE", 10, WHITE, serif=False, align="c")
    pg.rect(x + 100, y + 30, 34, 12, (150, 138, 112))
    pg.rect(x + 140, y + 32, 30, 10, (170, 158, 132))
    pg.poly([(x + 100, y + 30), (x + 117, y + 20), (x + 134, y + 30)], (120, 60, 50))
    pg.circle(x + 200, y + 14, 7, (255, 150, 40))
    pg.circle(x + 200, y + 14, 3, (255, 220, 120))
    pg.line([(x + 196, y + 20), (x + 190, y + 30)], (200, 200, 200), w=1)
    pg.text(x + w - 6, y + 2, "60 HOMES", 10, GOLD, serif=False, align="r")

def art_nhs(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (226, 236, 240), shade((226, 236, 240), 0.8))
    pg.rect(x + 12, y + 12, 70, 30, WHITE)
    pg.rect(x + 40, y + 16, 14, 22, RED)
    pg.rect(x + 33, y + 23, 28, 8, RED)
    pg.rect(x + 100, y + 8, 84, 34, (20, 30, 48))
    for i in range(8):
        pg.circle(x + 110 + i * 9, y + 18 + (i % 3) * 7, 2.2,
                  (120, 200, 220) if i % 2 else WHITE)
    pg.text(x + 142, y + 30, "AI", 11, GOLD, serif=False, align="c")
    for sx, sy in ((200, 8), (212, 20), (222, 6)):
        pg.line([(x + sx - 3, y + sy), (x + sx + 3, y + sy)], GOLD, w=1)
        pg.line([(x + sx, y + sy - 3), (x + sx, y + sy + 3)], GOLD, w=1)
    pg.text(x + 28, y + 2, "700,000", 10, NAVY, serif=False)

def art_wwc(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (32, 96, 60), shade((32, 96, 60), 0.8))
    pg.poly([(x + 10, y + 34), (x + 120, y + 34), (x + 230, y + 34),
             (x + 210, y + 12), (x + 30, y + 12)], (60, 130, 90))
    for fx in (30, 80, 130, 180, 220):
        pg.line([(x + fx, y + 12), (x + fx, y + 2)], WHITE, w=2)
        pg.circle(x + fx, y + 2, 2.5, GOLD)
    pg.poly([(x + 150, y + 16), (x + 166, y + 16), (x + 162, y + 30),
             (x + 154, y + 30)], GOLD)
    pg.rect(x + 152, y + 12, 12, 4, GOLD)
    pg.circle(x + 52, y + 24, 9, WHITE)
    pg.circle(x + 52, y + 24, 3, INK)
    pg.text(x + w - 8, y + 18, "2035", 13, WHITE, serif=False, align="r")

def art_mnf(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (38, 110, 62), shade((38, 110, 62), 0.8))
    for lx in range(20, 230, 26):
        pg.line([(x + lx, y + 4), (x + lx, y + h - 4)], (220, 230, 220), w=1)
    pg.line([(x + 30, y + 8), (x + 30, y + h - 8)], WHITE, w=2)
    pg.line([(x + 30, y + 8), (x + 44, y + 8)], GOLD, w=2)
    pg.line([(x + 30, y + h - 8), (x + 44, y + h - 8)], GOLD, w=2)
    pg.line([(x + 200, y + 8), (x + 200, y + h - 8)], WHITE, w=2)
    pg.ellipse(x + 118, y + 18, 34, 18, (122, 82, 40))
    pg.line([(x + 128, y + 27), (x + 142, y + 27)], WHITE, w=1)
    pg.rect(x + 160, y + 4, 66, 14, (20, 20, 26))
    pg.text(x + 193, y + 6, "22-20", 11, WHITE, serif=False, align="c")

def art_westbank(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (232, 214, 178), shade((232, 214, 178), 0.8))
    pg.rect(x + 12, y + 18, 56, 24, (190, 168, 128))
    pg.poly([(x + 12, y + 18), (x + 40, y + 6), (x + 68, y + 18)], (150, 90, 60))
    pg.rect(x + 84, y + 22, 48, 20, (200, 178, 138))
    pg.line([(x + 160, y + 42), (x + 160, y + 18)], (110, 84, 52), w=3)
    pg.circle(x + 152, y + 12, 9, (90, 130, 70))
    pg.circle(x + 168, y + 14, 8, (110, 150, 80))
    pg.poly([(x + 196, y + 42), (x + 206, y + 22), (x + 212, y + 32),
             (x + 218, y + 18), (x + 226, y + 42)], (255, 120, 30))
    pg.circle(x + 210, y + 40, 5, (255, 180, 60))
    pg.stamp(x + 46, y + 12, "ARSON", 10, WHITE, bg=RED, angle=-8)

def art_kenya(pg, x, y, w, h):
    pg.vgrad(x, y, w, h, (140, 180, 210), shade((140, 180, 210), 0.8))
    pg.circle(x + 120, y + 14, 12, (255, 210, 90))
    for i, col in enumerate(((20, 20, 20), (179, 38, 30), (31, 122, 77))):
        pg.rect(x + 24, y + 10 + i * 7, 66, 7, col)
    pg.rect(x + 24, y + 10, 66, 21, None, outline=WHITE)
    pg.rect(x + 150, y + 10, 66, 21, (30, 90, 160))
    pg.poly([(x + 183, y + 12), (x + 185, y + 17), (x + 190, y + 17),
             (x + 186, y + 20), (x + 188, y + 25), (x + 183, y + 22),
             (x + 178, y + 25), (x + 180, y + 20), (x + 176, y + 17),
             (x + 181, y + 17)], GOLD)
    pg.text(x + 120, y + 2, "TIES RESTORED", 10, NAVY, serif=False, align="c")

# ------------------------------------------------------------------ data
MARGIN = 14
CW = W - 2 * MARGIN  # 996

TAG_COLORS = {"CONFIRMED": GREEN, "OFFICIAL": NAVY, "REPORTED": AMBER,
              "CLAIM": RED}

LEADS = [
    dict(num=1, place="SANTA CLARA, US", region="AMERICAS", field="TECH",
         tag="CONFIRMED", art=art_nvidia,
         headline="Nvidia reinstates Huang as CEO; shares soar 31%",
         deck=("Board votes unanimously Monday, 11 days after his resignation; "
               "Trump says he 'convinced' the board."),
         source="Nvidia statement · Reuters · CNN"),
    dict(num=2, place="BENGHAZI, LIBYA", region="AFRICA", field="WAR",
         tag="REPORTED", art=art_libya,
         headline="Zelensky confirms sea drones sank Russian corvette off Libya",
         deck=("Seven Ukrainian naval drones hit the Merkury; a Ka-27 helicopter "
               "aboard destroyed; MV Angara also hit."),
         source="CNN · WSJ · The Times · Le Monde"),
    dict(num=3, place="BRUSSELS, EU", region="EUROPE", field="SANCTIONS",
         tag="OFFICIAL", art=art_eu,
         headline="EU proposes 22nd Russia sanctions, 60 banks off SWIFT",
         deck=("Von der Leyen unveils package Monday: about 60 banks cut from "
               "SWIFT, crypto crackdown, 70+ ships."),
         source="European Commission · Reuters · AP"),
]

CARDS = [
    dict(num=4, place="DYMER, UKRAINE", region="EUROPE", field="WAR",
         tag="CONFIRMED", art=art_dymer,
         headline="Dymer toll rises to 11; boy pulled alive from rubble",
         deck=("Rescuers recover 11th body Monday; boy Davyd, 7, freed after 14 hours."),
         source="Kyiv region admin · CNN"),
    dict(num=5, place="WASHINGTON, US", region="AMERICAS", field="POLITICS",
         tag="OFFICIAL", art=art_gomez,
         headline="Gomez to quit Congress on 1 Dec after ethics report",
         deck=("Ethics finds unwanted advances to a staffer; Gomez disputes it, will resign."),
         source="House Ethics Committee · AP"),
    dict(num=6, place="SINGAPORE", region="ASIA", field="TRADE",
         tag="CONFIRMED", art=art_megaspeed,
         headline="US blacklists Singapore's Megaspeed",
         deck=("Commerce adds the Nvidia customer to the entity list over chip diversion."),
         source="Semafor · Commerce Dept"),
    dict(num=7, place="WASHINGTON, US", region="AMERICAS", field="SANCTIONS",
         tag="OFFICIAL", art=art_treasury,
         headline="Treasury hits dozens in Iran shadow-banking",
         deck=("US sanctions 24+ entities in shadow banking; 'last lifeline' cut, US says."),
         source="US Treasury · Reuters"),
    dict(num=8, place="WASHINGTON, US", region="AMERICAS", field="POLITICS",
         tag="CONFIRMED", art=art_trumpeo,
         headline="Trump limits Congress access to agency files",
         deck=("Lawmakers must show a valid purpose to get agency and contractor files."),
         source="Politico · The Hill"),
    dict(num=9, place="BRUSSELS, BELGIUM", region="EUROPE", field="TRANSPORT",
         tag="CONFIRMED", art=art_belgium,
         headline="Belgium strike grounds flights as 50,000 march",
         deck=("Controllers join strike; airspace shut 07:00-21:00, 404 flights cancelled."),
         source="Skeyes · Brussels Airport"),
    dict(num=10, place="CUCUTA, COLOMBIA", region="AMERICAS", field="CONFLICT",
         tag="CONFIRMED", art=art_cucuta,
         headline="Drones hit Cucuta police base, 60 homes damaged",
         deck=("Drones strike a police base about 02:30; 2-3 hurt; a second hit in Cesar."),
         source="AP · Daily Summary"),
    dict(num=11, place="CAMBRIDGE, UK", region="EUROPE", field="HEALTH",
         tag="OFFICIAL", art=art_nhs,
         headline="NHS starts AI breast trial for 700,000 women",
         deck=("EDITH begins at Cambridge; AI replaces one of two human mammogram readers."),
         source="NHS England · BBC"),
    dict(num=12, place="LONDON, UK", region="EUROPE", field="SPORT",
         tag="CONFIRMED", art=art_wwc,
         headline="UK confirmed as host of 2035 Women's World Cup",
         deck=("FIFA decision Monday; England, Scotland, Wales and N. Ireland to host."),
         source="FIFA · BBC"),
    dict(num=13, place="WASHINGTON, US", region="AMERICAS", field="SPORT",
         tag="CONFIRMED", art=art_mnf,
         headline="Commanders walk off Bengals 22-20 on Monday",
         deck=("Daniels leads a final-minute winning drive; Bengals fall to 7-3."),
         source="theScore · NFL"),
    dict(num=14, place="WEST BANK", region="MIDDLE EAST", field="POLITICS",
         tag="CONFIRMED", art=art_westbank,
         headline="Israeli leaders call settler arson 'terrorism'",
         deck=("Herzog calls settler violence an 'assault on God himself'."),
         source="Reuters · Times of Israel"),
    dict(num=15, place="NAIROBI / KINSHASA", region="AFRICA", field="DIPLOMACY",
         tag="REPORTED", art=art_kenya,
         headline="Kenya and DR Congo restore ties",
         deck=("Ruto and Tshisekedi agree to restore ties after tensions over E. Congo."),
         source="Daily Summary"),
]

BRIEFS = [
    (16, "Trump halts Iowa blast", "Axios"),
    (17, "Democrats plan 12 debates", "CBS"),
    (18, "FAA halts O'Hare flights", "FAA"),
    (19, "States sue HUD on aid rule", "AP"),
    (20, "ICE need not unmask", "Court"),
    (21, "US eyes Iran ship attacks", "WSJ"),
    (22, "GOP may cut war funds", "WaPo"),
    (23, "Parties hit Huang return", "WSJ"),
    (24, "Iran vows 'all means'", "Reuters"),
    (25, "Israeli strikes kill 3", "AJ"),
    (26, "Hormuz oil falls", "FT"),
    (27, "UN urges Benghazi probe", "UN"),
    (28, "Guterres urges AI rules", "UN"),
    (29, "Mexico to try El Chapo", "AG"),
    (30, "NBA: Pacers 125-120", "NBA"),
    (31, "NHL: Devils 3-2 Jackets", "NHL"),
    (32, "Burnham: no EU referendum", "BBC"),
    (33, "Vance sidesteps war query", "NBC"),
    (34, "Likud-Yashar talks resume", "AFP"),
    (35, "Canada: no Hegseth memo", "Ottawa"),
    (36, "Asian tech slides", "Markets"),
]

NUMBERS = [
    ("31%", "Nvidia shares up Monday, best day since 2003"),
    ("$952bn", "Nvidia market value added, largest one-day gain ever"),
    ("60", "Russian banks to be cut from SWIFT in EU package"),
    ("700,000", "women to join the NHS EDITH breast screening trial"),
    ("404", "flights cancelled at Brussels Airport in the strike"),
    ("11", "dead in Dymer apartment strike; toll confirmed"),
]

TIMELINE = [
    ("05:20", "Dymer toll at 11"),
    ("06:00", "Belgium airspace out"),
    ("07:30", "Drones hit Cucuta"),
    ("14:00", "Huang back at Nvidia"),
    ("Afternoon", "EU unveils sanctions"),
    ("21:00", "Nasdaq +6.5%"),
    ("22:29", "Gomez to resign"),
]

REGIONS = [("AMERICAS", 19, BLUE), ("EUROPE", 6, GREEN),
           ("MIDDLE EAST", 5, RED), ("AFRICA", 3, AMBER),
           ("ASIA", 2, PURPLE), ("WORLD", 1, SLATE)]

DATE_CHECK = ("Every story here happened or was first reported on Monday 23 November "
    "2026 (UTC). Left out as earlier news: COP31 ends without a deal (22 Nov) · "
    "186 drones over Ukraine (22 Nov) · Hong Kong 98.79% turnout (22 Nov) · "
    "Verstappen wins Las Vegas GP (22 Nov) · Skubal $450m Mets deal (22 Nov) · "
    "Riemann proof released (20 Nov) · FBI database hack (20 Nov) · 'El Chapo "
    "Isidro' captured (20-21 Nov) · Miley Cyrus wedding (21 Nov).")

# map: land ellipses (x, y, w, h) in a 300x138 box; pins (story num, x, y)
LAND = [(14, 14, 78, 40), (64, 64, 38, 52), (136, 10, 34, 30),
        (138, 52, 44, 48), (182, 10, 102, 44), (252, 92, 42, 28),
        (196, 60, 36, 24)]
PINS = [(1, 32, 24), (2, 158, 58), (3, 162, 14), (4, 176, 26),
        (5, 48, 44), (6, 248, 78), (7, 66, 26), (8, 38, 54),
        (9, 148, 34), (10, 70, 76), (11, 132, 12), (12, 146, 20),
        (13, 74, 48), (14, 168, 52), (15, 172, 84)]

# ------------------------------------------------------------------ layout
def tag_chip(pg, x, y, tag):
    col = TAG_COLORS[tag]
    w = text_width(tag, 8.5, serif=False) + 10
    pg.rrect(x, y, w, 12, 2, col)
    pg.text(x + w / 2, y + 1.2, tag, 8.5, WHITE, serif=False, align="c")
    return w

def build():
    pg = Page()
    pg.vgrad(0, 0, W, H, (250, 245, 234), (243, 236, 220))
    # --- top bar
    pg.vgrad(0, 0, W, 20, NAVY, shade(NAVY, 0.7))
    pg.text(MARGIN, 4.5, "THE WORLD IN ONE DAY", 11, GOLD, serif=False)
    pg.text(W - MARGIN, 4.5, "36 STORIES · 6 REGIONS · 12 FIELDS", 11, WHITE,
            serif=False, align="r")
    # --- masthead
    pg.text(W / 2, 22, "Monday 23 November 2026", 42, INK, serif=True, align="c")
    pg.hline(MARGIN, 68, CW, INK, h=2)
    # --- red italic kicker
    pg.itext(W / 2, 72,
             "Huang back at Nvidia, shares up 31% · Zelensky confirms warship "
             "sunk off Libya · EU unveils sanctions",
             13.5, RED, serif=True, align="c")
    # --- region chips
    chip_y = 91
    total_w = sum(text_width(f"{n} {c}", 10.5, serif=False) + 18
                  for n, c, _ in REGIONS)
    gap = (CW - total_w) / (len(REGIONS) - 1)
    cx = MARGIN
    for name, count, col in REGIONS:
        label = f"{name} {count}"
        w = text_width(label, 10.5, serif=False) + 18
        pg.rrect(cx, chip_y, w, 17, 4, col)
        pg.text(cx + w / 2, chip_y + 3.5, label, 10.5, WHITE, serif=False,
                align="c")
        cx += w + gap
    # --- UTC timeline (dark blue panel)
    tl_y, tl_h = 112, 28
    pg.vgrad(MARGIN, tl_y, CW, tl_h, NAVY, shade(NAVY, 0.7))
    pg.text(MARGIN + 8, tl_y + 8, "THE DAY IN UTC", 10, GOLD, serif=False)
    cells_x = MARGIN + 108
    cells_w = (MARGIN + CW - 12) - cells_x
    cw = cells_w / len(TIMELINE)
    for i, (tm, label) in enumerate(TIMELINE):
        x0 = cells_x + i * cw
        pg.text(x0 + 4, tl_y + 3, tm, 10.5, GOLD, serif=False)
        pg.text(x0 + 4, tl_y + 15, label, 8.5, WHITE, serif=False)
    # --- leads
    lead_y = 146
    lead_w = (CW - 24) / 3
    art_h = 66
    for i, ld in enumerate(LEADS):
        x0 = MARGIN + i * (lead_w + 12)
        ld["art"](pg, x0, lead_y, lead_w, art_h)
        art_label(pg, x0, lead_y, lead_w, art_h, ld["num"], ld["place"])
        ty = lead_y + art_h + 5
        pg.text(x0, ty, f"{ld['region']} · {ld['field']}", 9.5,
                REGION_COLORS[ld["region"]], serif=False)
        tag_chip(pg, x0 + lead_w - 62, ty - 1, ld["tag"])
        hy = ty + 13
        lines = wrap_text(ld["headline"], 17, lead_w, serif=True)
        hy = pg.para(x0, hy, lines[:3], 17, INK, serif=True, lh=21)
        dy = hy + 3
        dlines = wrap_text(ld["deck"], 10, lead_w, serif=False)
        dy = pg.para(x0, dy, dlines[:3], 10, (58, 56, 50), serif=False,
                      lh=13)
        pg.text(x0, dy + 2, ld["source"], 9, GREY, serif=False)
    # --- cards: 4 cols x 3 rows
    card_y = 351
    card_w = (CW - 30) / 4
    row_h = 137
    cart_h = 44
    for r in range(3):
        for c in range(4):
            cd = CARDS[r * 4 + c]
            x0 = MARGIN + c * (card_w + 10)
            y0 = card_y + r * (row_h + 8)
            cd["art"](pg, x0, y0, card_w, cart_h)
            art_label(pg, x0, y0, card_w, cart_h, cd["num"], cd["place"])
            ty = y0 + cart_h + 4
            pg.text(x0, ty, f"{cd['region']} · {cd['field']}", 8.5,
                    REGION_COLORS[cd["region"]], serif=False)
            tag_chip(pg, x0 + card_w - 58, ty - 1, cd["tag"])
            hy = ty + 11
            lines = wrap_text(cd["headline"], 13.5, card_w, serif=True)
            hy = pg.para(x0, hy, lines[:2], 13.5, INK, serif=True, lh=18)
            dy = hy + 2
            dlines = wrap_text(cd["deck"], 9, card_w, serif=False)
            dy = pg.para(x0, dy, dlines[:2], 9, (58, 56, 50), serif=False,
                         lh=12.5)
            pg.text(x0, dy + 1, cd["source"], 8.5, GREY, serif=False)
    # --- numbers strip
    num_y = 784
    pg.vgrad(MARGIN, num_y, CW, 52, NAVY, shade(NAVY, 0.7))
    pg.text(MARGIN + 10, num_y + 2, "THE DAY IN NUMBERS", 9, GOLD, serif=False)
    cell_w = CW / 6
    for i, (val, label) in enumerate(NUMBERS):
        x0 = MARGIN + i * cell_w
        pg.text(x0 + cell_w / 2, num_y + 12, val, 19, GOLD, serif=True,
                align="c")
        ll = wrap_text(label, 8, cell_w - 14, serif=False)
        pg.para(x0 + cell_w / 2, num_y + 32, ll[:2], 8, WHITE, serif=False,
                lh=9, align="c")
    # --- bottom: map + briefs
    bot_y = 842
    bot_h = 112
    map_w = 300
    pg.rect(MARGIN, bot_y, map_w, bot_h, PAPER2)
    pg.text(MARGIN + 8, bot_y + 4, "WHERE IT HAPPENED", 10, INK, serif=False)
    pg.text(MARGIN + map_w - 8, bot_y + 4, "pins = story numbers", 8.5, GREY,
            serif=False, align="r")
    mx, my = MARGIN, bot_y + 18
    ys = 84 / 108.0
    for gy in range(0, 84, 5):
        for gx in range(0, 300, 5):
            for (ex, ey, ew, eh) in LAND:
                if ((gx - ex - ew / 2) / (ew / 2)) ** 2 + \
                   ((gy / ys - ey - eh / 2) / (eh / 2)) ** 2 <= 1.0:
                    pg.circle(mx + gx, my + gy, 1.6, (140, 146, 156))
                    break
    for (num, px, py) in PINS:
        pg.circle(mx + px, my + py * ys, 5.5, RED)
        pg.text(mx + px, my + py * ys - 4, str(num), 7.5, WHITE, serif=False,
                align="c")
    bx = MARGIN + map_w + 14
    bw = W - MARGIN - bx
    pg.text(bx, bot_y + 4, "ALSO ON MONDAY 23 NOVEMBER", 10, INK, serif=False)
    pg.text(bx + bw, bot_y + 4, "— 21 MORE STORIES", 9, GREY, serif=False,
            align="r")
    col_w = (bw - 20) / 3
    for i, (num, text, src) in enumerate(BRIEFS):
        col = i // 7
        row = i % 7
        x0 = bx + col * (col_w + 10)
        yy = bot_y + 20 + row * 13
        pg.text(x0, yy, str(num), 9.5, RED, serif=False)
        pg.text(x0 + 18, yy, text, 9.5, INK, serif=False)
        sw = text_width(src, 8.5, serif=False)
        if 18 + text_width(text, 9.5, serif=False) + 4 + sw <= col_w:
            pg.text(x0 + col_w - sw, yy, src, 8.5, GREY, serif=False)
    # --- DATE CHECK
    dc_y = 960
    pg.rect(MARGIN, dc_y, CW, 36, PAPER2, outline=RED, ow=1.5)
    pg.rrect(MARGIN + 6, dc_y + 6, 74, 14, 2, RED)
    pg.text(MARGIN + 43, dc_y + 8.5, "DATE CHECK", 9.5, WHITE, serif=False,
            align="c")
    dlines = wrap_text(DATE_CHECK, 8.5, CW - 96, serif=False)
    pg.para(MARGIN + 88, dc_y + 2, dlines[:3], 8.5, INK, serif=False, lh=11)
    # --- footer
    ft_y = 1000
    pg.text(MARGIN, ft_y,
            "HOW SURE: CONFIRMED = 2+ outlets · OFFICIAL = the body itself · "
            "REPORTED = one outlet · CLAIM = one side's account. Scenes are drawn "
            "illustrations, not photographs.",
            9, GREY, serif=False)
    pg.text(MARGIN, ft_y + 11,
            "Sources: Reuters · CNN · WSJ · AP · BBC · NBC · CBS · Politico · Axios · "
            "Semafor · EU Commission · US Treasury · NHS England · UN News · FT · "
            "The Times · Le Monde · Al Jazeera · FIFA · RTBF",
            7.5, GREY, serif=False)
    return pg, ft_y + 22

def main():
    pg, end_y = build()
    if end_y > H:
        print(f"WARNING layout overflows by {end_y - H}px", file=sys.stderr)
    path = os.path.join(OUT, "entry.png")
    pg.finish(path)
    data = open(path, "rb").read()
    print(f"wrote {path} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    print(f"layout ends at y={end_y} (canvas {H})")

if __name__ == "__main__":
    main()
