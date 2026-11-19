# font-shape-bench

Times `font-shape` on fixed corpora with open fonts, with HarfBuzz as the oracle and the speed
reference.

```sh
modules/shape/bench/fetch-fonts.sh ~/bench-fonts
silk build --manifest-path modules/shape/bench/silk.toml --release
BENCH=build/<target>/release/font-shape-bench

$BENCH words ~/bench-fonts/Inter-Regular.ttf modules/shape/bench/corpora/latin-prose.txt
$BENCH lines ~/bench-fonts/Inter-Regular.ttf modules/shape/bench/corpora/latin-prose.txt
```

`words` shapes every space-separated word as its own call, which is what a UI does most; `lines`
shapes every line of the corpus as one call. Both print the calls, the glyphs, ns per call, ns per
glyph and a checksum of glyph ids, clusters, advances and offsets. `dump-words` and `dump-lines`
print the glyphs instead, in `hb-shape --no-glyph-names` form.

## Safe breaks

A text layer that takes a line's glyphs from its shaped paragraph relies on the unsafe-to-break
flag: text cut at a cluster without it must shape to the same glyphs on both sides. The checks
shape every line of a corpus (or with `-words` every word), cut it, shape the parts with the
script and direction of the whole, and compare. Each exits with 1 when a cut gives other glyphs.

| Mode | What it cuts | What must hold |
|---|---|---|
| `breaks`, `breaks-words` | once, at every cluster not flagged | the two sides give the glyphs of the whole |
| `slices`, `slices-words` | twice, from every such cluster to the next few and some further on | the piece gives the glyphs it has in the whole |
| `grow` | the text up to each word end, at its last such cluster before its last word; then one more word, and all the rest, are added | the kept glyphs and the shaped rest give the glyphs of the longer text |
| `concat` | as `grow`, with the unsafe-to-concat flag | the same |

```sh
$BENCH breaks ~/bench-fonts/Inter-Regular.ttf modules/shape/bench/corpora/latin-prose.txt
$BENCH grow '/System/Library/Fonts/HelveticaNeue.ttc#2' modules/shape/bench/corpora/aat-latin.txt
```

They print `safe` (cuts made), `flagged` (clusters that could not be cut, or for `grow` word
ends where nothing could be kept), `wrong`, the texts checked and the texts skipped because the
font lacks most of their characters. `FONT#N` is face N of a collection.

`grow` needs more than the flag. The flag says what a cut does to the text that was shaped;
words added later may reach back over the cut (a state machine of an Apple font that replaces
a glyph it marked earlier). So the rest must not lean on what is before it: `grow` keeps
nothing when `Buffer.leansOnBefore` is set after shaping the rest. `leans-lines` and
`leans-words` dump each text's glyphs with `leans` or `stays` in front. HarfBuzz flags the
whole buffer unsafe to concat for these fonts, so `concat` keeps nothing there.

`flags-words` and `flags-lines` dump the glyphs with their flags, to compare with HarfBuzz's.
A corpus in one font with several scripts (`mixed`) is not for these checks: a layer above
itemizes by script first.

### Fonts with Apple's tables

`aat-breaks.py` runs `breaks`, `slices` and `grow` over every face with a `morx`, `mort`,
`kerx` or `kern` table: the AAT fonts of the shaping test data with the texts their tests
shape, then the faces of the font files in the directories given, with the Latin corpora,
`aat-latin.txt` (ligatures, kerning pairs, digits, punctuation runs), `scripts.txt` (a line or
two in each of 20 scripts), Arabic, Devanagari, CJK and emoji. It prints a row a face and
exits with 1 when any cut was wrong. On macOS:

```sh
BENCH=$BENCH modules/shape/bench/run.sh breaks out/ /System/Library/Fonts /System/Library/Fonts/Supplemental
```

## HarfBuzz

`hb/hb_bench.c` is the same program over HarfBuzz. Build it against the release to compare with
(15.0.0 is the one `font-shape` follows):

```sh
c++ -O2 -DHB_NO_MT -c harfbuzz-15.0.0/src/harfbuzz.cc -o harfbuzz.o
cc -O2 -Iharfbuzz-15.0.0/src modules/shape/bench/hb/hb_bench.c harfbuzz.o -lstdc++ -lm -o hb-bench
```

## The matrix

```sh
export FONTS=~/bench-fonts BENCH=... HB_BENCH=./hb-bench
modules/shape/bench/run.sh                 # every corpus and font, with the ratio to HarfBuzz
modules/shape/bench/run.sh dump out/       # glyph dumps: diff two builds, or against HarfBuzz
modules/shape/bench/run.sh aat out/        # the AAT fonts of the shaping test data
modules/shape/bench/run.sh breaks out/ DIR # the break checks over fonts with Apple's tables
```

To check that a change keeps the output, dump before and after it and `diff -r` the directories.

Wall time on a shared machine moves by tens of percent between runs. For a change of a few
percent, count instructions instead, which repeat exactly:

```sh
valgrind --tool=callgrind --callgrind-out-file=/dev/null $BENCH words FONT CORPUS 2
```
