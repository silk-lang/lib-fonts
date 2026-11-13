# font-web

Web fonts for native hosts: what a browser does between a `<link>` to a font stylesheet and
a font it can draw with.

| Module | What it does |
| --- | --- |
| `lib` | `decode(data)`: any font file to sfnt bytes (WOFF and WOFF2 decoded, TTF/OTF/TTC copied) |
| `woff` | WOFF 1.0 (zlib tables) |
| `woff2` | WOFF 2.0: Brotli, the `glyf`/`loca` and `hmtx` transforms, collections |
| `stylesheet` | `parse(css, base)`: the @font-face rules of a stylesheet |
| `fetch` | `stylesheet(url)`, `font(url)`, `face(rule)` over `silk.http.client.Http` |
| `sfnt` | format detection and the sfnt and collection writer the decoders share |

The decoders follow the [WOFF](https://www.w3.org/TR/WOFF/) and
[WOFF2](https://www.w3.org/TR/WOFF2/) specifications and rebuild tables as the reference
decoder does. The output reads in `FontDatabase.add` and `FontCollection.add` like the font
the file was made from.

## Loading Google Fonts

```silk
import font_web.fetch
import font_web.stylesheet { FontFaceRule }
import silk.http.client { Http }

// With `? &mut Http` provided by NativeHttp.fromEnvironment() in a native app.
let rules = run fetch.stylesheet("https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap")
// For each rule that text needs (rule.covers(codePoint)), load its face once:
let sfnt = run fetch.face(&rules.asSlice()[i])
// and register it under the rule's descriptors:
database.addFace(move sfnt, 0, rule.family, rule.weight, rule.width, rule.style)
```

Requests send a desktop Chrome `User-Agent` (`fetch.USER_AGENT`), because Google Fonts picks
the file format from it; with it every family comes as WOFF2 split into `unicode-range`
subsets. URLs are percent-encoded as a browser does, so `family=Roboto|Lobster` works.

## Descriptors

`FontFaceRule` holds `font-family`, `src` (`url()` with `format()` and `tech()`, and
`local()`), `font-weight`, `font-stretch` (also spelled `font-width`), `font-style` (with
oblique angle ranges), `unicode-range` and `font-display`. Weight, width and style are the
face database's own `Range` and `FaceStyle`, and `None` means `auto`. An invalid descriptor
is dropped, as CSS does, and a rule without a family or a source is dropped.
`rule.loadable()` picks the first `url()` source in a format this package reads.

## Validation

`src/tests.silk` covers the fixtures in `tests/` (see its README). Before it landed, the
decoder was also run over 341 WOFF2 and WOFF files that Google Fonts served for 15 families
(Inter, Roboto, Noto Sans JP, Noto Serif SC, Material Symbols, Noto Color Emoji, Roboto Flex
and others): every output matched fontTools' decoder glyph by glyph and passed the OpenType
Sanitizer browsers use.
