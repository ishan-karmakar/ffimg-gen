from PIL import Image, ImageDraw
import bitmath, yaml, re, argparse
import numpy as np

def get_width(size: bitmath.Bitmath, text_size: int):
    width = size.bytes * BYTE_WIDTH
    if width > WIDTH_THRESHOLD:
        width = np.interp(
            width,
            (WIDTH_THRESHOLD, MAX_SIZE.bytes * BYTE_WIDTH),
            (WIDTH_THRESHOLD, USABLE_WIDTH)
        )
    return max(width, text_size + PADDING * 2)

def draw_blocks(draw: ImageDraw.ImageDraw, blocks: list, y):
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

def estimate_layout(spec, draw: ImageDraw.ImageDraw, max_iterations=10):
    row_height = USABLE_HEIGHT / 10
    for _ in range(max_iterations):
        font_size = row_height / 3
        rows = 1
        x = PADDING

        for category in spec:
            for field in category["fields"]:
                width = get_width(
                    field["size"],
                    draw.textlength(max(field["name"], str(field["size"]), key=len), font_size=font_size)
                )

                if x + width > PADDING + USABLE_WIDTH:
                    rows += 1
                    x = PADDING
                x += width

        old_row_height = row_height
        rows = max(rows, 10)
        row_height = (USABLE_HEIGHT - PADDING * (rows - 1)) / rows
        if abs(old_row_height - row_height) < 1:
            break
    return row_height, font_size

def draw_layout(spec, draw: ImageDraw.ImageDraw):
    x = y = PADDING
    blocks = []
    for category in spec:
        for field in category["fields"]:
            width = get_width(
                field["size"],
                draw.textlength(max(field["name"], str(field["size"]), key=len), font_size=FONT_SIZE)
            )
            if x + width > PADDING + USABLE_WIDTH:
                draw_blocks(draw, blocks, y)
                rows += 1
                y += ROW_HEIGHT + PADDING
                x = PADDING
                blocks.clear()
            blocks.append([
                width,
                field
            ])
            x += width
    draw_blocks(draw, blocks, y)

def calculate_byte_width(data):
    # Remove outliers
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else np.zeros(len(d))
    return (USABLE_WIDTH / 10) / np.average(data[s < 5])

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

sizes = []
for category in spec:
    for field in category["fields"]:
        field["size"] = bitmath.parse_string(field["size"])
        sizes.append(field["size"].bytes)
BYTE_WIDTH = calculate_byte_width(np.array(sizes))
ROW_HEIGHT, FONT_SIZE = estimate_layout(spec, draw)
MAX_SIZE = max(field["size"] for category in spec for field in category["fields"])
draw_layout(spec, draw)
image.save(args.output)