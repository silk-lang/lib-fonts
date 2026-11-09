# Fonts

Fonts for Silk, from reading the file to shaping text.

| Package | Path | What it does |
| --- | --- | --- |
| [font-types](types) | `modules/types` | OpenType scalars: big-endian codecs, fixed point, tags, glyph IDs |
| [font-parse](parse) | `modules/parse` | Parses sfnt/TTC files and their tables, plus a font model for metrics, character maps, names and outlines |
| [font-shape](shape) | `modules/shape` | Text shaping: OpenType, AAT and the complex-script shapers |
| [font-outline](outline) | `modules/outline` | Glyph outlines (`glyf`/`gvar`, `CFF`, `CFF2`) drawn as flat commands or into a [graphics-vector](https://github.com/silk-lang/nonstd/tree/7d6c3693a9ad1fec24127985626ab4224f9f1995/graphics/vector) path |
| [font-raster](raster) | `modules/raster` | The UI glyph cache: unhinted glyphs rasterized once into [graphics-atlas](https://github.com/silk-lang/nonstd/tree/7d6c3693a9ad1fec24127985626ab4224f9f1995/graphics/atlas) tiles, a shaped-line cache, text gamma correction |
| [font-faces](faces) | `modules/faces` | Host-filled face database and CSS Fonts 4 matching |
| [font-collection](collection) | `modules/collection` | Application font collections and per-character fallback |

Unicode properties and text segmentation come from the standard library's `silk.text` modules,
which font-shape uses.

font-types, font-parse and font-shape started as ports of Google's
[fontations](https://github.com/googlefonts/fontations) (read-fonts, font-types, parts of
skrifa) and of [harfrust](https://github.com/harfbuzz/harfrust). Those projects are now
optional baselines rather than targets. Historical benchmark results and the original
nonstd weekly baseline workflow are not verification of this standalone repository.

## Shared tooling

- [`modules/scripts`](scripts) retains optional Python code generation, corpus,
  robustness, malformed-input and benchmark tooling, plus Rust baseline programs
  (`rust-font-dump`, `rust-hr-shape`). These are not required by native CI.
  Run maintainer scripts from the repository root.
- The internal parse dumper and shaping CLI live at
  [`font-parse-test-harness`](../font-parse-test-harness) and
  [`font-shape-test-harness`](../font-shape-test-harness), respectively, with matching
  package and binary names. They are not consumer libraries.
- [`modules/parse/bench`](parse/bench) remains the benchmark-only `font-parse-bench`.
- [`modules/shape/tools/wasm`](shape/tools/wasm) remains the consumer WebAssembly wrapper.
- [`modules/docs`](docs) holds the [porting decisions](docs/porting-decisions.md) and the
  [standard library gaps](docs/stdlib-gaps.md) the port ran into.

The standalone [Fonts workflow](../.github/workflows/fonts.yml) uses direct Silk
commands for workspace checking, six native test roots, internal harness and benchmark
builds, and Linux WebAssembly checking/building. `font-collection` has no test root
and receives workspace-check coverage. It does not run the optional Python/Rust
baseline and generation campaigns or the JavaScript wrapper runtime tests.

See the [repository overview](../README.md) for root-level commands, the pinned Silk
toolchain, recursively checked-out upstream corpus, and pinned graphics Git dependencies.

## Extraction

This subtree was extracted from
[silk-lang/nonstd at 7d6c3693a9ad1fec24127985626ab4224f9f1995](https://github.com/silk-lang/nonstd/tree/7d6c3693a9ad1fec24127985626ab4224f9f1995/fonts).
The originals remain in nonstd. Implementations, fixtures, upstream gitlinks and
license notices are retained; graphics libraries remain external dependencies.

## License

font-types and font-parse are [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), following
fontations. font-shape is [MIT](shape/LICENSE), following harfrust.
