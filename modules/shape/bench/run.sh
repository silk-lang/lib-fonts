#!/bin/sh
# Runs every corpus with its fonts and prints one row for each: ns per call and per glyph, for
# words (short runs) and lines (paragraphs), with HarfBuzz's time and the ratio to it when
# HB_BENCH names a built hb/hb_bench.c. With `dump DIR`, writes each run's glyphs to DIR
# instead, to compare two builds or to compare with HarfBuzz.
#
# With `aat DIR`, shapes the texts of the shaping test data's AAT fonts (morx, mort, kerx), which
# stand in for Apple's system fonts off macOS: one row a font, and with HB_BENCH the number of
# texts whose glyphs differ from HarfBuzz's. DIR receives the corpora and the dumps.
#
# With `breaks DIR [FONT_DIR ...]`, checks the unsafe-to-break flags of every face with Apple's
# tables: the AAT test fonts, then the font files of each FONT_DIR (see aat-breaks.py). FONTS is
# not needed for it.
#
#   FONTS=dir BENCH=path/to/font-shape-bench [HB_BENCH=path/to/hb-bench] run.sh [dump DIR | aat DIR | breaks DIR [FONT_DIR ...]]
set -eu
here=$(dirname "$0")
: "${BENCH:?the font-shape-bench binary}"
if [ "${1:-}" = breaks ]; then
  shift
  export BENCH
  exec python3 "$here/aat-breaks.py" "$@"
fi
: "${FONTS:?the directory fetch-fonts.sh filled}"
HB_BENCH=${HB_BENCH:-}
iterations=${ITERATIONS:-20}
rows="latin-prose:Inter-Regular.ttf latin-prose:Roboto-Regular.ttf latin-prose:NotoSans-Regular.ttf
latin-prose:JetBrainsMono-Regular.ttf ui-labels:Inter-Regular.ttf ui-labels:Roboto-Regular.ttf
ui-labels:NotoSans-Regular.ttf ui-labels:JetBrainsMono-Regular.ttf code:JetBrainsMono-Regular.ttf
cjk:NotoSansCJKsc-Regular.otf arabic:NotoNaskhArabic-Regular.ttf
devanagari:NotoSansDevanagari-Regular.ttf emoji:NotoColorEmoji.ttf mixed:NotoSans-Regular.ttf
mixed:NotoSansCJKsc-Regular.otf"
field() { echo "$1" | sed -n "s#.* $2 \([0-9.]*\).*#\1#p"; }
if [ "${1:-}" = dump ]; then
  mkdir -p "$2"
  for row in $rows; do
    corpus=${row%%:*}; font=${row##*:}
    for mode in words lines; do
      "$BENCH" dump-$mode "$FONTS/$font" "$here/corpora/$corpus.txt" > "$2/$corpus-$font-$mode.txt"
    done
  done
  exit 0
fi
if [ "${1:-}" = aat ]; then
  printf '%-48s %6s %7s %9s %9s %8s %6s\n' font calls glyphs ns/call ns/glyph hb/glyph differ
  python3 "$here/aat-corpora.py" "$2" | while read -r font corpus; do
    ours=" $("$BENCH" lines "$font" "$corpus" "$iterations")"
    hb=-; differ=-
    if [ -n "$HB_BENCH" ]; then
      hb=$(field "$("$HB_BENCH" lines "$font" "$corpus" "$iterations")" ns/glyph)
      "$BENCH" dump-lines "$font" "$corpus" > "$corpus.ours"
      "$HB_BENCH" dump-lines "$font" "$corpus" > "$corpus.hb"
      differ=$(diff "$corpus.ours" "$corpus.hb" | grep -c '^<' || true)
    fi
    printf '%-48s %6s %7s %9s %9s %8s %6s\n' "$(basename "$font")" "$(field "$ours" calls)" \
      "$(field "$ours" glyphs)" "$(field "$ours" ns/call)" "$(field "$ours" ns/glyph)" "$hb" "$differ"
  done
  exit 0
fi
printf '%-12s %-32s %-5s %7s %8s %9s %9s %8s %6s\n' corpus font mode calls glyphs ns/call ns/glyph hb/glyph ratio
for row in $rows; do
  corpus=${row%%:*}; font=${row##*:}
  for mode in words lines; do
    ours=" $("$BENCH" $mode "$FONTS/$font" "$here/corpora/$corpus.txt" "$iterations")"
    hb=-; ratio=-
    if [ -n "$HB_BENCH" ]; then
      theirs=$("$HB_BENCH" $mode "$FONTS/$font" "$here/corpora/$corpus.txt" "$iterations")
      hb=$(field "$theirs" ns/glyph)
      ratio=$(echo "$(field "$ours" ns/glyph) $hb" | awk '{ printf "%.2f", $1 / $2 }')
    fi
    printf '%-12s %-32s %-5s %7s %8s %9s %9s %8s %6s\n' "$corpus" "$font" "$mode" \
      "$(field "$ours" calls)" "$(field "$ours" glyphs)" "$(field "$ours" ns/call)" \
      "$(field "$ours" ns/glyph)" "$hb" "$ratio"
  done
done
