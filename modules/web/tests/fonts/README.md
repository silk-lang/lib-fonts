# Web font fixtures

Small fonts for the `font-web` tests, made from the fonts in `test-support/fonts`
by [`generate.py`](generate.py) with fontTools 4.68 and Brotli:

| File | What it is |
| --- | --- |
| `noto.ttf`, `noto-bold.ttf` | Noto Sans Regular and Bold, subset to `Hello Wörld! ÅéÇ ﬁ 0123` with hinting kept (simple and composite glyphs, instructions) |
| `noto.woff` | WOFF 1.0 of `noto.ttf` (zlib) |
| `noto.woff2` | WOFF 2.0 of `noto.ttf`, `glyf`/`loca` transformed |
| `noto.hmtx.woff2` | Same, with the `hmtx` transform too |
| `flex.*` | Roboto Flex, a variable font (`fvar`, `gvar`), subset the same way |
| `cff.otf`, `cff.woff`, `cff.woff2` | A three-glyph CFF font built with fontTools' `FontBuilder` |
| `pair.woff2` | A WOFF2 collection of `noto.ttf` and `noto-bold.ttf` (shared tables, null transforms), written by `generate.py` itself because fontTools does not write WOFF2 collections |
| `inter.woff2` | Inter 400 as Google Fonts serves it for `css2?family=Inter&text=Hello%20Silk` (Google's encoder) |
| `*.decoded.ttf` | What `woff2.decode` gives for the file of the same name; checked against fontTools' own WOFF2 decoder glyph by glyph and with the OpenType Sanitizer before they were added |

`../inter.css` is the stylesheet Google Fonts returned on 2026-11-13 for
`css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap` with a desktop Chrome
User-Agent.

Noto Sans, Roboto Flex and Inter are under the SIL Open Font License 1.1
([Noto-LICENSE-OFL.txt](Noto-LICENSE-OFL.txt), [RobotoFlex-LICENSE-OFL.txt](RobotoFlex-LICENSE-OFL.txt);
Inter: Copyright 2020 The Inter Project Authors, same license).
