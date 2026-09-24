"""Builds the XLRTE and P·E logo files from Jost Medium outlines.

    pip install -r ../templates/requirements.txt fonttools shapely cairosvg pillow
    python3 build_logo.py

Letters are converted to outlines, so the SVG/PNG files render identically
without Jost installed. Jost Medium is fetched once from Google Fonts (OFL).
"""
import json, math, re, urllib.request
from pathlib import Path

import cairosvg
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from PIL import Image
from shapely.geometry import Polygon

HERE = Path(__file__).parent
TOKENS = json.loads((HERE.parent / "tokens.json").read_text())
INK, PAPER, ACC = (TOKENS["color"][k] for k in ("ink", "paper", "accent"))
CAP = 700            # Jost cap height (font units); all geometry below is in these units
TRACK = 60           # 6 % letter spacing
PAD = 230            # monogram padding inside its square

# ---------- font ----------
def jost_medium():
    cache = HERE / ".cache" / "Jost-Medium.ttf"
    if not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        css = urllib.request.urlopen(urllib.request.Request(
            "https://fonts.googleapis.com/css2?family=Jost:wght@500", headers={"User-Agent": "curl"})).read().decode()
        url = re.search(r"url\((https://[^)]+\.ttf)\)", css).group(1)
        cache.write_bytes(urllib.request.urlopen(url).read())
    return TTFont(cache)

FONT = jost_medium()
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()

class _Flatten(BasePen):
    """Collects glyph contours as point rings, flattening curves."""
    def __init__(self, gs):
        super().__init__(gs); self.rings, self.cur = [], []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for k in range(1, 17):
            t = k / 16; m = 1 - t
            self.cur.append(tuple(m**3 * a + 3 * m * m * t * b + 3 * m * t * t * c + t**3 * d
                                  for a, b, c, d in zip(p0, p1, p2, p3)))
    def _closePath(self): self.rings.append(self.cur); self.cur = []

def glyph(ch, dx=0.0):
    """Glyph outline as a shapely geometry (y up), shifted by dx; returns (geom, advance)."""
    name = CMAP[ord(ch)]; pen = _Flatten(GLYPHS); GLYPHS[name].draw(pen)
    geom = None
    for poly in sorted((Polygon([(x + dx, y) for x, y in r]) for r in pen.rings), key=lambda p: -p.area):
        geom = poly if geom is None else (geom.difference(poly) if geom.contains(poly) else geom.union(poly))
    return geom.buffer(0), GLYPHS[name].width

# ---------- marks ----------
# The X is drawn from two strokes; its left half is a forward chevron, split off by a small gap.
CHEVRON = Polygon([(8, 0), (234.6, 366.4), (33, 700), (176, 700), (307.1, 483.5), (378.1, 366.3), (305.5, 249.1), (151, 0)])
X_REST = Polygon([(441, 700), (585, 700), (398.2, 398.7), (336.2, 501.2), (327.2, 516)]).union(
         Polygon([(600, 0), (456, 0), (325.2, 216.4), (334.4, 231.2), (397.9, 333.7)]))
X_WIDTH = 600

def xlrte_parts():
    parts, x = [], X_WIDTH + TRACK
    for ch in "LRTE":
        g, adv = glyph(ch, x); parts.append(g); x += adv + TRACK
    letters = parts[0]
    for g in parts[1:]:
        letters = letters.union(g)
    return CHEVRON, X_REST.union(letters), x - TRACK

def pe_parts(overlap=60):
    p, _ = glyph("P"); e, _ = glyph("E", 541 - 78 - overlap)   # E's stem overlaps the P's bowl
    spark = p.intersection(e)
    return spark, p.union(e).difference(spark), e.bounds[2]

# ---------- SVG ----------
def path_d(geom, height=CAP):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = list(ring.coords)[:-1]
            out.append("M" + " L".join(f"{x:.1f} {height - y:.1f}" for x, y in pts) + "Z")
    return "".join(out)

def svg(layers, width, height=CAP, bg=None, title="XLRTE"):
    body = "".join(f'<path d="{path_d(g, height)}" fill="{c}"/>' for g, c in layers if not g.is_empty)
    rect = f'<rect width="{width:.0f}" height="{height:.0f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" role="img">'
            f'<title>{title}</title>{rect}{body}</svg>\n')

def square(layers, width, bg, title):
    """Mark centred in a square with PAD on every side (for icons and avatars)."""
    from shapely import affinity
    size = CAP + 2 * PAD
    shifted = [(affinity.translate(g, (size - width) / 2, PAD), c) for g, c in layers]
    return svg(shifted, size, size, bg=bg, title=title)

def write(name, content, png_height=None):
    (HERE / name).write_text(content)
    if png_height:
        cairosvg.svg2png(bytestring=content.encode(), write_to=str(HERE / name.replace(".svg", ".png")),
                         output_height=png_height)

def main():
    chev, rest, w = xlrte_parts()
    write("xlrte-color.svg", svg([(chev, ACC), (rest, INK)], w), 400)
    write("xlrte-white.svg", svg([(chev, ACC), (rest, PAPER)], w), 400)       # on ink or photos
    write("xlrte-black.svg", svg([(chev, INK), (rest, INK)], w), 400)         # single colour
    write("xlrte-mono-white.svg", svg([(chev, PAPER), (rest, PAPER)], w), 400)

    mono = square([(chev, ACC), (X_REST, PAPER)], X_WIDTH, INK, "XLRTE")
    write("x-monogram.svg", mono, 512)
    for size, name in [(180, "apple-touch-icon.png"), (32, "favicon-32.png"), (16, "favicon-16.png")]:
        cairosvg.svg2png(bytestring=mono.encode(), write_to=str(HERE / name), output_width=size, output_height=size)
    Image.open(HERE / "x-monogram.png").save(HERE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    spark, letters, pw = pe_parts()
    write("pe-color.svg", svg([(letters, INK), (spark, ACC)], pw, title="P·E"), 400)
    write("pe-white.svg", svg([(letters, PAPER), (spark, ACC)], pw, title="P·E"), 400)
    write("pe-black.svg", svg([(letters, INK)], pw, title="P·E"), 400)        # spark becomes a cut-out
    write("pe-mono-white.svg", svg([(letters, PAPER)], pw, title="P·E"), 400)
    print("wrote logo files to", HERE)

if __name__ == "__main__":
    main()
