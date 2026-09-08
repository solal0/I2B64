import base64
from PIL import Image

IMAGE_BASE64 = r"""
Raw I2B64 base64 goes here
"""

data = base64.b64decode(''.join(IMAGE_BASE64.split()))

pos = 0

def u8():
    global pos
    value = data[pos]
    pos += 1
    return value

def u16():
    return (u8() << 8) | u8()

width = u16()
height = u16()
palette_count = u16()

palette = []

for _ in range(palette_count):
    palette.append((u8(), u8(), u8()))

pixels = bytearray(width * height * 4)
pixel_count = width * height
p = 0

while pos <= len(data) - 4 and p < pixel_count:
    count = u16()
    index = u16()

    r, g, b = palette[index]

    r = int(r * 255 / 99 + 0.5)
    g = int(g * 255 / 99 + 0.5)
    b = int(b * 255 / 99 + 0.5)

    for _ in range(count):
        if p >= pixel_count:
            break

        i = p * 4
        pixels[i] = r
        pixels[i + 1] = g
        pixels[i + 2] = b
        pixels[i + 3] = 255

        p += 1

image = Image.frombytes("RGBA", (width, height), bytes(pixels))
image.save("output.png")

print(f"Image created: {width}x{height}")