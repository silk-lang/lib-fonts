// The HarfBuzz twin of font-shape-bench: the same modes, corpora, per-call work and output,
// as the speed reference and (with dump-MODE) the oracle.
//
//   cc -O2 hb_bench.c -o hb-bench $(pkg-config --cflags --libs harfbuzz)
#define _POSIX_C_SOURCE 199309L
#include <hb.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define SAMPLES 7

typedef struct { size_t start, length; } range_t;

static char *read_file(const char *path, size_t *length) {
  FILE *file = fopen(path, "rb");
  if (!file) return NULL;
  fseek(file, 0, SEEK_END);
  long size = ftell(file);
  fseek(file, 0, SEEK_SET);
  char *data = malloc((size_t)size + 1);
  if (fread(data, 1, (size_t)size, file) != (size_t)size) return NULL;
  fclose(file);
  *length = (size_t)size;
  return data;
}

static uint64_t mix(uint64_t hash, uint64_t value) { return (hash ^ value) * 1099511628211ull; }

static void pass(hb_font_t *font, hb_buffer_t *buffer, const char *text, const range_t *calls,
                 size_t count, uint64_t *checksum, uint64_t *glyphs) {
  for (size_t call = 0; call < count; call++) {
    hb_buffer_clear_contents(buffer);
    hb_buffer_add_utf8(buffer, text + calls[call].start, (int)calls[call].length, 0, -1);
    hb_buffer_guess_segment_properties(buffer);
    hb_shape(font, buffer, NULL, 0);
    unsigned length;
    hb_glyph_info_t *infos = hb_buffer_get_glyph_infos(buffer, &length);
    hb_glyph_position_t *positions = hb_buffer_get_glyph_positions(buffer, &length);
    uint64_t sum = *checksum;
    for (unsigned i = 0; i < length; i++) {
      sum = mix(sum, infos[i].codepoint);
      sum = mix(sum, infos[i].cluster);
      sum = mix(sum, (uint32_t)positions[i].x_advance);
      sum = mix(sum, (uint32_t)positions[i].y_advance);
      sum = mix(sum, (uint32_t)positions[i].x_offset);
      sum = mix(sum, (uint32_t)positions[i].y_offset);
    }
    *checksum = sum;
    *glyphs += length;
  }
}

int main(int argc, char **argv) {
  if (argc < 4) {
    fprintf(stderr, "Usage: hb-bench words|lines|dump-words|dump-lines FONT TEXT [ITERATIONS]\n");
    return 2;
  }
  const char *mode = argv[1];
  int flags = strncmp(mode, "flags-", 6) == 0;
  int dump = flags || strncmp(mode, "dump-", 5) == 0;
  if (dump) mode += flags ? 6 : 5;
  int words = strcmp(mode, "words") == 0;
  if (!words && strcmp(mode, "lines") != 0) return 2;
  size_t iterations = argc > 4 ? (size_t)atol(argv[4]) : 20;
  if (iterations == 0) return 2;
  size_t length = 0;
  char *text = read_file(argv[3], &length);
  hb_blob_t *blob = hb_blob_create_from_file_or_fail(argv[2]);
  if (!text || !blob) return 2;
  hb_face_t *face = hb_face_create(blob, 0);
  hb_font_t *font = hb_font_create(face);
  range_t *calls = malloc(sizeof(range_t) * (length + 1));
  size_t count = 0, start = 0;
  for (size_t at = 0; at <= length; at++) {
    if (at == length || text[at] == '\n' || (words && text[at] == ' ')) {
      if (at > start) calls[count++] = (range_t){start, at - start};
      start = at + 1;
    }
  }
  hb_buffer_t *buffer = hb_buffer_create();
  if (dump) {
    char line[1 << 16];
    for (size_t call = 0; call < count; call++) {
      uint64_t checksum = 0, glyphs = 0;
      pass(font, buffer, text, calls + call, 1, &checksum, &glyphs);
      unsigned total = hb_buffer_get_length(buffer), at = 0;
      printf("[");
      while (at < total) {
        unsigned written = 0;
        at += hb_buffer_serialize_glyphs(buffer, at, total, line, sizeof line, &written, font,
                                         HB_BUFFER_SERIALIZE_FORMAT_TEXT,
                                         HB_BUFFER_SERIALIZE_FLAG_NO_GLYPH_NAMES |
                                             (flags ? HB_BUFFER_SERIALIZE_FLAG_GLYPH_FLAGS : 0));
        if (!written) break;
        fwrite(line, 1, written, stdout);
      }
      printf("]\n");
    }
    return 0;
  }
  uint64_t checksum = 14695981039346656037ull, glyphs = 0;
  pass(font, buffer, text, calls, count, &checksum, &glyphs);
  int64_t best = 0;
  for (int sample = 0; sample < SAMPLES; sample++) {
    checksum = 14695981039346656037ull;
    glyphs = 0;
    struct timespec begin, end;
    clock_gettime(CLOCK_MONOTONIC, &begin);
    for (size_t iteration = 0; iteration < iterations; iteration++)
      pass(font, buffer, text, calls, count, &checksum, &glyphs);
    clock_gettime(CLOCK_MONOTONIC, &end);
    int64_t took = (end.tv_sec - begin.tv_sec) * 1000000000ll + (end.tv_nsec - begin.tv_nsec);
    if (sample == 0 || took < best) best = took;
  }
  uint64_t total_calls = (uint64_t)count * iterations;
  uint64_t per_call = (uint64_t)best * 10 / (total_calls + 1);
  uint64_t per_glyph = (uint64_t)best * 10 / (glyphs + 1);
  printf("calls %zu glyphs %llu ns/call %llu.%llu ns/glyph %llu.%llu checksum %llu\n", count,
         (unsigned long long)(glyphs / iterations), (unsigned long long)(per_call / 10),
         (unsigned long long)(per_call % 10), (unsigned long long)(per_glyph / 10),
         (unsigned long long)(per_glyph % 10), (unsigned long long)checksum);
  return 0;
}
