#!/bin/sh
# Downloads the open fonts the benchmark shapes into DIR, at pinned versions, and checks them.
#
#   fetch-fonts.sh DIR
set -eu
dir=${1:?the directory to fill}
mkdir -p "$dir"
get() {
  [ -f "$dir/$1" ] || curl -fsSL --retry 3 -o "$dir/$1" "$2"
  echo "$3  $dir/$1" | sha256sum -c - > /dev/null || { echo "$1: checksum mismatch" >&2; exit 1; }
}
noto=https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts
get NotoSans-Regular.ttf "$noto/NotoSans/hinted/ttf/NotoSans-Regular.ttf" \
  478c558ea716033cd60c03438f628dfa75694dcf6b5f6d505a2f05fd2b4f3823
get NotoNaskhArabic-Regular.ttf "$noto/NotoNaskhArabic/hinted/ttf/NotoNaskhArabic-Regular.ttf" \
  6f0a92031367b2f5a2078fe9d24f3433122b61a0bad57c423aad8f3c39aa2e6e
get NotoSansDevanagari-Regular.ttf "$noto/NotoSansDevanagari/hinted/ttf/NotoSansDevanagari-Regular.ttf" \
  4e3c66638958c3e2ab5d37f47a8deb89fffeb7be9985c665a519bbc7ba762313
get JetBrainsMono-Regular.ttf \
  https://raw.githubusercontent.com/JetBrains/JetBrainsMono/v2.304/fonts/ttf/JetBrainsMono-Regular.ttf \
  a0bf60ef0f83c5ed4d7a75d45838548b1f6873372dfac88f71804491898d138f
get NotoSansCJKsc-Regular.otf \
  https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf \
  2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b
get NotoColorEmoji.ttf \
  https://raw.githubusercontent.com/googlefonts/noto-emoji/v2.047/fonts/NotoColorEmoji.ttf \
  39ee3c587e10e89669b9ff32703261d10d5f9c4dd5ad147b6b5a1c5200591817
get Roboto-Regular.ttf \
  https://raw.githubusercontent.com/googlefonts/roboto-2/v2.138/src/hinted/Roboto-Regular.ttf \
  56a45233d29f11b4dfb86d248e921939d115778f87325e7ae8cc108383d6664d
if [ ! -f "$dir/Inter-Regular.ttf" ]; then
  curl -fsSL --retry 3 -o "$dir/inter.zip" https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip
  unzip -q -o -j "$dir/inter.zip" extras/ttf/Inter-Regular.ttf -d "$dir"
  rm "$dir/inter.zip"
fi
get Inter-Regular.ttf "" 64f8be6e55c37e32ef03da99714bf3aa58b8f2099bfe4f759a7578e3b8291123
