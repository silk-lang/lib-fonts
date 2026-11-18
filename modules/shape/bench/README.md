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
flag: text cut at a cluster without it must shape to the same glyphs on both sides. `breaks`
cuts every line at every such cluster, shapes the two sides and compares them with the whole;
`concat` does the same for text that grows, with the unsafe-to-concat flag. Both exit with 1
when a cut gives other glyphs. `flags-words` and `flags-lines` dump the glyphs with their
flags, to compare with HarfBuzz's.

```sh
$BENCH breaks ~/bench-fonts/Inter-Regular.ttf modules/shape/bench/corpora/latin-prose.txt
```

A corpus in one font with several scripts (`mixed`) reports wrong cuts: a layer above itemizes
by script first, and this check shapes each side with the script it guesses.

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
```

To check that a change keeps the output, dump before and after it and `diff -r` the directories.

Wall time on a shared machine moves by tens of percent between runs. For a change of a few
percent, count instructions instead, which repeat exactly:

```sh
valgrind --tool=callgrind --callgrind-out-file=/dev/null $BENCH words FONT CORPUS 2
```
