# I2B64 v1.1
# https://github.com/solal0/I2B64

import base64
import re
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def choose(title,filetypes):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost",True)
    path = filedialog.askopenfilename(title=title,filetypes=filetypes)
    root.destroy()
    return path

def save(title,filetypes,default_name):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost",True)
    path = filedialog.asksaveasfilename(title=title,filetypes=filetypes,initialfile=default_name,defaultextension=filetypes[0][1])
    root.destroy()
    return path

def compile():
    path = choose("Select image", [("Image files","*.png;*.jpg;*.jpeg;*.bmp;*.webp;*.gif"), ("All files","*.*")])
    if not path: return

    image = Image.open(path).convert("RGBA")
    width,height = image.size

    if width > 65535 or height > 65535:
        raise ValueError("Image dimensions cannot exceed 65535x65535.")

    pixels = list(image.getdata())
    palette = []
    palette_map = {}

    for r,g,b,a in pixels:
        rgba = (round(r*99/255), round(g*99/255), round(b*99/255), round(a*99/255))

        if rgba not in palette_map:
            palette_map[rgba] = len(palette)
            palette.append(rgba)

    if len(palette) > 65535:
        raise ValueError("Image contains more than 65535 unique colors.")

    encoded = bytearray()
    encoded += width.to_bytes(2,"big")
    encoded += height.to_bytes(2,"big")
    encoded += len(palette).to_bytes(2,"big")

    for r,g,b,a in palette:
        encoded += bytes((r,g,b,a))

    indices = [
        palette_map[(round(r*99/255), round(g*99/255), round(b*99/255), round(a*99/255))]
        for r,g,b,a in pixels
    ]

    i = 0

    while i < len(indices):
        index = indices[i]
        count = 1

        while i+count < len(indices) and indices[i+count] == index and count < 65535:
            count += 1

        encoded += count.to_bytes(2,"big")
        encoded += index.to_bytes(2,"big")
        i += count

    result = base64.b64encode(bytes(encoded)).decode("ascii")

    output = save("Save ImageData Lua module", [("Lua ModuleScript","*.lua"), ("All files","*.*")], "ImageData.lua")

    if not output:
        return

    with open(output,"w",encoding="ascii") as f:
        f.write(
            "-- Data generated using I2B64 (https://github.com/solal0/I2B64)\n"
            "-- You can copy and paste this file's content in a ModuleScript or copy the base64 alone and use it directly as the image data\n"
            "return[[" + result + "]]"
        )

    print()
    print(f"Compiled: {width}x{height}")
    print(f"Palette: {len(palette)} colors")
    print(f"Binary size: {len(encoded):,} bytes")
    print(f"Base64 size: {len(result):,} characters")
    print(f"Output: {output}")

def extract(source):
    source = source.strip()

    match = re.search(r"return\s*\[\[(.*?)\]\]",source,re.DOTALL)
    if match: return "".join(match.group(1).split())

    lines = []

    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("--"): continue
        lines.append(line)

    raw = "".join(lines)
    raw = re.sub(r"\s+","",raw)

    if not raw: raise ValueError("No Base64 data found.")
    if not re.fullmatch(r"[A-Za-z0-9+/]*={0,2}",raw): raise ValueError("The file does not contain valid I2B64 Base64 data.")

    return raw

def decompile():
    path = choose("Select ImageData Lua file", [("Lua files","*.lua"), ("All files","*.*")])
    if not path: return

    with open(path,"r",encoding="utf-8") as f:
        source = f.read()

    encoded = extract(source)

    try:
        data = base64.b64decode(encoded,validate=True)
    except Exception as e:
        raise ValueError(f"Invalid Base64 data: {e}")

    pos = 0

    def u8():
        nonlocal pos
        if pos >= len(data): raise ValueError("Unexpected end of image data.")
        value = data[pos]
        pos += 1
        return value

    def u16():
        return (u8()<<8)|u8()

    if len(data) < 6: raise ValueError("Image data is too short.")

    width = u16()
    height = u16()
    palette_count = u16()

    if width == 0 or height == 0: raise ValueError("Invalid image dimensions.")

    palette = []

    for _ in range(palette_count):
        palette.append((u8(),u8(),u8(),u8()))

    pixel_count = width*height
    pixels = bytearray(pixel_count*4)
    p = 0

    while pos <= len(data)-4 and p < pixel_count:
        count = u16()
        index = u16()

        if count == 0: raise ValueError("Invalid RLE count: 0.")
        if index >= len(palette): raise ValueError(f"Invalid palette index: {index}.")

        r,g,b,a = palette[index]

        r = round(r*255/99)
        g = round(g*255/99)
        b = round(b*255/99)
        a = round(a*255/99)

        for _ in range(count):
            if p >= pixel_count:
                break

            i = p*4
            pixels[i] = r
            pixels[i+1] = g
            pixels[i+2] = b
            pixels[i+3] = a

            p += 1

    if p != pixel_count:
        raise ValueError(f"Image data ended early. Expected {pixel_count:,} pixels, decoded {p:,}.")

    output = save("Save decoded image", [("PNG image","*.png")], "output.png")
    if not output: return

    image = Image.frombytes("RGBA",(width,height),bytes(pixels))
    image.save(output,"PNG")

    print()
    print(f"Decompiled: {width}x{height}")
    print(f"Palette: {len(palette)} colors")
    print(f"Output: {output}")

def main():
    print("I2B64 v1.0")
    print("https://github.com/solal0/I2B64")
    print()
    print("1. Compile")
    print("2. Decompile")
    print()

    action = input("Action: ").strip()

    if action == "1":
        compile()
    elif action == "2":
        decompile()
    else:
        print("Invalid action.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print(f"Error: {e}")

    input("\nPress Enter to exit...")