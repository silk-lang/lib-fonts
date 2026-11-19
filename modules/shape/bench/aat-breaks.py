#!/usr/bin/env python3
"""Checks the unsafe-to-break flags of fonts shaped with Apple's tables.

    BENCH=path/to/font-shape-bench aat-breaks.py OUT_DIR [FONT_DIR ...]

For every face with a morx, mort, kerx or kern table (the AAT fonts of the shaping test data
with the texts their tests shape, then every face of the font files in each FONT_DIR with the
corpora here) runs the bench's checks: `breaks` and `slices` by line and by word, and `grow`.
Prints one row a face: the texts checked, the cuts a text layer may make (clusters not flagged
unsafe to break) and the clusters that are flagged, how often growing text kept glyphs and
how often it could keep none, and per check how many cuts gave other glyphs than the whole
text has. Writes the rows to OUT_DIR/breaks.tsv and exits with 1 when any cut was wrong.

MODES (default "breaks breaks-words slices slices-words grow") picks the checks; FACES=first
checks only the first face of each collection.
"""
import os, struct, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
bench = os.environ["BENCH"]
modes = os.environ.get("MODES", "breaks breaks-words slices slices-words grow").split()
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
corpora = ["aat-latin", "latin-prose", "ui-labels", "code", "scripts", "arabic", "devanagari", "cjk", "emoji"]
tables = {b"morx", b"mort", b"kerx", b"kern"}

def faces(path):
    """The table tags of each face of a font file."""
    with open(path, "rb") as file:
        head = file.read(12)
        offsets = [0]
        if head[:4] == b"ttcf":
            count = struct.unpack(">I", head[8:12])[0]
            offsets = struct.unpack(">%dI" % count, file.read(4 * count))
        found = []
        for offset in offsets:
            file.seek(offset)
            head = file.read(12)
            if head[:4] not in (b"\0\1\0\0", b"OTTO", b"true"):
                break
            count = struct.unpack(">H", head[4:6])[0]
            records = file.read(16 * count)
            found.append({records[i * 16 : i * 16 + 4] for i in range(count)})
        return found

def check(font, corpus):
    """safe, flagged and per mode wrong, summed over a corpus; None when nothing was checked."""
    row = {"safe": 0, "flagged": 0, "texts": 0}
    for mode in modes:
        run = subprocess.run([bench, mode, font, corpus], capture_output=True, text=True)
        fields = run.stdout.strip().split("\n")[-1].split()
        if run.returncode not in (0, 1) or len(fields) < 12:
            row[mode] = row.get(mode, 0)
            row["failed"] = row.get("failed", 0) + 1
            continue
        values = dict(zip(fields[0::2], (int(v) for v in fields[1::2])))
        row[mode] = values["wrong"]
        if mode == modes[0]:
            row["safe"], row["flagged"], row["texts"] = values["safe"], values["flagged"], values["texts"]
        if mode == "grow":
            row["kept"], row["none"] = values["safe"], values["flagged"]
        if values["wrong"]:
            with open(os.path.join(out, "wrong.txt"), "a") as log:
                log.write("%s %s %s\n%s\n" % (mode, font, corpus, run.stdout))
    return row

rows = []
def add(label, font, texts):
    total = {"safe": 0, "flagged": 0, "texts": 0, "failed": 0, "kept": 0, "none": 0}
    for corpus in texts:
        row = check(font, corpus)
        for key, value in row.items():
            total[key] = total.get(key, 0) + value
    if total["texts"] == 0 and not total["failed"]:
        return
    rows.append((label, total))
    wrong = " ".join("%6d" % total.get(mode, 0) for mode in modes)
    print("%-44s %6d %7d %7d %6d %6d %s%s" % (label[:44], total["texts"], total["safe"], total["flagged"],
          total["kept"], total["none"], wrong,
          "  FAILED %d" % total["failed"] if total["failed"] else ""), flush=True)

print("%-44s %6s %7s %7s %6s %6s %s" % ("font", "texts", "safe", "flagged", "kept", "none",
      " ".join("%6s" % m.replace("breaks", "brk").replace("slices", "slc").replace("-words", "-w") for m in modes)))
if os.path.exists(os.path.join(out, "wrong.txt")):
    os.remove(os.path.join(out, "wrong.txt"))
listed = subprocess.run([sys.executable, os.path.join(here, "aat-corpora.py"), os.path.join(out, "texts")],
                        capture_output=True, text=True).stdout
for line in listed.splitlines():
    # A row is `FONT CORPUS`; both may hold spaces, and the corpus is the font's name plus .txt.
    at = line.find(" " + os.path.join(out, "texts"))
    font, corpus = line[:at], line[at + 1 :]
    if "/tests/fonts/" in font:
        add("test:" + os.path.basename(font), font, [corpus])
for directory in sys.argv[2:]:
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if not os.path.isfile(path) or not name.lower().endswith((".ttf", ".ttc", ".otf")):
            continue
        try:
            found = faces(path)
        except (OSError, struct.error):
            continue
        for index, tags in enumerate(found):
            if not tags & tables or (index and os.environ.get("FACES") == "first"):
                continue
            kinds = "".join(k for k, t in (("m", b"morx"), ("M", b"mort"), ("x", b"kerx"), ("k", b"kern"), ("G", b"GPOS")) if t in tags)
            add("%s#%d [%s]" % (name, index, kinds), "%s#%d" % (path, index),
                [os.path.join(here, "corpora", c + ".txt") for c in corpora])
with open(os.path.join(out, "breaks.tsv"), "w") as file:
    file.write("font\ttexts\tsafe\tflagged\tgrow-kept\tgrow-none\t%s\n" % "\t".join(modes))
    for label, total in rows:
        file.write("%s\t%d\t%d\t%d\t%d\t%d\t%s\n" % (label, total["texts"], total["safe"], total["flagged"],
                   total["kept"], total["none"], "\t".join(str(total.get(mode, 0)) for mode in modes)))
wrong = sum(total.get(mode, 0) for _, total in rows for mode in modes)
failed = sum(total["failed"] for _, total in rows)
print("faces %d  safe %d  flagged %d  grow kept %d none %d  wrong %d  failed runs %d" % (
    len(rows), sum(t["safe"] for _, t in rows), sum(t["flagged"] for _, t in rows),
    sum(t["kept"] for _, t in rows), sum(t["none"] for _, t in rows), wrong, failed))
sys.exit(1 if wrong or failed else 0)
