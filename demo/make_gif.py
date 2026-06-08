"""
Headless generator for demo/agentbrake.gif — an illustrative terminal animation
of AgentBrake stopping a runaway agent on a real cost ceiling. The numbers match
the README's "Live cost visibility" example (cost climbs $0.40/step, warns at
80% of the $2.00 limit, stops at $2.00).

Run:  uv run --no-project --with pillow python demo/make_gif.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "agentbrake.gif")

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
SIZE = 26
reg = ImageFont.truetype(FONT_PATH, SIZE, index=0)
bold = ImageFont.truetype(FONT_PATH, SIZE, index=1)

BG = (13, 17, 23)
GRAY = (139, 148, 158)
WHITE = (221, 223, 226)
CYAN = (86, 194, 230)
YELLOW = (240, 200, 90)
RED = (243, 110, 130)
DIMRED = (200, 95, 112)
GREEN = (158, 226, 154)

PAD = 30
LINE_H = 38
ICON_W = 34
TOP_BAR = 44

# (text, color, font, icon)  icon in {None, "warn", "stop", "ok"}
LINES = [
    ("$ python my_agent.py", GRAY, reg, None),
    ("", WHITE, reg, None),
    ("[AgentBrake] step 1: web_search · running cost $0.40", CYAN, reg, None),
    ("[AgentBrake] step 2: web_search · running cost $0.80", CYAN, reg, None),
    ("[AgentBrake] step 3: web_search · running cost $1.20", CYAN, reg, None),
    ("[AgentBrake] step 4: web_search · running cost $1.60", CYAN, reg, None),
    ("[AgentBrake]  approaching cost limit (1.60 of 2.00)", YELLOW, reg, "warn"),
    ("[AgentBrake]  STOPPED  cost ceiling reached ($2.00 >= $2.00)", RED, bold, "stop"),
    ("  steps=5 tool_calls=5 llm_calls=5 cost=$2.00 elapsed=6.2s", DIMRED, reg, None),
    ("", WHITE, reg, None),
    ("  AgentBrake caught it before the bill grew", GREEN, reg, "ok"),
]

# progressive reveal: (n_lines_shown, duration_ms)
FRAMES = [
    (1, 650),
    (3, 600),
    (4, 520),
    (5, 520),
    (6, 520),
    (7, 850),    # the warning
    (9, 1800),   # the STOPPED moment lands
    (11, 2700),  # full output, hold
]

H = TOP_BAR + PAD + LINE_H * len(LINES) + PAD

_probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
_maxw = 0
for text, _c, font, icon in LINES:
    indent = ICON_W if icon else 0
    _maxw = max(_maxw, indent + int(_probe.textlength(text, font=font)))
W = PAD + _maxw + PAD


def draw_stop_icon(d, x, y, r):
    pts = []
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    d.polygon(pts, fill=(229, 72, 77), outline=(255, 255, 255))
    d.rectangle([x - r * 0.45, y - r * 0.16, x + r * 0.45, y + r * 0.16], fill=(255, 255, 255))


def draw_warn_icon(d, x, y, r):
    d.polygon([(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)],
              fill=(240, 200, 90), outline=(13, 17, 23))
    d.rectangle([x - 1.6, y - r * 0.35, x + 1.6, y + r * 0.25], fill=(13, 17, 23))
    d.ellipse([x - 1.7, y + r * 0.4, x + 1.7, y + r * 0.4 + 3.4], fill=(13, 17, 23))


def draw_ok_icon(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(63, 185, 80))
    d.line([(x - r * 0.45, y), (x - r * 0.05, y + r * 0.45), (x + r * 0.5, y - r * 0.45)],
           fill=(255, 255, 255), width=3)


def render(n_lines):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([PAD + i * 26, 16, PAD + i * 26 + 14, 30], fill=c)
    d.text((W / 2, 23), "agentbrake — demo", fill=GRAY,
           font=ImageFont.truetype(FONT_PATH, 20, index=0), anchor="mm")

    y = TOP_BAR + PAD
    for i in range(n_lines):
        text, color, font, icon = LINES[i]
        x = PAD
        if icon == "stop":
            draw_stop_icon(d, x + 12, y + LINE_H / 2 - 4, 13)
            x += 34
        elif icon == "ok":
            draw_ok_icon(d, x + 12, y + LINE_H / 2 - 4, 12)
            x += 34
        elif icon == "warn":
            draw_warn_icon(d, x + 12, y + LINE_H / 2 - 4, 12)
            x += 34
        d.text((x, y), text, fill=color, font=font)
        y += LINE_H
    return img


frames = [render(n) for n, _ in FRAMES]
durations = [ms for _, ms in FRAMES]
frames[0].save(
    OUT, save_all=True, append_images=frames[1:],
    duration=durations, loop=0, disposal=2, optimize=True,
)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
