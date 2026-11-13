"""Regenerates the font-web test fixtures. Needs fontTools and brotli (pip install fonttools brotli).

Run from this directory: python3 generate.py. The *.decoded.ttf files are not written here:
they are font-web's own output, checked against fontTools before they are committed.
"""
import os
import struct

import brotli
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTCollection, TTFont, woff2

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "..", "..", "..", "test-support", "fonts")
TEXT = "Hello Wörld! ÅéÇ ﬁ 0123"


def out(name):
    return os.path.join(HERE, name)


def subset_font(path, name):
    font = TTFont(os.path.join(SOURCE, path), recalcTimestamp=False)
    options = subset.Options()
    options.hinting = True
    options.notdef_outline = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=TEXT)
    subsetter.subset(font)
    font.save(out(name))


def flavors(name):
    for flavor in ("woff", "woff2"):
        font = TTFont(out(name + ".ttf"), recalcTimestamp=False)
        font.flavor = flavor
        font.save(out(name + "." + flavor))


def cff_font():
    builder = FontBuilder(1000, isTTF=False)
    names = [".notdef", "A", "B"]
    builder.setupGlyphOrder(names)
    builder.setupCharacterMap({65: "A", 66: "B"})
    strings = {}
    for name in names:
        pen = T2CharStringPen(600, None)
        pen.moveTo((50, 0))
        pen.lineTo((550, 0))
        pen.curveTo((560, 300), (400, 700), (300, 700))
        pen.closePath()
        strings[name] = pen.getCharString()
    builder.setupCFF("TestCFF-Regular", {"FullName": "Test CFF"}, strings, {})
    builder.setupHorizontalMetrics({name: (600, 50) for name in names})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({"familyName": "Test CFF", "styleName": "Regular"})
    builder.setupOS2()
    builder.setupPost()
    builder.save(out("cff.otf"))


def base128(value):
    digits = [value & 0x7F]
    value >>= 7
    while value:
        digits.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(digits))


def woff2_collection(ttc, target):
    """A WOFF2 collection with null transforms: fontTools cannot write one."""
    data = open(ttc, "rb").read()
    count = struct.unpack(">I", data[8:12])[0]
    offsets = struct.unpack(">%dI" % count, data[12 : 12 + 4 * count])
    tables, index, fonts = [], {}, []
    for offset in offsets:
        flavor, number = struct.unpack(">IH", data[offset : offset + 6])
        used = []
        for i in range(number):
            record = data[offset + 12 + 16 * i : offset + 28 + 16 * i]
            tag, _, start, length = struct.unpack(">4sIII", record)
            if (start, length) not in index:
                index[(start, length)] = len(tables)
                tables.append((tag, data[start : start + length]))
            used.append(index[(start, length)])
        fonts.append((flavor, used))
    directory = b""
    for tag, blob in tables:
        name = tag.decode("latin1")
        version = 3 if name in ("glyf", "loca") else 0
        if name in woff2.woff2KnownTags:
            directory += bytes([woff2.woff2KnownTags.index(name) | (version << 6)])
        else:
            directory += bytes([63 | (version << 6)]) + tag
        directory += base128(len(blob))
    collection = struct.pack(">I", 0x00020000) + bytes([len(fonts)])
    for flavor, used in fonts:
        collection += bytes([len(used)]) + struct.pack(">I", flavor) + bytes(used)
    packed = brotli.compress(b"".join(blob for _, blob in tables))
    total = 48 + len(directory) + len(collection) + len(packed)
    header = struct.pack(
        ">4sIIHHIIHHIIIII", b"wOF2", 0x74746366, total, len(tables), 0, len(data), len(packed),
        1, 0, 0, 0, 0, 0, 0,
    )
    open(target, "wb").write(header + directory + collection + packed)


subset_font("NotoSans-Regular.subset.ttf", "noto.ttf")
subset_font("NotoSans-Bold.subset.ttf", "noto-bold.ttf")
subset_font("RobotoFlex.subset.ttf", "flex.ttf")
flavors("noto")
flavors("flex")
woff2.compress(out("noto.ttf"), out("noto.hmtx.woff2"), transform_tables={"glyf", "loca", "hmtx"})
cff_font()
for flavor in ("woff", "woff2"):
    font = TTFont(out("cff.otf"))
    font.flavor = flavor
    font.save(out("cff." + flavor))
pair = TTCollection()
pair.fonts = [TTFont(out("noto.ttf"), recalcTimestamp=False), TTFont(out("noto-bold.ttf"), recalcTimestamp=False)]
pair.save(out("pair.ttc"))
woff2_collection(out("pair.ttc"), out("pair.woff2"))
os.remove(out("pair.ttc"))
