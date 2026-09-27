"""Builds the static Matrix-themed SVGs used by the profile README.

Run from the repo root:  python .github/scripts/build_assets.py
Edit PROJECTS / STACK below and re-run to update the cards and stack panel.
"""
import os, random, re, urllib.request
from html import escape

OUT = "assets"
BG, LINE, GREEN, DIM, TEXT, MUTED, GLOW = "#080C0B", "#1E2925", "#3DD68F", "#1C8A57", "#E0E6E3", "#8FA39A", "#B6FFD9"
MONO = "'IBM Plex Mono','JetBrains Mono',Consolas,'Courier New',monospace"
GLYPHS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワ0123456789Z:=*+¦"
CW = 0.6  # monospace advance, as a fraction of font size

random.seed(121)
os.makedirs(os.path.join(OUT, "cards"), exist_ok=True)


def save(name, parts):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts) + "\n")


def t(x, y, s, size=14, fill=TEXT, extra=""):
    return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" {extra}>{s}</text>'


def rain(w, h, step=20, size=14, opacity=0.55, speed=(5, 11), density=1.0):
    """Falling glyph columns. Each column is one <text> translated top to bottom."""
    out = [f'<g opacity="{opacity}">']
    for x in range(10, w, step):
        if random.random() > density:
            continue
        n = random.randint(6, 16)
        spans = []
        for i in range(n):
            last = i == n - 1
            a = 1 if last else 0.12 + 0.6 * (i / n) ** 1.6
            spans.append(f'<tspan x="{x}" dy="{size + 2}" fill="{GLOW if last else GREEN}" fill-opacity="{a:.2f}">{random.choice(GLYPHS)}</tspan>')
        d, delay = random.uniform(*speed), random.uniform(0, 10)
        out.append(f'<text class="rain" style="animation-duration:{d:.1f}s;animation-delay:-{delay:.1f}s" font-family="{MONO}" font-size="{size}">{"".join(spans)}</text>')
    out.append("</g>")
    css = (f".rain{{animation:fall linear infinite}}@keyframes fall{{from{{transform:translateY(-{h + 40}px)}}to{{transform:translateY({h + 40}px)}}}}")
    return css, out


def windows_keyframes(name, cycle, spans, on=1, off=0):
    """Discrete opacity keyframes: `on` inside each (start, end) second-window of the cycle."""
    frames = [f"0%{{opacity:{off}}}"]
    for a, b in spans:
        frames.append(f"{a / cycle * 100:.3f}%{{opacity:{on}}}")
        frames.append(f"{b / cycle * 100:.3f}%{{opacity:{off}}}")
    frames.append(f"100%{{opacity:{off}}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


# ----------------------------------------------------------------------------- header
def header():
    W, H = 1200, 340
    css_rain, rain_g = rain(W, H)
    css = [css_rain, ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}",
           ".scan{animation:scan 7s linear infinite}@keyframes scan{from{transform:translateY(-40px)}to{transform:translateY(" + str(H) + "px)}}"]
    body = []

    # name that decodes from glyphs, then glitches a few letters every cycle
    name, size, ls = "AHILL SELVARAJ", 50, 9
    adv = size * CW + ls
    x0 = 600 - adv * len(name) / 2 + adv / 2
    cycle = 9.0
    for i, ch in enumerate(name):
        if ch == " ":
            continue
        x = x0 + i * adv
        s = 0.15 + 0.06 * i
        wins = [(s, s + 0.55)]
        if i in (2, 7, 11):  # periodic glitch
            g = 5.5 + (i % 3) * 0.35
            wins.append((g, g + 0.3))
        hide = [(a, b) for a, b in wins]
        css.append(windows_keyframes(f"n{i}", cycle, hide, on=0, off=1))
        body.append(f'<text x="{x:.1f}" y="176" text-anchor="middle" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{GREEN}" style="animation:n{i} {cycle}s step-end infinite">{ch}</text>')
        for k in range(4):
            spans = [(a + (b - a) * k / 4, a + (b - a) * (k + 1) / 4) for a, b in wins]
            css.append(windows_keyframes(f"n{i}g{k}", cycle, spans))
            body.append(f'<text x="{x:.1f}" y="176" text-anchor="middle" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{GLOW}" opacity="0" style="animation:n{i}g{k} {cycle}s step-end infinite">{random.choice(GLYPHS)}</text>')

    # rotating typed lines
    lines = ["wake up, visitor...", "the profile has you.", "follow the green rabbit.", "knock, knock."]
    slot, fs = 4.0, 18
    total = slot * len(lines)
    for j, line in enumerate(lines):
        w = len(line) * fs * CW
        lx = 600 - w / 2
        a, b = j * slot, (j + 1) * slot
        css.append(windows_keyframes(f"l{j}", total, [(a, b)]))
        p = lambda s: f"{s / total * 100:.3f}%"
        ts, te = a + 0.3, a + 0.3 + 0.07 * len(line)
        css.append(f"@keyframes m{j}{{0%{{transform:translateX(0)}}{p(ts)}{{transform:translateX(0);animation-timing-function:steps({len(line)})}}"
                   f"{p(te)}{{transform:translateX({w:.1f}px)}}{p(b)}{{transform:translateX({w:.1f}px)}}{p(b + 0.001) if b < total else '100%'}{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}")
        body.append(f'<g opacity="0" style="animation:l{j} {total}s step-end infinite">'
                    f'<text x="{lx:.1f}" y="218" font-family="{MONO}" font-size="{fs}" fill="{TEXT}" textLength="{w:.1f}" lengthAdjust="spacing">{escape(line)}</text>'
                    f'<g style="animation:m{j} {total}s linear infinite"><rect x="{lx:.1f}" y="199" width="{w + 20:.1f}" height="26" fill="{BG}"/>'
                    f'<rect class="cur" x="{lx + 1:.1f}" y="202" width="{fs * CW - 1:.1f}" height="20" fill="{GREEN}"/></g></g>')

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Ahill Selvaraj. Full-stack, applied AI, security, data.">',
             "<style>" + "".join(css) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>",
             f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset="1" stop-color="{GREEN}" stop-opacity=".07"/></linearGradient></defs>',
             f'<rect width="{W}" height="{H}" fill="{BG}"/>', *rain_g,
             f'<rect x="220" y="62" width="760" height="216" rx="6" fill="{BG}" fill-opacity=".93" stroke="{LINE}"/>',
             t(248, 96, "00 / SIGNAL", 12, DIM, 'letter-spacing="2"'),
             t(952, 96, f'<tspan class="cur" fill="{GREEN}">●</tspan> COIMBATORE, IN · ONLINE', 12, DIM, 'text-anchor="end" letter-spacing="1"'),
             *body,
             t(600, 256, "FULL-STACK · APPLIED AI · SECURITY · DATA", 12, DIM, 'text-anchor="middle" letter-spacing="3"'),
             f'<rect class="scan" width="{W}" height="40" fill="url(#sg)"/>',
             "</svg>"]
    save("matrix-header.svg", parts)


# ----------------------------------------------------------------------------- project cards
PROJECTS = [
    # slug, name, stack, description, metric, host, repo, tag
    ("procureai", "ProcureAI", "Next.js · FastAPI · multi-agent", "Agents read invoices from email, OCR them and run a three-way PO match.", "~250ms dashboard", "sa-procure-ai.vercel.app", "ProcureAI", "AI SYSTEM"),
    ("datapulse", "DataPulse", "FastAPI · scikit-learn · Next.js", "Drop in a dataset; get cleaning, EDA, anomalies, a fitted model and a PDF/PPTX report.", "auto model selection", "sa-datapulse.vercel.app", "DataPulse", "AI SYSTEM"),
    ("silicon-gazette", "The Silicon Gazette", "Groq · Tavily · Next.js", "A daily tech newspaper written from live web search, set as a vintage broadsheet.", "one edition per day", "sa-silicon-gazette.vercel.app", "The-Silicon-Gazette", "AI SYSTEM"),
    ("gitverdict", "GitVerdict", "Next.js · GitHub API · LLM", "Paste any repository URL and get a reasoned verdict on its code quality.", "zero config", "sa-git-verdict.vercel.app", "gitverdict", "AI SYSTEM"),
    ("kipd", "Kipd", "Next.js 14 · Neon · Capacitor", "Multi-tenant hotel & restaurant system: SSE kitchen display, Android shell, native UPI.", "multi-tenant SaaS", "sa-kipd.vercel.app", "KIPD", "PRODUCT"),
    ("categorycrash", "CategoryCrash", "PartyKit · Groq · Next.js", "Real-time multiplayer word game where an LLM referees every answer.", "<200ms llama-3.3 verdicts", "sa-category-crash.vercel.app", "CategoryCrash", "REAL-TIME"),
    ("wordbomb", "Word Bomb", "Next.js · WebSocket", "Multiplayer word-bombing game with live scores and a leaderboard.", "real-time rooms", "sa-word-bomb.vercel.app", "wordbomb", "REAL-TIME"),
    ("fam-tree", "Fam Tree", "Next.js · React", "Node-based family tree builder: draw your lineage, save it, share it.", "drag & connect", "sa-fam-tree-builder.vercel.app", "fam-tree", "PRODUCT"),
    ("devlens", "DevLens", "Next.js · GitHub API", "Builds a developer fingerprint from any GitHub profile: languages, repos, habits.", "instant analysis", "sa-dev-lens.vercel.app", "devlens", "DEV TOOL"),
    ("leet-api", "leet-api", "Go · Fiber", "Unofficial LeetCode stats API; also renders the heatmap SVG on this page.", "public · free", "leetapi.vercel.app", "leet-api", "API"),
    ("exercism-api", "exercism-api", "Go · Fiber", "Exercism tracks, exercises and a contribution heatmap as a REST API.", "public · free", "sa-exercismapi.vercel.app", "exercism-api", "API"),
    ("weather", "Weather Dashboard", "Next.js · Weather API", "Global weather lookup with nothing on screen that isn't needed.", "live data", "sa-weather-dashboard.vercel.app", "WEATHER-DASHBOARD", "PRODUCT"),
]


def wrap(s, n):
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def card(i, slug, name, stack, desc, metric, host, repo, tag):
    W, H = 480, 220
    per = 2 * (W - 1 + H - 1)
    dur, delay = 6 + (i % 3), i * 0.9
    css_rain, rain_g = rain(90, H, step=18, size=12, opacity=0.35, speed=(6, 12), density=0.9)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(name)}: {escape(desc)}">',
        f"<style>{css_rain}.p{{animation:p 2s ease-in-out infinite}}@keyframes p{{50%{{opacity:.2}}}}"
        f".tr{{stroke-dasharray:90 {per - 90};animation:tr {dur}s linear infinite;animation-delay:-{delay:.1f}s}}@keyframes tr{{to{{stroke-dashoffset:-{per}}}}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>",
        f'<defs><clipPath id="c"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="6"/></clipPath>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>',
        f'<g clip-path="url(#c)"><g transform="translate({W - 100},0)">', *rain_g,
        f'<rect width="60" height="{H}" fill="url(#fade)"/></g></g>',
        f'<rect class="tr" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" stroke="{GREEN}" stroke-width="1.5" stroke-linecap="round"/>',
        t(24, 34, f'{i:02d} <tspan fill="{LINE}">/</tspan> ~/{slug}', 12, DIM, 'letter-spacing="1"'),
        f'<rect x="{W - 24 - len(tag) * 7.2 - 16:.1f}" y="20" width="{len(tag) * 7.2 + 16:.1f}" height="20" rx="3" fill="{BG}" stroke="{DIM}"/>',
        t(f"{W - 32}", 34, escape(tag), 11, GREEN, 'text-anchor="end" letter-spacing="1"'),
        t(24, 76, escape(name), 26, GREEN, 'font-weight="700"'),
        t(24, 100, escape(stack.upper()), 11, DIM, 'letter-spacing="1.5"'),
    ]
    for k, line in enumerate(wrap(desc, 48)[:3]):
        parts.append(t(24, 130 + k * 19, escape(line), 13.5, TEXT))
    parts += [
        f'<line x1="24" y1="184" x2="{W - 24}" y2="184" stroke="{LINE}"/>',
        t(24, 205, f"&gt; {escape(metric)}", 12, GREEN),
        t(W - 24, 205, f'<tspan class="p" fill="{GREEN}">●</tspan> {escape(host)}', 11, MUTED, 'text-anchor="end"'),
        "</svg>",
    ]
    save(f"cards/{slug}.svg", parts)


# ----------------------------------------------------------------------------- stack panel
STACK = [
    ("frontend", [("nextdotjs", "next.js"), ("react", "react"), ("typescript", "typescript"), ("tailwindcss", "tailwind"), ("capacitor", "capacitor")]),
    ("backend", [("go", "go/fiber"), ("python", "python"), ("fastapi", "fastapi"), ("nodedotjs", "node.js"), ("socketdotio", "websockets")]),
    ("data", [("postgresql", "postgres"), ("mysql", "mysql"), ("mongodb", "mongodb"), ("redis", "redis"), ("drizzle", "drizzle"), ("neon", "neon")]),
    ("ai / ml", [(None, "groq"), ("langchain", "langchain"), ("scikitlearn", "scikit-learn"), ("pytorch", "pytorch"), ("huggingface", "hugging face"), ("ollama", "ollama")]),
    ("security", [("kalilinux", "kali"), ("owasp", "owasp"), ("burpsuite", "burp"), ("wireshark", "wireshark"), ("jsonwebtokens", "jwt/oauth")]),
    ("infra", [("docker", "docker"), ("amazonwebservices", "aws"), ("vercel", "vercel"), ("linux", "linux"), ("githubactions", "actions"), ("git", "git")]),
]


def icon_path(slug):
    url = f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg"
    svg = urllib.request.urlopen(url, timeout=20).read().decode()
    return re.search(r' d="([^"]+)"', svg).group(1)


def stack():
    W, row = 1000, 40
    H = 84 + row * len(STACK) + 30
    css = [".r{opacity:0;animation:in .4s ease forwards}@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}",
           ".cur{animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}",
           ".ic{animation:gl 5s ease-in-out infinite}@keyframes gl{0%,86%,100%{fill:" + GREEN + "}90%{fill:" + GLOW + "}}"]
    p = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>',
         *[f'<circle cx="{22 + 16 * k}" cy="20" r="4.5" fill="{LINE}"/>' for k in range(3)],
         t(W / 2, 24, "ahill@zion: ~/stack", 11, DIM, 'text-anchor="middle"'),
         f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{LINE}"/>',
         t(24, 66, f'$ <tspan fill="{TEXT}">tree -L 1 --icons</tspan>', 14, DIM)]
    n = 0
    for k, (cat, items) in enumerate(STACK):
        y = 66 + row * (k + 1)
        g = [t(24, y, escape(cat), 14, DIM)]
        x = 150
        for slug, label in items:
            if slug:
                g.append(f'<g transform="translate({x},{y - 15}) scale(.75)"><path class="ic" style="animation-delay:{n * 0.37 % 5:.2f}s" fill="{GREEN}" d="{icon_path(slug)}"/></g>')
            else:
                g.append(t(x + 9, y, "◆", 16, GREEN, 'text-anchor="middle"'))
            g.append(t(x + 26, y, escape(label), 14, TEXT))
            x += 26 + len(label) * 14 * CW + 26
            n += 1
        p.append(f'<g class="r" style="animation-delay:{0.3 + k * 0.2:.1f}s">{"".join(g)}</g>')
    y = 66 + row * (len(STACK) + 1)
    p.append(f'<g class="r" style="animation-delay:{0.3 + len(STACK) * 0.2:.1f}s">{t(24, y, f"$ <tspan class=\"cur\" fill=\"{GREEN}\">█</tspan>", 14, DIM)}</g>')
    save("stack.svg", [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">',
                       "<style>" + "".join(css) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}.r{opacity:1}}</style>", *p, "</svg>"])


# ----------------------------------------------------------------------------- buttons
def button(name, label, sub, color, glow, w=380):
    H = 74
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{escape(label)}">',
             f"<style>.g{{animation:g 2.6s ease-in-out infinite}}@keyframes g{{50%{{opacity:.35}}}}.s{{animation:s 3.2s ease-in-out infinite}}@keyframes s{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(4px)}}}}"
             "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>",
             f'<defs><linearGradient id="pill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{glow}"/><stop offset=".55" stop-color="{color}"/><stop offset="1" stop-color="{BG}" stop-opacity=".6"/></linearGradient>'
             f'<filter id="f" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter></defs>',
             f'<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{LINE}"/>',
             f'<rect class="g" x="22" y="25" width="54" height="24" rx="12" fill="{color}" filter="url(#f)"/>',
             f'<rect x="22" y="25" width="54" height="24" rx="12" fill="url(#pill)"/>',
             f'<rect x="30" y="29" width="22" height="5" rx="2.5" fill="#fff" fill-opacity=".45"/>',
             t(96, 34, escape(label), 15, TEXT, 'font-weight="700"'),
             t(96, 54, escape(sub), 12, MUTED),
             f'<g class="s">{t(w - 22, 44, "→", 18, color, "text-anchor=\"end\"")}</g>',
             "</svg>"]
    save(f"{name}.svg", parts)


# ----------------------------------------------------------------------------- quote
def quote():
    W, H = 1000, 120
    q = "code is poetry written in logic."
    fs = 22
    w = len(q) * fs * CW
    x = W / 2 - w / 2
    css = (f".m{{animation:m 9s infinite}}@keyframes m{{0%,6%{{transform:translateX(0);animation-timing-function:steps({len(q)})}}40%,100%{{transform:translateX({w:.1f}px)}}}}"
           ".cur{animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
           ".a{opacity:0;animation:a 9s infinite}@keyframes a{0%,42%{opacity:0}48%,100%{opacity:1}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}.m{transform:translateX(" + f"{w:.1f}" + "px)}.a{opacity:1}}")
    save("quote.svg", [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{q} (Ahill Selvaraj)">',
                       f"<style>{css}</style>",
                       f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>',
                       t(24, 30, "// fortune", 12, DIM),
                       t(f"{x:.1f}", 66, q, fs, GREEN, f'textLength="{w:.1f}" lengthAdjust="spacing"'),
                       f'<g class="m"><rect x="{x:.1f}" y="44" width="{w + 30:.1f}" height="30" fill="{BG}"/><rect class="cur" x="{x + 1:.1f}" y="47" width="{fs * CW - 1:.1f}" height="24" fill="{GREEN}"/></g>',
                       f'<g class="a">{t(W / 2, 96, "— ahill selvaraj", 13, MUTED, "text-anchor=\"middle\"")}</g>',
                       "</svg>"])


if __name__ == "__main__":
    header()
    for n, c in enumerate(PROJECTS, 1):
        card(n, *c)
    stack()
    button("pill-red", "take the red pill", "see how deep the repo goes", "#E5484D", "#FF9592")
    button("pill-blue", "take the blue pill", "open the portfolio, believe what you want", "#3E63DD", "#9EB1FF")
    button("transmit", "transmit a message", "opens a GitHub issue · I read every one", DIM, GREEN)
    quote()
    print("assets built")
