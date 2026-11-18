#!/usr/bin/env python3
"""Writes one corpus per AAT font of the shaping test data: the texts its tests shape.

    aat-corpora.py OUT_DIR

Prints `FONT CORPUS` rows for `run.sh aat`. A font counts as AAT when it has a morx, mort or
kerx table. Fonts for macOS system files, which the test data does not hold, are left out.
"""
import os, re, struct, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, "..", "test-data", "harfrust", "harfrust")
out = sys.argv[1]
os.makedirs(out, exist_ok=True)

def aat(path):
    try:
        data = open(path, "rb").read(4096)
    except OSError:
        return False
    if data[:4] == b"ttcf" or len(data) < 12:
        return False
    count = struct.unpack(">H", data[4:6])[0]
    tags = {data[12 + 16 * i : 16 + 16 * i] for i in range(count)}
    return bool(tags & {b"morx", b"mort", b"kerx"})

call = re.compile(r'shape\(\s*"([^"]+)",\s*((?:"(?:[^"\\]|\\.)*"\s*(?:\\\s*)?)+),', re.S)
texts = {}
for name in sorted(os.listdir(os.path.join(root, "tests", "shaping"))):
    source = open(os.path.join(root, "tests", "shaping", name), encoding="utf-8").read()
    for font, literal in call.findall(source):
        literal = re.sub(r'\\\n\s*', "", literal.strip()[1:-1])
        text = re.sub(r"\\u\{([0-9A-Fa-f]+)\}", lambda m: chr(int(m.group(1), 16)), literal)
        if "\\" in text or "\n" in text or not text:
            continue
        texts.setdefault(font, [])
        if text not in texts[font]:
            texts[font].append(text)
for font in sorted(texts):
    path = os.path.join(root, font)
    if not aat(path):
        continue
    corpus = os.path.join(out, os.path.basename(font) + ".txt")
    with open(corpus, "w", encoding="utf-8", errors="surrogatepass") as file:
        file.write("\n".join(texts[font]) + "\n")
    print(os.path.normpath(path), corpus)
