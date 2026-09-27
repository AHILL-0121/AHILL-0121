"""Shared design system for the profile SVGs.

Everything is drawn at GitHub's README column width (W = 840) so an
<img width="100%"> renders 1:1 and type sizes are real pixel sizes.
Fonts (JetBrains Mono, M PLUS 1 Code for katakana) are subset woff2 files
embedded as data URIs, since SVGs inside <img> cannot load external fonts.
"""
import base64, os, random
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "assets"
W = 840

C = {
    "bg0": "#060A08", "bg1": "#0B120F", "panel": "#050806",
    "line": "#16211C", "line2": "#223129",
    "green": "#3DD68F", "bright": "#B6F5D2", "deep": "#1C8A57",
    "text": "#E6EEE9", "body": "#AEBDB5", "muted": "#6B8075", "dim": "#2F4238",
}
HEAT = ["#0E1612", "#0E3B25", "#15653F", "#23A465", "#3DD68F"]
KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン0123456789:=*+"
ADV = 0.6  # JetBrains Mono advance width (em)


def tw(s, size, ls=0):
    """Rendered width of a monospace string."""
    return len(s) * (size * ADV + ls)


def _font(name, file):
    with open(os.path.join(HERE, "fonts", file), "rb") as f:
        return base64.b64encode(f.read()).decode()


def font_css(weights=(400, 700), kata=False):
    css = [f"@font-face{{font-family:M;font-weight:{w};src:url(data:font/woff2;base64,{_font('M', f'jbm-{w}.woff2')}) format('woff2')}}" for w in weights]
    if kata:
        css.append(f"@font-face{{font-family:K;src:url(data:font/woff2;base64,{_font('K', 'kata-500.woff2')}) format('woff2')}}")
    css.append("text{font-family:M,'JetBrains Mono',ui-monospace,Consolas,monospace}.k{font-family:K,M,monospace}")
    return "".join(css)


def svg(w, h, body, label, css="", weights=(400, 700), kata=False):
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">',
        f"<title>{escape(label)}</title>",
        "<style>" + font_css(weights, kata) + css +
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.fx{opacity:1!important;transform:none!important}}</style>",
        *body, "</svg>"]) + "\n"


def save(name, content):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def t(x, y, s, size=14, fill=None, weight=400, anchor=None, ls=0, cls=None, extra="", raw=False):
    a = [f'x="{x:.1f}"' if isinstance(x, float) else f'x="{x}"', f'y="{y}"', f'font-size="{size}"', f'fill="{fill or C["body"]}"']
    if weight != 400:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if ls:
        a.append(f'letter-spacing="{ls}"')
    if cls:
        a.append(f'class="{cls}"')
    if extra:
        a.append(extra)
    return f'<text {" ".join(a)}>{s if raw else escape(s)}</text>'


def micro(x, y, s, fill=None, anchor=None):
    """Small uppercase label."""
    return t(x, y, s.upper(), 10.5, fill or C["muted"], 500, anchor, 1.6)


def rounded_path(x, y, w, h, r):
    """(tl, tr, br, bl) radii."""
    tl, tr, br, bl = r
    return (f"M{x + tl},{y} H{x + w - tr} Q{x + w},{y} {x + w},{y + tr} V{y + h - br} Q{x + w},{y + h} {x + w - br},{y + h} "
            f"H{x + bl} Q{x},{y + h} {x},{y + h - bl} V{y + tl} Q{x},{y} {x + tl},{y} Z")


def tile(w, h, r=14, radii=None, edge=True, uid="t"):
    """Panel background: vertical gradient, hairline border, lit top edge."""
    d = rounded_path(0.5, 0.5, w - 1, h - 1, radii or (r, r, r, r))
    out = [f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["bg1"]}"/><stop offset="1" stop-color="{C["bg0"]}"/></linearGradient>'
           f'<linearGradient id="{uid}e" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}" stop-opacity="0"/><stop offset=".5" stop-color="{C["green"]}" stop-opacity=".45"/><stop offset="1" stop-color="{C["green"]}" stop-opacity="0"/></linearGradient></defs>',
           f'<path d="{d}" fill="url(#{uid}g)" stroke="{C["line"]}"/>']
    if edge:
        out.append(f'<rect x="{w * 0.15:.0f}" y="0.5" width="{w * 0.7:.0f}" height="1" fill="url(#{uid}e)"/>')
    return out


def rain(x0, y0, w, h, step=16, size=13, rng=None, speed=(4.5, 9.5), density=0.85, head=True):
    """Falling katakana columns inside a box (caller clips). Returns (css, elements)."""
    rng = rng or random.Random(7)
    els = []
    for x in range(int(x0 + step / 2), int(x0 + w), step):
        if rng.random() > density:
            continue
        n = rng.randint(7, 18)
        spans = []
        for i in range(n):
            last = i == n - 1
            a = 1 if (last and head) else 0.08 + 0.62 * (i / n) ** 1.8
            col = C["bright"] if last and head else C["green"]
            spans.append(f'<tspan x="{x}" dy="{size + 3}" fill="{col}" fill-opacity="{a:.2f}">{rng.choice(KATA)}</tspan>')
        d, delay = rng.uniform(*speed), rng.uniform(0, 10)
        els.append(f'<text class="k rn" y="{y0}" font-size="{size}" style="animation-duration:{d:.1f}s;animation-delay:-{delay:.1f}s">{"".join(spans)}</text>')
    travel = h + 18 * (size + 3)
    css = f".rn{{animation:rn linear infinite}}@keyframes rn{{from{{transform:translateY(-{18 * (size + 3)}px)}}to{{transform:translateY({travel}px)}}}}"
    return css, els


def wrap(s, n):
    lines, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > n:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


def windows(name, cycle, spans, on=1, off=0):
    """Discrete opacity keyframes: `on` inside each (start, end) window (seconds) of the cycle."""
    f = [f"0%{{opacity:{off}}}"]
    for a, b in spans:
        f += [f"{a / cycle * 100:.3f}%{{opacity:{on}}}", f"{b / cycle * 100:.3f}%{{opacity:{off}}}"]
    f.append(f"100%{{opacity:{off}}}")
    return f"@keyframes {name}{{{''.join(f)}}}"


def typewriter(uid, x, y, s, size, fill, cycle, start, end, cps=0.065, weight=400, cursor=True, still=True):
    """Per-character reveal (no masking rectangles). Characters appear one by one from
    `start`, stay until `end` (seconds within `cycle`), then reset. Returns (css, elements)."""
    adv = size * ADV
    css, els = [], []
    for i, ch in enumerate(s):
        if ch == " ":
            continue
        css.append(windows(f"{uid}c{i}", cycle, [(start + i * cps, end)]))
        els.append(t(x + i * adv, y, ch, size, fill, weight, cls="fx" if still else None, extra=f'opacity="0" style="animation:{uid}c{i} {cycle}s step-end infinite"'))
    if cursor:
        te = start + len(s) * cps
        p = lambda v: f"{v / cycle * 100:.3f}%"
        css.append(windows(f"{uid}cv", cycle, [(start - 0.2, end)]))
        css.append(f"@keyframes {uid}cm{{0%{{transform:translateX(0)}}{p(start)}{{transform:translateX(0);animation-timing-function:steps({len(s)},end)}}"
                   f"{p(te)}{{transform:translateX({len(s) * adv:.1f}px)}}{p(end - 0.001)}{{transform:translateX({len(s) * adv:.1f}px)}}{p(end)}{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}")
        els.append(f'<g opacity="0" style="animation:{uid}cv {cycle}s step-end infinite"><g style="animation:{uid}cm {cycle}s linear infinite">'
                   f'<rect class="blink" x="{x + 1:.1f}" y="{y - size * 0.8:.1f}" width="{adv - 2:.1f}" height="{size * 1.05:.1f}" fill="{C["green"]}"/></g></g>')
        css.append(".blink{animation:blink 1.05s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    return "".join(css), els
