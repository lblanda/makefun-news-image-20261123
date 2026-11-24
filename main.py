"""Draw one editorial news poster for Monday 23 November 2026.

Pure Python standard library: a hand-written PNG encoder (zlib + CRC),
a 5x7 bitmap font (font5x7.py) and the day's stories (stories.py).
Writes /output/entry.png, a 1024x1024 PNG under 1 MiB.

Run:  MAKEFUN_OUTPUT_DIR=<dir> python3 -P -s main.py
"""

import math
import os
import struct
import sys
import zlib

# The grader runs `python3 -P -s /bot/main.py`, and -P keeps the script
# directory off sys.path, so sibling imports need this bootstrap first.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import font5x7
import stories

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 234)
INK = (18, 24, 40)
NAVY = (16, 35, 63)
NAVY_LIGHT = (38, 68, 110)
RED = (176, 32, 32)
BLUE = (30, 90, 168)
SKY = (120, 170, 220)
GREEN = (46, 125, 70)
GOLD = (184, 134, 11)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
CREAM = (232, 224, 205)

MARGIN = 28
CONTENT = WIDTH - 2 * MARGIN


def chunk(kind, data):
    """One PNG chunk: length, type, data, CRC32 of type+data."""
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(
        ">I", zlib.crc32(body) & 0xFFFFFFFF
    )


def encode_png(width, height, pixels):
    """Encode an RGB bytearray as a PNG (8-bit, colour type 2)."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += pixels[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )


class Canvas:
    """An RGB canvas with rectangle, line, circle and bitmap-text drawing."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def hline(self, x, y, w, colour):
        self.fill_rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.fill_rect(x, y, 1, h, colour)

    def fill_circle(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, colour)

    def circle(self, cx, cy, r, colour):
        for angle in range(360):
            rad = math.radians(angle)
            self.set_pixel(
                cx + int(r * math.cos(rad)), cy + int(r * math.sin(rad)), colour
            )

    def draw_text(self, x, y, text, scale, colour):
        """Draw text left-aligned at (x, y); returns the pixel width used."""
        cx = x
        for char in text:
            rows = font5x7.glyph(char)
            for ry, row in enumerate(rows):
                for rx, bit in enumerate(row):
                    if bit == "#":
                        self.fill_rect(
                            cx + rx * scale, y + ry * scale, scale, scale, colour
                        )
            cx += 6 * scale
        return cx - x - scale if text else 0

    def text_width(self, text, scale):
        return font5x7.text_width(text, scale)

    def draw_centred(self, y, text, scale, colour):
        w = self.text_width(text, scale)
        self.draw_text((self.width - w) // 2, y, text, scale, colour)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split()
            if not words:
                lines.append("")
                continue
            line = words[0]
            for word in words[1:]:
                trial = line + " " + word
                if self.text_width(trial, scale) <= max_width:
                    line = trial
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return lines


def draw_globe(canvas, cx, cy, r):
    """A simple stylised globe: blue disc, latitude bands, land blobs."""
    canvas.fill_circle(cx, cy, r, BLUE)
    # Latitude bands.
    for frac, colour in ((-0.55, SKY), (-0.2, SKY), (0.2, SKY), (0.55, SKY)):
        dy = int(r * frac)
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        canvas.fill_rect(cx - dx, cy + dy - 2, 2 * dx, 4, colour)
    # Meridian.
    for dx_off in (-r // 2, r // 2):
        canvas.vline(cx + dx_off, cy - r + 6, 2 * r - 12, SKY)
    canvas.circle(cx, cy, r, NAVY)
    # Land blobs, kept inside the disc.
    for bx, by, br in ((-38, -30, 20), (30, -42, 14), (42, 28, 22), (-30, 40, 16)):
        canvas.fill_circle(cx + bx, cy + by, br, GREEN)
    # Marker for Antalya.
    canvas.fill_circle(cx + 12, cy - 52, 5, RED)
    canvas.circle(cx + 12, cy - 52, 8, WHITE)


def draw_kicker(canvas, x, y, text, scale=2):
    canvas.draw_text(x, y, text, scale, RED)


def draw_headline(canvas, x, y, text, scale, max_width, colour=INK):
    lines = canvas.wrap(text, max_width, scale)
    for i, line in enumerate(lines):
        canvas.draw_text(x, y + i * (7 * scale + 4), line, scale, colour)
    return y + len(lines) * (7 * scale + 4)


def draw_body(canvas, x, y, text, scale, max_width, colour=INK, max_lines=None):
    """Draw wrapped body text; with max_lines, cut the last line short
    with an ellipsis so text can never spill into the next section."""
    lines = canvas.wrap(text, max_width, scale)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while canvas.text_width(last + "...", scale) > max_width and last:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "..."
    for i, line in enumerate(lines):
        canvas.draw_text(x, y + i * (7 * scale + 3), line, scale, colour)
    return y + len(lines) * (7 * scale + 3)


def truncate_to_width(canvas, text, max_width, scale):
    """Cut text at a word boundary so it fits, adding an ellipsis."""
    if canvas.text_width(text, scale) <= max_width:
        return text
    words = text.split()
    out = ""
    for word in words:
        trial = (out + " " + word).strip()
        if canvas.text_width(trial + "...", scale) <= max_width:
            out = trial
        else:
            break
    return out + "..." if out else text[:1]


def build():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # --- Masthead -------------------------------------------------------
    canvas.fill_rect(0, 0, WIDTH, 104, NAVY)
    canvas.draw_centred(14, stories.MASTHEAD, 9, WHITE)
    canvas.draw_centred(78, stories.DATE_LINE + "  •  " + stories.TAGLINE, 2, SKY)
    canvas.fill_rect(0, 104, WIDTH, 6, RED)

    # --- Lead story: COP31 collapses ------------------------------------
    y = 126
    draw_kicker(canvas, MARGIN, y, stories.LEAD["kicker"])
    y += 22
    y = draw_headline(canvas, MARGIN, y, stories.LEAD["headline"], 8, 640)
    y += 6
    draw_body(canvas, MARGIN, y, stories.LEAD["subhead"], 3, 620)
    draw_globe(canvas, 852, 268, 118)

    canvas.fill_rect(MARGIN, 458, CONTENT, 3, INK)

    # --- Second row: Zelensky (left) and Nvidia (right) ------------------
    col_w = (CONTENT - 36) // 2
    y = 476
    for i, story in enumerate((stories.SECOND, stories.THIRD)):
        x = MARGIN + i * (col_w + 36)
        draw_kicker(canvas, x, y, story["kicker"])
        yy = draw_headline(canvas, x, y + 20, story["headline"], 3, col_w)
        draw_body(canvas, x, yy + 4, story["body"], 2, col_w, max_lines=6)
        if i == 0:
            canvas.vline(MARGIN + col_w + 18, y, 176, CREAM)

    canvas.fill_rect(MARGIN, 668, CONTENT, 3, INK)

    # --- Third row: three columns ----------------------------------------
    col3_w = (CONTENT - 2 * 28) // 3
    y = 686
    for i, story in enumerate(stories.COLUMNS):
        x = MARGIN + i * (col3_w + 28)
        draw_kicker(canvas, x, y, story["kicker"], scale=2)
        yy = draw_headline(canvas, x, y + 20, story["headline"], 2, col3_w)
        draw_body(canvas, x, yy + 4, story["body"], 2, col3_w, max_lines=7)
        if i < 2:
            canvas.vline(MARGIN + (i + 1) * col3_w + i * 28 + 14, y, 168, CREAM)

    canvas.fill_rect(MARGIN, 872, CONTENT, 3, INK)

    # --- Also today ------------------------------------------------------
    y = 890
    canvas.draw_text(MARGIN, y, "ALSO TODAY", 2, RED)
    src = stories.FOOTER
    canvas.draw_text(
        WIDTH - MARGIN - canvas.text_width(src, 1), y + 4, src, 1, GREY
    )
    y += 24
    half = (CONTENT - 28) // 2
    for row in range(4):
        for col in range(2):
            item = stories.ALSO_TODAY[row * 2 + col]
            x = MARGIN + col * (half + 28)
            label, text = item
            line = truncate_to_width(
                canvas, label + ": " + text, half, 2
            )
            canvas.draw_text(x, y + row * 19, line, 2, INK)
        canvas.fill_rect(MARGIN, y + row * 19 + 15, CONTENT, 1, CREAM)

    # --- Footer rule ------------------------------------------------------
    canvas.fill_rect(0, HEIGHT - 8, WIDTH, 8, NAVY)

    return encode_png(WIDTH, HEIGHT, canvas.pixels)


def output_path():
    """Where to write entry.png. Never removes the output directory."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def main():
    png = build()
    path = output_path()
    if os.path.exists(path):
        os.remove(path)  # clear only the file, never the directory itself
    with open(path, "wb") as handle:
        handle.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
