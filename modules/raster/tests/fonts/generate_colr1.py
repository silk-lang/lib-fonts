"""Writes ColrV1.ttf, the COLR version 1 fixture for modules/raster color tests.

Run with fontTools installed (`pip install fonttools`):
  python3 modules/raster/tests/fonts/generate_colr1.py
Every glyph is a 1000-unit square or a paint over it, so tests can check pixels by position.
"""
import os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.ttLib.tables import otTables as ot

def square(x0, y0, x1, y1):
    pen = TTGlyphPen(None)
    pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0)); pen.closePath()
    return pen.glyph()

names = [".notdef", "square", "left", "solid", "linear", "radial", "sweep", "composite", "moved", "override"]
glyphs = {n: square(0, 0, 0, 0) for n in names}
glyphs[".notdef"] = TTGlyphPen(None).glyph()
glyphs["square"] = square(0, 0, 1000, 1000)
glyphs["left"] = square(0, 0, 500, 1000)
for n in names[3:]:
    glyphs[n] = square(0, 0, 1000, 1000)

fb = FontBuilder(1000, isTTF=True)
fb.setupGlyphOrder(names)
fb.setupCharacterMap({0x41 + i: n for i, n in enumerate(names[3:])})
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics({n: (1000, 0) for n in names})
fb.setupHorizontalHeader(ascent=1000, descent=0)
fb.setupNameTable({"familyName": "Raster ColrV1", "styleName": "Regular"})
fb.setupOS2(sTypoAscender=1000, sTypoDescender=0, usWinAscent=1000, usWinDescent=0)
fb.setupPost()

def glyph(name, paint):
    return {"Format": ot.PaintFormat.PaintGlyph, "Glyph": name, "Paint": paint}

def solid(index, alpha=1.0):
    return {"Format": ot.PaintFormat.PaintSolid, "PaletteIndex": index, "Alpha": alpha}

line = {"Extend": "pad", "ColorStop": [{"StopOffset": 0.0, "PaletteIndex": 0, "Alpha": 1.0},
                                      {"StopOffset": 1.0, "PaletteIndex": 1, "Alpha": 1.0}]}
paints = {
    "solid": glyph("square", solid(0)),
    "linear": glyph("square", {"Format": ot.PaintFormat.PaintLinearGradient, "ColorLine": line,
                               "x0": 0, "y0": 0, "x1": 1000, "y1": 0, "x2": 0, "y2": 1000}),
    "radial": glyph("square", {"Format": ot.PaintFormat.PaintRadialGradient, "ColorLine": line,
                               "x0": 500, "y0": 500, "r0": 0, "x1": 500, "y1": 500, "r1": 500}),
    # 0 to 180 degrees counter-clockwise from +x: the top half ramps, the bottom half pads.
    "sweep": glyph("square", {"Format": ot.PaintFormat.PaintSweepGradient, "ColorLine": line,
                              "centerX": 500, "centerY": 500, "startAngle": 0.0, "endAngle": 180.0}),
    # Red square, then blue kept only where red is (src-in) on the left half.
    "composite": {"Format": ot.PaintFormat.PaintComposite, "CompositeMode": "src_in",
                  "SourcePaint": glyph("left", solid(1)), "BackdropPaint": glyph("square", solid(0))},
    "moved": {"Format": ot.PaintFormat.PaintTranslate, "dx": 500, "dy": 0, "Paint": glyph("left", solid(2))},
    "override": glyph("square", solid(2)),
}
colr = buildCOLR(paints, version=1, glyphMap=fb.font.getReverseGlyphMap())
fb.font["COLR"] = colr
# Palette 0 (light): red, blue, green. Palette 1 (dark): yellow, cyan, white.
fb.font["CPAL"] = buildCPAL(
    [[(1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 0, 1)], [(1, 1, 0, 1), (0, 1, 1, 1), (1, 1, 1, 1)]],
    paletteTypes=[1, 2],
)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ColrV1.ttf")
fb.save(out)
print(out)
