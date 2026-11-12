# lib-fonts

Font parsing, shaping, outlines, rasterization, face matching and fallback for Silk.

## Consumer libraries

| Package | Source | Purpose |
| --- | --- | --- |
| `font-types` | [modules/types](modules/types) | OpenType scalars, big-endian codecs, fixed point, tags and glyph IDs |
| `font-parse` | [modules/parse](modules/parse) | sfnt/TTC parsing, tables, metrics, character maps and font models |
| `font-shape` | [modules/shape](modules/shape) | OpenType, AAT and complex-script text shaping |
| `font-outline` | [modules/outline](modules/outline) | `glyf`/`gvar`, CFF and CFF2 glyph outlines and vector paths |
| `font-raster` | [modules/raster](modules/raster) | Glyph atlas and shaped-line caches, rasterization and text gamma correction |
| `font-faces` | [modules/faces](modules/faces) | Host-filled face database and CSS Fonts 4 matching |
| `font-collection` | [modules/collection](modules/collection) | Application font collections and per-character fallback |

The workspace uses Silk `0.1.0-dev.69+366225ca4dc5`. Graphics dependencies are
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
  'https://raw.githubusercontent.com/silk-lang/silk/v0.1.0-dev.69+366225ca4dc5/install.sh' \
  -o /tmp/install-lib-fonts-silk.sh
SILK_RELEASE='v0.1.0-dev.69+366225ca4dc5' sh /tmp/install-lib-fonts-silk.sh
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
silk task check
```

`font-collection` is covered by workspace checking; it has no `src/tests.silk`
test root. Shaping runtime tests use the recursively checked-out upstream corpus.
Keep the `modules/` fixture layout intact. The retained `test-support/fonts/` files and
licenses support font tests. `silk task generate-casefold` regenerates face-matching
data offline from sources authenticated by `scripts/casefold.lock.json`. Use
`--fetch` to hydrate missing locked sources (requires curl), or `--update` to
explicitly refresh the pins. `--fetch` never updates the lock.

### Internal executables and WebAssembly

These tools are separate from the seven consumer libraries:

- [font-parse-test-harness](font-parse-test-harness): internal parse dumper;
  package and binary name `font-parse-test-harness`.
- [font-shape-test-harness](font-shape-test-harness): internal shaping CLI;
  package and binary name `font-shape-test-harness`.
- [modules/parse/bench](modules/parse/bench): benchmark-only `font-parse-bench`.
- [modules/shape/tools/wasm](modules/shape/tools/wasm): retained consumer WebAssembly
  wrapper, `font-shape-wasm`, with its JavaScript wrapper under `js/`.

With LLVM's `wasm-ld` on `PATH`, build the WebAssembly wrapper:

```sh
silk task build-wasm
```

The task also installs the artifact at
`modules/shape/tools/wasm/js/dist/harfrust.wasm`.

### CI and optional maintainer tooling

[Fonts CI](.github/workflows/fonts.yml) installs the workspace-pinned Silk release,
checks the workspace, runs the six native test roots on Linux and macOS, and
builds the two internal harnesses and parser benchmark. Its Linux job also checks
and builds the WebAssembly wrapper. CI runs the same Silk tasks used locally;
WebAssembly compilation is not a JavaScript wrapper runtime test.
The installer and LLVM selection run before the first task: tasks themselves are
compiled programs, and this Silk release requires Clang 22 or newer to build them.

Run `silk task` to list maintenance commands. Tasks live in `src/` and run from the
repository root, including when selected with `--manifest-path`.

```sh
silk task build --release              # Rust reference and Silk parser tools
silk task build --reference-only       # Rust reference only
silk task generate-casefold --fetch    # hydrate authenticated Unicode inputs
silk task generate-color-fonts         # author COLRv0, sbix and CBDT raster fixtures
silk task generate                    # regenerate parser and shaping data
silk task generate-shaping-tests --check
silk task font-list --output build/fonts.txt
silk task test-harness                 # native orchestration and mutation tests
```

`generate --check` retains the original dirty-tree gate: it regenerates and formats,
then fails if tracked package outputs differ from Git. Individual generator tasks
offer non-publishing `--check` modes where listed by their help.

Reference comparisons still use the pinned Rust domain tools in
[modules/scripts](modules/scripts) (`rust-font-dump` and `rust-hr-shape`), and
require Cargo plus the recursive upstream submodules. JavaScript wrapper runtime
tests remain JavaScript so they exercise the public JavaScript API, not a substitute
Silk interface. Color-font generation writes sfnt tables and PNG images directly
in Silk; it preserves the fixture geometry, palettes and bitmap metrics, without
requiring fontTools. Regeneration may change font serialization, not those contracts.

Native harness tasks need Silk's managed subprocess API, which this pinned release does not
export on Windows ([silk#3034](https://github.com/silk-lang/silk/issues/3034)); there is no
separate Windows script path. Native CI targets Linux and macOS. Historical porting notes and
results under [modules/docs](modules/docs) are not fresh verification, and the
original nonstd weekly baseline workflow is not claimed here.

## Provenance and licensing

Extracted from `fonts/` in
[silk-lang/nonstd at 7d6c3693a9ad1fec24127985626ab4224f9f1995](https://github.com/silk-lang/nonstd/tree/7d6c3693a9ad1fec24127985626ab4224f9f1995/fonts).
Earlier implementation history remains in that source snapshot. The extraction retains
implementations, fixtures, upstream gitlinks and existing license notices; it does not vendor
the other libraries.

The parsing and shaping work began as ports of Google's
[fontations](https://github.com/googlefonts/fontations) and
[harfrust](https://github.com/harfbuzz/harfrust). `font-types` and `font-parse` retain
their [MIT](modules/LICENSE-MIT) or [Apache-2.0](modules/LICENSE-APACHE) licensing;
`font-shape` retains its [MIT license](modules/shape/LICENSE). Consult the retained
notices for individual source files, upstream data and font fixtures; this overview
does not replace their licenses.
