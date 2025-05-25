from PIL import Image, ImageDraw, ImageFont
import bitmath
import yaml
import numpy as np
import argparse
import re

def get_width(size: bitmath.Bitmath, text_size: int):
    width = size.bytes * BYTE_WIDTH
    if width > WIDTH_THRESHOLD:
        width = np.interp(
            width,
            (WIDTH_THRESHOLD, max_size.bytes * BYTE_WIDTH),
            (WIDTH_THRESHOLD, USABLE_WIDTH)
        )
    return max(width, text_size + PADDING * 2)

def draw_blocks(draw: ImageDraw.ImageDraw, blocks: list):
    # Extend the previous blocks to fill the whole line
    remainder = USABLE_WIDTH - sum(block[0] for block in blocks)
    x = PADDING
    for block in blocks:
        block[0] += remainder / len(blocks)
        draw.rectangle(
            (x, y, x + block[0], y + ROW_HEIGHT),
            outline="black",
            fill="orange"
        )
        draw.text(
            (x + block[0] / 2, y + ROW_HEIGHT / 2),
            block[1]["name"],
            anchor="md",
            font_size=FONT_SIZE,
            fill="black"
        )
        draw.text(
            (x + block[0] / 2, y + ROW_HEIGHT / 2),
            str(block[1]["size"]),
            anchor="ma",
            font_size=FONT_SIZE,
            fill="black"
        )
        x += block[0]

def calculate_byte_width(data):
    # Remove outliers
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else np.zeros(len(d))
    return (USABLE_WIDTH / 10) / np.average(data[s < 10])

def resolution(value):
    if not re.match("^[0-9]+x[0-9]+$", value):
        raise ValueError
    return tuple(int(x) for x in value.split("x"))

bitmath.format_plural = True
bitmath.format_string = "{value:.0f} {unit}"

parser = argparse.ArgumentParser(
    prog = "ffimg-gen",
    description = "A utility to create images describing a file format from a YAML spec file"
)
parser.add_argument("filename", help="Filename of the YAML spec file")
parser.add_argument("-o", "--output", default="output.png", help="Filename of the output image")
parser.add_argument("-r", "--resolution", default="1920x1080", type=resolution, help="Resolution of the output image in the format ___x___ (1280x720)")
args = parser.parse_args()

PADDING = args.resolution[0] / 100
USABLE_WIDTH = args.resolution[0] - PADDING * 2
USABLE_HEIGHT = args.resolution[1] - PADDING * 2
ROW_HEIGHT = USABLE_HEIGHT / 10
FONT_SIZE = ROW_HEIGHT / 3

"""
width = field_size * BYTE_SIZE
widths below WIDTH_THRESHOLD will be used directly
widths above WIDTH_THRESHOLD will scale linearly to max_width
"""
WIDTH_THRESHOLD = USABLE_WIDTH / 2

with open(args.filename) as file:
    spec = yaml.safe_load(file)
image = Image.new("RGB", args.resolution, "white")
draw = ImageDraw.Draw(image)

BYTE_WIDTH = calculate_byte_width(np.array(tuple(bitmath.parse_string(field["size"]).bytes for category in spec for field in category["fields"])))
max_size = max(bitmath.parse_string(field["size"]) for category in spec for field in category["fields"])

x = PADDING
y = PADDING
blocks = []
for category in spec:
    for field in category["fields"]:
        field["size"] = bitmath.parse_string(field["size"])
        width = get_width(
            field["size"],
            draw.textlength(max(field["name"], str(field["size"]), key=lambda x: len(x)), font_size=FONT_SIZE)
        )
        if x + width > PADDING + USABLE_WIDTH:
            # Wrap around to next line
            draw_blocks(draw, blocks)
            y += ROW_HEIGHT + PADDING
            x = PADDING
            blocks.clear()

        blocks.append([
            width,
            field
        ])
        x += width
draw_blocks(draw, blocks)
image.save(args.output)