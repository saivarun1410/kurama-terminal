#!/usr/bin/env python3
"""Render honest, staged README previews from the app's shipped sprites."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "previews"
OUT.mkdir(parents=True, exist_ok=True)

BG = (10, 13, 22)
PANEL = (19, 24, 37)
PANEL_LIGHT = (28, 35, 51)
CREAM = (255, 246, 228)
MUTED = (153, 165, 187)
ORANGE = (255, 143, 67)
GREEN = (122, 226, 169)
FONT = "/System/Library/Fonts/Avenir Next.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False):
    return ImageFont.truetype(MONO if mono else FONT, size)


def background(size, glow=(0.76, 0.63)):
    w, h = size
    image = Image.new("RGB", size, BG)
    pixels = image.load()
    gx, gy = w * glow[0], h * glow[1]
    for y in range(h):
        for x in range(w):
            radial = max(0.0, 1.0 - math.hypot(x - gx, y - gy) / (w * 0.7)) ** 3
            top = (1 - y / h) * 0.24
            pixels[x, y] = (
                int(10 + 55 * radial + 9 * top),
                int(13 + 19 * radial + 12 * top),
                int(22 + 16 * radial + 20 * top),
            )
    return image.convert("RGBA")


def panel(image, box, radius=28, fill=PANEL, shadow=18):
    if shadow:
        layer = Image.new("RGBA", image.size)
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((box[0], box[1] + 14, box[2], box[3] + 14), radius, fill=(0, 0, 0, 115))
        image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(image).rounded_rectangle(box, radius, fill=fill, outline=(59, 67, 87), width=2)


def pill(draw, xy, label, fill=(71, 44, 38), text=ORANGE, size=22):
    x, y = xy
    f = font(size)
    width = int(draw.textlength(label, font=f)) + 34
    draw.rounded_rectangle((x, y, x + width, y + 42), 21, fill=fill)
    draw.text((x + 17, y + 7), label, font=f, fill=text)
    return width


def sprite(image, name, box):
    art = Image.open(ROOT / "assets" / f"{name}.png").convert("RGBA")
    art.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    x = box[0] + (box[2] - box[0] - art.width) // 2
    y = box[1] + (box[3] - box[1] - art.height) // 2
    image.alpha_composite(art, (x, y))


def terminal(image, box, lines, title="Terminal - kurama", text_size=27):
    panel(image, box, 24, PANEL, 24)
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle((x0, y0, x1, y0 + 64), radius=24, fill=PANEL_LIGHT)
    draw.rectangle((x0, y0 + 35, x1, y0 + 64), fill=PANEL_LIGHT)
    for i, color in enumerate(((255, 92, 87), (255, 188, 65), (39, 201, 89))):
        cx = x0 + 29 + 28 * i
        draw.ellipse((cx - 8, y0 + 24, cx + 8, y0 + 40), fill=color)
    draw.text((x0 + 135, y0 + 18), title, font=font(24, True), fill=(174, 183, 200))
    y = y0 + 95
    for text, color in lines:
        draw.text((x0 + 56, y), text, font=font(text_size, True), fill=color)
        y += text_size + 26


def footer(draw, w, h):
    label = "STAGED PREVIEW  /  ACTUAL APP SPRITES"
    f = font(17, True)
    draw.text((w - int(draw.textlength(label, font=f)) - 42, h - 38), label, font=f, fill=(130, 138, 156))


def save(image, name):
    image.convert("RGB").save(OUT / name, optimize=True)
    print(name, (OUT / name).stat().st_size)


hero = background((1600, 900))
d = ImageDraw.Draw(hero)
pill(d, (94, 58), "macOS terminal companion")
d.text((94, 111), "A little fox for your terminal.", font=font(66), fill=CREAM)
d.text((98, 194), "Blinks, tilts, respects your secrets, and waves goodbye.", font=font(30), fill=MUTED)
terminal(hero, (94, 277, 1506, 811), [
    ("dev@mac ~ % kurama status", CREAM),
    ("Kurama is running", GREEN),
    ("dev@mac ~ % swift build", CREAM),
    ("Build complete!", GREEN),
    ("dev@mac ~ % _", ORANGE),
], text_size=27)
sprite(hero, "idle", (1040, 366, 1464, 793))
d = ImageDraw.Draw(hero)
footer(d, 1600, 900)
save(hero, "terminal-hero.png")


gallery = background((1600, 1110), glow=(0.55, 0.47))
d = ImageDraw.Draw(gallery)
d.text((93, 55), "Meet every mood.", font=font(62), fill=CREAM)
d.text((96, 132), "The same companion, with six small reactions.", font=font(28), fill=MUTED)
poses = [
    ("idle", "01  IDLE", "A gentle float"),
    ("blink", "02  BLINK", "Every 1–2 seconds"),
    ("tilt", "03  TILT LEFT", "Curious about your work"),
    ("tilt_opposite", "04  TILT RIGHT", "Alternates every 5 seconds"),
    ("privacy", "05  PRIVACY", "Paws over the eyes"),
    ("wave", "06  GOODBYE", "A wave when you quit"),
]
for i, (pose, label, detail) in enumerate(poses):
    col, row = i % 3, i // 3
    x = 95 + col * 475
    y = 225 + row * 407
    panel(gallery, (x, y, x + 440, y + 372), 26, (21, 27, 40), 12)
    sprite(gallery, pose, (x + 65, y + 16, x + 375, y + 291))
    d = ImageDraw.Draw(gallery)
    d.text((x + 32, y + 297), label, font=font(25, True), fill=ORANGE)
    d.text((x + 32, y + 330), detail, font=font(20), fill=MUTED)
footer(ImageDraw.Draw(gallery), 1600, 1110)
save(gallery, "expression-gallery.png")


privacy = background((1400, 820))
d = ImageDraw.Draw(privacy)
pill(d, (82, 52), "privacy mode")
d.text((82, 108), "Secrets stay yours.", font=font(64), fill=CREAM)
d.text((85, 190), "Kurama covers its eyes when a sensitive command begins.", font=font(27), fill=MUTED)
terminal(privacy, (84, 287, 1316, 740), [
    ("dev@mac ~ % kurama privacy on", GREEN),
    ("dev@mac ~ % sudo -v", CREAM),
    ("Password:", ORANGE),
], text_size=25)
sprite(privacy, "privacy", (907, 346, 1286, 727))
footer(ImageDraw.Draw(privacy), 1400, 820)
save(privacy, "privacy-mode.png")


goodbye = background((1400, 820), glow=(0.83, 0.48))
d = ImageDraw.Draw(goodbye)
pill(d, (82, 52), "goodbye")
d.text((82, 108), "See you next session.", font=font(64), fill=CREAM)
d.text((85, 190), "Exit the terminal or quit the pet and get a wave.", font=font(27), fill=MUTED)
terminal(goodbye, (84, 287, 1316, 740), [
    ("dev@mac ~ % kurama quit", CREAM),
], text_size=25)
sprite(goodbye, "wave", (887, 346, 1266, 727))
d = ImageDraw.Draw(goodbye)
d.rounded_rectangle((761, 326, 890, 388), 22, fill=(255, 246, 228))
d.text((791, 338), "Bye!", font=font(34), fill=(104, 39, 28))
footer(d, 1400, 820)
save(goodbye, "goodbye-wave.png")


def animation_frame(pose, label):
    frame = background((900, 510))
    terminal(frame, (32, 40, 868, 466), [
        ("% kurama status", CREAM),
        ("Kurama is running", GREEN),
        (f"% {label}", ORANGE),
    ], text_size=23)
    sprite(frame, pose, (570, 119, 848, 451))
    if pose == "wave":
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((465, 151, 552, 192), 16, fill=(255, 246, 228))
        draw.text((483, 156), "Bye!", font=font(21), fill=(104, 39, 28))
    return frame.convert("RGB")


sequence = [
    ("idle", "hello", 850),
    ("blink", "hello", 170),
    ("idle", "hello", 720),
    ("tilt", "curious...", 850),
    ("idle", "hello", 680),
    ("blink", "hello", 170),
    ("idle", "hello", 640),
    ("tilt_opposite", "curious...", 850),
    ("privacy", "sudo -v", 1150),
    ("wave", "kurama quit", 950),
]
frames = [animation_frame(pose, label) for pose, label, _ in sequence]
frames = [
    frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    for frame in frames
]
frames[0].save(
    OUT / "kurama-in-action.gif",
    save_all=True,
    append_images=frames[1:],
    duration=[duration for _, _, duration in sequence],
    loop=0,
    optimize=False,
    disposal=2,
)
print("kurama-in-action.gif", (OUT / "kurama-in-action.gif").stat().st_size)
