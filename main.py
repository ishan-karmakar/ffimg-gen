from PIL import Image, ImageDraw, ImageFont
import bitmath
import yaml
import numpy as np
import argparse

RESOLUTION_X = 1920
RESOLUTION_Y = 1080
PADDING = RESOLUTION_X / 100
USABLE_WIDTH = RESOLUTION_X - PADDING * 2
USABLE_HEIGHT = RESOLUTION_Y - PADDING * 2
ROW_HEIGHT = RESOLUTION_Y / 10
FONT_SIZE = ROW_HEIGHT / 3

"""
width = field_size * BYTE_SIZE
widths below WIDTH_THRESHOLD will be used directly
widths above WIDTH_THRESHOLD will scale linearly to max_width
"""
WIDTH_THRESHOLD = RESOLUTION_X / 2
MAX_WIDTH = USABLE_WIDTH
BYTE_WIDTH = RESOLUTION_X / 10

def get_width(size: bitmath.Bitmath, text_size: int):
    width = size.bytes * BYTE_WIDTH
    if width > WIDTH_THRESHOLD:
        width = np.interp(
            width,
            (WIDTH_THRESHOLD, max_size.bytes),
            (WIDTH_THRESHOLD, MAX_WIDTH)
        )
    return max(width, text_size + PADDING * 2)

def draw_blocks(draw: ImageDraw.ImageDraw, blocks: list):
    # Extend the previous blocks to fill the whole line
    last_block = blocks[-1]
    remainder = (USABLE_WIDTH + PADDING) - (last_block[0][0] + last_block[1])
    for i in range(len(blocks)):
        if i != 0:
            blocks[i][0][0] = blocks[i - 1][0][0] + blocks[i - 1][1]
        blocks[i][1] += remainder / len(blocks)
        block = blocks[i]
        draw.rectangle(
            (block[0][0], block[0][1], block[0][0] + block[1], block[0][1] + ROW_HEIGHT),
            outline="black",
            fill="orange"
        )
        draw.text(
            (block[0][0] + block[1] / 2, block[0][1] + ROW_HEIGHT / 2),
            block[2],
            anchor="md",
            font_size=FONT_SIZE,
            fill="black"
        )
        draw.text(
            (block[0][0] + block[1] / 2, block[0][1] + ROW_HEIGHT / 2),
            block[3],
            anchor="ma",
            font_size=FONT_SIZE,
            fill="black"
        )

bitmath.format_plural = True
bitmath.format_string = "{value:.0f} {unit}"

with open("spec.yaml") as file:
    spec = yaml.safe_load(file)
image = Image.new("RGB", (RESOLUTION_X, RESOLUTION_Y), "white")
draw = ImageDraw.Draw(image)

max_size = max(bitmath.parse_string(field["size"]) for category in spec for field in category["fields"])

x = PADDING
y = PADDING
blocks = []
for category in spec:
    for field in category["fields"]:
        size = bitmath.parse_string(field["size"])
        width = get_width(
            size,
            draw.textlength(field["name"], font_size=FONT_SIZE)
        )
        if x + width > PADDING + USABLE_WIDTH:
            # Wrap around to next line
            y += ROW_HEIGHT + PADDING
            x = PADDING
            draw_blocks(draw, blocks)
            blocks.clear()

        blocks.append([
            [x, y],
            width,
            field["name"],
            str(size)
        ])
        x += width
draw_blocks(draw, blocks)
image.save("output.png")