import base64
from PIL import Image

INPUT = "output.png"
OUTPUT = "ImageData.txt"

image = Image.open(INPUT).convert("RGBA")
width, height = image.size

if width > 65535 or height > 65535:
    raise ValueError("Image dimensions cannot exceed 65535x65535.")

pixels = list(image.getdata())

palette = []
palette_map = {}

for r, g, b, a in pixels:
    if a != 255:
        raise ValueError("Image contains transparent pixels. The Roblox format only supports opaque pixels.")

    rgb = (round(r * 99 / 255), round(g * 99 / 255), round(b * 99 / 255))

    if rgb not in palette_map:
        palette_map[rgb] = len(palette)
        palette.append(rgb)

if len(palette) > 65535:
    raise ValueError("Image contains more than 65535 unique colors.")

encoded = bytearray()

encoded += width.to_bytes(2, "big")
encoded += height.to_bytes(2, "big")
encoded += len(palette).to_bytes(2, "big")

for r, g, b in palette:
    encoded += bytes((r, g, b))

indices = []

for r, g, b, a in pixels:
    rgb = (round(r * 99 / 255), round(g * 99 / 255), round(b * 99 / 255))
    indices.append(palette_map[rgb])

i = 0

while i < len(indices):
    index = indices[i]
    count = 1

    while i + count < len(indices) and indices[i + count] == index and count < 65535:
        count += 1

    encoded += count.to_bytes(2, "big")
    encoded += index.to_bytes(2, "big")

    i += count

result = base64.b64encode(bytes(encoded)).decode("ascii")

with open(OUTPUT, "w", encoding="ascii") as f:
    f.write("-- Data generated using I2B64 v1.0 (https://github.com/solal0/I2B64)\n-- You can copy and paste this file's content in a ModuleScript\nreturn[[" + result + "]]")

print(f"Compiled: {width}x{height}")
print(f"Palette: {len(palette)} colors")
print(f"Binary size: {len(encoded):,} bytes")
print(f"Base64 size: {len(result):,} characters")
print(f"Output: {OUTPUT}")