"""Writes /output/entry.png: a byte copy of the committed entry.png (drawn by render.py). Stdlib only, offline."""
import os
import shutil
import struct
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

with open(SRC, "rb") as f:
    data = f.read()
if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) > 1048576:
    sys.exit("entry.png is not a PNG of at most 1 MiB")
if data[-12:-4] != b"\x00\x00\x00\x00IEND":  # the gate needs a whole image, ending in its IEND chunk
    sys.exit("entry.png is truncated")
w, h = struct.unpack(">II", data[16:24])  # IHDR width, height
if w > 1024 or h > 1024:
    sys.exit(f"entry.png is {w}x{h}, over 1024")
os.makedirs(OUT, exist_ok=True)
shutil.copyfile(SRC, os.path.join(OUT, "entry.png"))
