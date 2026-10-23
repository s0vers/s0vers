"""Builds hello.svg for the GitHub profile README from the portfolio's pixel avatar."""
# Run from this repo: python scripts/build-hello.py assets/hello.svg scripts/sky.txt
# sky.txt is a data URL of the avatar window canvas, copied from s0vers.com in the browser.
import base64, io, json, random, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

SITE = "D:/Programming/Personal/s0vers.com"
OUT = sys.argv[1]
SKY = open(sys.argv[2]).read().strip()  # data URL of the window canvas, from the live site

# --- pixel data -------------------------------------------------------------
base = open(f"{SITE}/public/avatar-pixel.svg", encoding="utf8").read()
base_inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", base.strip())

frames = {}
for line in open(f"{SITE}/src/components/pixel-avatar-frames.ts", encoding="utf8"):
    m = re.match(r'\s+"?([\w:]+)"?: (\[.*\]),?$', line)
    if m:
        frames[m.group(1)] = json.loads(m.group(2))

def frame_paths(name):
    by_fill = {}
    for x, y, w, fill in frames[name]:
        by_fill.setdefault(fill, []).append(f"M{x} {y}h{w}v1h-{w}z")
    return "".join(f'<path fill="{f}" d="{"".join(d)}"/>' for f, d in by_fill.items())

# --- timeline (ms) ------------------------------------------------------------
LOOP = 16000
shows = {}  # frame -> [(start, end)]
def show(names, start, end):
    for n in names:
        shows.setdefault(n, []).append((start, end))

# Scenes, as on the site: code bubble, a double blink, steam off the cup, an idea, blinks.
show(["blink"], 2500, 2630)
show(["bubble", "code"], 4000, 6400)
for i, f in enumerate(["steam0", "steam1", "steam2", "steam3", "steam4"] * 2):
    show([f], 6800 + i * 240, 7040 + i * 240)
show(["blink"], 9200, 9310); show(["blink"], 9450, 9560)
show(["brows", "lookRight"], 10200, 10450)
show(["brows", "lookRight", "bubble", "idea"], 10450, 11950)
show(["happyEyes", "bubble", "idea"], 11950, 12550)
show(["lookLeft"], 13400, 14300); show(["lookRight"], 14450, 15150)
show(["blink"], 15500, 15630)

# Typing everywhere except during the idea.
rng = random.Random(7)
taps = ["tap0", "tap1", "tap2", "tap3", "tapFar"]
for lo, hi in [(0, 10100), (12900, LOOP)]:
    t = lo + 200
    while t < hi - 300:
        burst_end = min(t + rng.randint(1200, 2000), hi - 200)
        while t < burst_end:
            d = rng.randint(70, 110)
            show([rng.choice(taps)], t, t + d)
            t += d + rng.randint(35, 110)
        t += rng.randint(400, 900)

def animated(name):
    spans = sorted(shows[name])
    times, values = [0.0], ["0"]
    for s, e in spans:
        times += [s / LOOP, e / LOOP]
        values += ["1", "0"]
    kt = ";".join(f"{t:.5f}".rstrip("0").rstrip(".") or "0" for t in times)
    return (f'<g opacity="0">{frame_paths(name)}<animate attributeName="opacity" dur="{LOOP}ms" '
            f'repeatCount="indefinite" calcMode="discrete" values="{";".join(values)}" keyTimes="{kt}"/></g>')

overlays = frame_paths("cup:hemanta") + "".join(animated(n) for n in shows)

# Night lighting from the site: dim ambient, then the desk lamp and the laptop screen.
scene_defs = f"""
<g id="s"><path fill="none" d=""/>{base_inner}{overlays}</g>
<filter id="amb" color-interpolation-filters="sRGB"><feColorMatrix values="0.3 0 0 0 0  0 0.33 0 0 0  0 0 0.5 0 0  0 0 0 1 0"/></filter>
<filter id="t0" color-interpolation-filters="sRGB"><feColorMatrix values="1.05 0 0 0 0  0 0.92 0 0 0  0 0 0.7 0 0  0 0 0 1 0"/></filter>
<filter id="t1" color-interpolation-filters="sRGB"><feColorMatrix values="0.62 0 0 0 0  0 0.75 0 0 0  0 0 1 0 0  0 0 0 1 0"/></filter>
<radialGradient id="f0"><stop offset="0" stop-color="#fff" stop-opacity="0.95"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.4275"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="f1"><stop offset="0" stop-color="#fff" stop-opacity="0.6"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.27"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="m0" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="144"><ellipse cx="136" cy="76" rx="42" ry="30" fill="url(#f0)"/></mask>
<mask id="m1" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="144"><ellipse cx="96" cy="64" rx="26" ry="22" fill="url(#f1)"/></mask>
"""

# --- type -----------------------------------------------------------------------
GREETING = "Hi, I’m Sovers."
LINES = [
    "Sovers Tonmoy Pandey, or s0vers online. Based in Dhaka.",
    "Team Lead and software engineer at Typetech-IT.",
]

def font_data(weight, text):
    font = TTFont(f"{SITE}/src/assets/fonts/schibsted-grotesk-{weight}.ttf")
    sub = subset.Subsetter(subset.Options())
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO(); font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()

def oklch_grey(l):
    lin = l ** 3
    s = 1.055 * lin ** (1 / 2.4) - 0.055 if lin > 0.0031308 else 12.92 * lin
    return "#" + f"{round(s * 255):02x}" * 3

BG, CARD, FG, MUTED = oklch_grey(0.155), oklch_grey(0.19), oklch_grey(0.94), oklch_grey(0.69)
YELLOW = "#ffc700"

W, H = 920, 300
AV = dict(x=32, y=30, w=320, h=240)
TX = AV["x"] + AV["w"] + 44

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Pixel art of Sovers typing at a laptop in a room at night. Hi, I’m Sovers.">
<style>
@font-face{{font-family:S;font-weight:400;src:url(data:font/ttf;base64,{font_data(400, "".join(LINES))}) format("truetype")}}
@font-face{{font-family:S;font-weight:600;src:url(data:font/ttf;base64,{font_data(600, GREETING)}) format("truetype")}}
text{{font-family:S,ui-sans-serif,system-ui,sans-serif}}
.e{{opacity:0;animation:rise .5s cubic-bezier(.23,1,.32,1) forwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.e{{opacity:1;animation:none}}}}
</style>
<defs>
<clipPath id="card"><rect x="{AV['x']}" y="{AV['y']}" width="{AV['w']}" height="{AV['h']}" rx="14"/></clipPath>
<clipPath id="page"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse"><path d="M64 0H0V64" fill="none" stroke="#fff" stroke-opacity=".055"/></pattern>
<linearGradient id="gridFade" x1="0" x2="1"><stop offset=".35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="gridMask"><rect width="{W}" height="{H}" fill="url(#gridFade)"/></mask>
<radialGradient id="glow" cx=".5" cy="0" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
{scene_defs}
</defs>
<g clip-path="url(#page)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridMask)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
</g>
<g clip-path="url(#card)">
<rect x="{AV['x']}" y="{AV['y']}" width="{AV['w']}" height="{AV['h']}" fill="{CARD}"/>
<svg x="{AV['x']}" y="{AV['y']}" width="{AV['w']}" height="{AV['h']}" viewBox="0 0 192 144" shape-rendering="crispEdges">
<image href="{SKY}" x="11" y="9" width="37" height="52" style="image-rendering:pixelated" preserveAspectRatio="none"/>
<use href="#s" filter="url(#amb)"/>
<use href="#s" filter="url(#t0)" mask="url(#m0)"/>
<use href="#s" filter="url(#t1)" mask="url(#m1)"/>
</svg>
</g>
<rect x="{AV['x'] + .5}" y="{AV['y'] + .5}" width="{AV['w'] - 1}" height="{AV['h'] - 1}" rx="13.5" fill="none" stroke="#fff" stroke-opacity=".08"/>
<text class="e" x="{TX}" y="{H/2 - 22}" font-size="32" font-weight="600" letter-spacing="-0.64" fill="{FG}" style="animation-delay:.07s">{GREETING}</text>
<text class="e" x="{TX}" y="{H/2 + 16}" font-size="17" fill="{MUTED}" style="animation-delay:.14s">{LINES[0]}</text>
<text class="e" x="{TX}" y="{H/2 + 44}" font-size="17" fill="{MUTED}" style="animation-delay:.21s">{LINES[1]}</text>
</svg>
"""
# The base still has an empty path or two; strip the placeholder.
svg = svg.replace('<path fill="none" d=""/>', "")
open(OUT, "w", encoding="utf8").write(svg)
print(len(svg), "bytes;", len(shows), "animated frames")
