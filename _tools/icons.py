"""
draws the fox-berg.com favicons from one little pixel fox. no pip installs.

    python3 _tools/icons.py

writes favicon.svg, favicon-32.png and apple-touch-icon.png. folders starting
with _ aren't published by github pages, so this file stays off the site.
"""
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# catppuccin mocha
PAL = {
    "B": "#11111b",  # crust, the background
    "P": "#fab387",  # peach, the fur
    "W": "#f5e0dc",  # rosewater, cheeks and chin
    "K": "#1e1e2e",  # base, eyes and nose
    "E": "#eba0ac",  # maroon, inside the ears
}

# 16x16. "." is background
FOX = [
    "................",
    "..P..........P..",
    "..PP........PP..",
    "..PEP......PEP..",
    "..PEEP....PEEP..",
    "..PPPPPPPPPPPP..",
    ".PPPPPPPPPPPPPP.",
    ".PPPKKPPPPKKPPP.",
    ".PPPKKPPPPKKPPP.",
    ".WPPPPPPPPPPPPW.",
    ".WWWPPPPPPPPWWW.",
    "..WWWWPPPPWWWW..",
    "...WWWWWWWWWW...",
    ".....WWKKWW.....",
    "......WWWW......",
    "................",
]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def png(path, size, pad):
    """nearest-neighbor scale of FOX onto a size x size square, pad pixels of crust around it."""
    inner = size - 2 * pad
    bg = rgb(PAL["B"])
    rows = []
    for y in range(size):
        row = bytearray([0])  # filter: none
        for x in range(size):
            c = bg
            if pad <= x < size - pad and pad <= y < size - pad:
                ch = FOX[(y - pad) * 16 // inner][(x - pad) * 16 // inner]
                if ch != ".":
                    c = rgb(PAL[ch])
            row += bytes(c)
        rows.append(bytes(row))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = zlib.compress(b"".join(rows), 9)
    head = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


def svg(path):
    rects = []
    for y, row in enumerate(FOX):
        x = 0
        while x < 16:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < 16 and row[x + run] == ch:
                run += 1
            rects.append(f'<rect x="{x + 2}" y="{y + 2}" width="{run}" height="1" fill="{PAL[ch]}"/>')
            x += run
    body = "\n  ".join(rects)
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" shape-rendering="crispEdges">\n'
        f'  <rect width="20" height="20" rx="4" fill="{PAL["B"]}"/>\n  {body}\n</svg>\n'
    )


if __name__ == "__main__":
    svg(ROOT / "favicon.svg")
    png(ROOT / "favicon-32.png", 32, 0)
    png(ROOT / "apple-touch-icon.png", 180, 18)
    print("wrote favicon.svg, favicon-32.png, apple-touch-icon.png")
