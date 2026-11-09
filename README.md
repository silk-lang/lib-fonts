# lib-fonts

Font parsing, shaping, outlines, rasterization, face matching and fallback for Silk.

## Consumer libraries

| Package | Source | Purpose |
| --- | --- | --- |
| `font-types` | [fonts/types](fonts/types) | OpenType scalars, big-endian codecs, fixed point, tags and glyph IDs |
| `font-parse` | [fonts/parse](fonts/parse) | sfnt/TTC parsing, tables, metrics, character maps and font models |
| `font-shape` | [fonts/shape](fonts/shape) | OpenType, AAT and complex-script text shaping |
| `font-outline` | [fonts/outline](fonts/outline) | `glyf`/`gvar`, CFF and CFF2 glyph outlines and vector paths |
| `font-raster` | [fonts/raster](fonts/raster) | Glyph atlas and shaped-line caches, rasterization and text gamma correction |
| `font-faces` | [fonts/faces](fonts/faces) | Host-filled face database and CSS Fonts 4 matching |
| `font-collection` | [fonts/collection](fonts/collection) | Application font collections and per-character fallback |

The workspace uses Silk `0.1.0-dev.61+91f335268900`. Graphics dependencies are
pinned Git dependencies on [silk-lang/lib-graphics](https://github.com/silk-lang/lib-graphics),
not copied graphics libraries or sibling-checkout dependencies. Keep that revision aligned
with `lib-css` and other consumers: Silk rejects duplicate physical copies of a named package.
Unicode properties and segmentation come from Silk's standard library.

## Development

Clone with the retained upstream test data:

```sh
git clone --recurse-submodules https://github.com/silk-lang/lib-fonts.git
cd lib-fonts
# For an existing checkout:
git submodule update --init --recursive
```

Install the pinned Silk release using its installer, then run commands from the
repository root:

```sh
curl --fail --silent --show-error --location \
  'https://raw.githubusercontent.com/silk-lang/silk/v0.1.0-dev.61+91f335268900/install.sh' \
  -o /tmp/install-lib-fonts-silk.sh
SILK_RELEASE='v0.1.0-dev.61+91f335268900' sh /tmp/install-lib-fonts-silk.sh
export PATH="$HOME/.silk/bin:$PATH"
silk use
```

Native builds need LLVM/Clang. On Linux, select Clang 22 with
`export SILK_CLANG="$(command -v clang-22)"`. On macOS, install Homebrew LLVM and
select both Clang and the Apple SDK:

```sh
brew install llvm
export SILK_CLANG="$(brew --prefix llvm)/bin/clang"
export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
```

The native checks do not require Python or Rust:

```sh
silk check --workspace
for package in types parse shape outline raster faces; do
  silk test --manifest-path "fonts/$package/silk.toml" --root src/tests.silk
done
silk build --package font-parse-test-harness
silk build --package font-shape-test-harness
silk build --package font-parse-bench
```

`font-collection` is covered by workspace checking; it has no `src/tests.silk`
test root. Shaping runtime tests use the recursively checked-out upstream corpus.
Keep the `fonts/` fixture layout intact. The retained `svg/tests/fonts/` files and
licenses support font tests, while `svg/casefold.lock.json` and
`svg/scripts/generate-casefold` support maintenance of `font-faces` generated data;
these are supporting assets, not an extracted SVG library.

### Internal executables and WebAssembly

These tools are separate from the seven consumer libraries:

- [font-parse-test-harness](font-parse-test-harness): internal parse dumper;
  package and binary name `font-parse-test-harness`.
- [font-shape-test-harness](font-shape-test-harness): internal shaping CLI;
  package and binary name `font-shape-test-harness`.
- [fonts/parse/bench](fonts/parse/bench): benchmark-only `font-parse-bench`.
- [fonts/shape/tools/wasm](fonts/shape/tools/wasm): retained consumer WebAssembly
  wrapper, `font-shape-wasm`, with its JavaScript wrapper under `js/`.

With LLVM's `wasm-ld` on `PATH`, check and build the WebAssembly wrapper directly:

```sh
export PATH="$(dirname "$SILK_CLANG"):$PATH"
silk check --manifest-path fonts/shape/tools/wasm/silk.toml --target wasm32-unknown-unknown
silk build --release --manifest-path fonts/shape/tools/wasm/silk.toml --target wasm32-unknown-unknown
```

The retained shell helper `fonts/scripts/build-wasm` additionally copies the
artifact into the JavaScript wrapper's `dist/harfrust.wasm`.

### CI and optional maintainer tooling

[Fonts CI](.github/workflows/fonts.yml) installs the workspace-pinned Silk release,
checks the workspace, runs the six native test roots on Linux and macOS, and
builds the two internal harnesses and parser benchmark. Its Linux job also checks
and builds the WebAssembly wrapper. CI uses direct Silk commands, not Python;
WebAssembly compilation is not a JavaScript wrapper runtime test.

[fonts/scripts](fonts/scripts) retains optional Python generation, corpus,
robustness and benchmark tooling, plus Rust reference programs
(`rust-font-dump` and `rust-hr-shape`). Those tools have their own Python/Rust and
upstream-data requirements and run from the repository root. They are not part of
the native CI path, and this repository does not claim the original nonstd weekly
baseline or generated-code campaigns run here. Existing porting notes and
historical results remain under [fonts/docs](fonts/docs); they are not fresh
verification of this extraction.

## Provenance and licensing

Extracted from `fonts/` in
[silk-lang/nonstd at 7d6c3693a9ad1fec24127985626ab4224f9f1995](https://github.com/silk-lang/nonstd/tree/7d6c3693a9ad1fec24127985626ab4224f9f1995/fonts).
Earlier implementation history remains in that source snapshot. The extraction retains
implementations, fixtures, upstream gitlinks and existing license notices; it does not vendor
the other libraries.

The parsing and shaping work began as ports of Google's
[fontations](https://github.com/googlefonts/fontations) and
[harfrust](https://github.com/harfbuzz/harfrust). `font-types` and `font-parse` retain
their [MIT](fonts/LICENSE-MIT) or [Apache-2.0](fonts/LICENSE-APACHE) licensing;
`font-shape` retains its [MIT license](fonts/shape/LICENSE). Consult the retained
notices for individual source files, upstream data and font fixtures; this overview
does not replace their licenses.
