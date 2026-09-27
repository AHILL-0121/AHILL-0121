"""Builds the static profile SVGs (hero, nav, sections, about, projects, stack, roadmap, contact, footer).

Run from the repo root:  python .github/scripts/build_assets.py
Content lives in the data blocks below; edit and re-run.
"""
import json, os, random, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix import C, W, KATA, micro, rain, rounded_path, save, svg, t, tile, tw, typewriter, windows, wrap  # noqa: E402

rng = random.Random(121)
GAP = 8  # gap between side-by-side tiles; README widths are derived from it

# ----------------------------------------------------------------------------- data
NAME = "AHILL S"
ROLE = "Full-stack engineer · applied AI · security"
TYPED = ["wake up, visitor...", "the profile has you.", "follow the green rabbit.", "knock, knock."]

BIO = ("I build AI products and the full-stack systems around them. My first two internships "
       "were in cybersecurity, so I learned how systems break before I started shipping my own. "
       "Everything I make goes live.")
FACTS = [("education", "B.Tech IT + Honours AI & DS", "SNS College of Technology"),
         ("cgpa", "8.94", "honours track"),
         ("certified", "10+ credentials", "AWS · Cisco · IBM · NPTEL"),
         ("based", "Coimbatore, India", "IST · UTC+05:30")]
TRAJECTORY = [("now", "Shipping 12 live products", "AI systems · SaaS · dev tools"),
              ("2025", "Data Science Intern", "NXTLOGIC Software Solutions"),
              ("2024", "Cybersecurity Intern", "Ether Infotech"),
              ("2023", "Ethical Hacking Intern", "Virtual Coincent"),
              ("2022", "B.Tech IT begins", "SNS College of Technology")]

FEATURED = [
    # slug, name, tag, description, stack, metric, host
    ("procureai", "ProcureAI", "AI system", "Agents pull invoices from email, OCR them and run a three-way purchase-order match.",
     ["Next.js", "FastAPI", "multi-agent"], "~250ms dashboard", "sa-procure-ai.vercel.app"),
    ("kipd", "Kipd", "SaaS", "Multi-tenant hotel & restaurant platform with an SSE kitchen display and an Android shell.",
     ["Next.js 14", "Neon", "Capacitor"], "native UPI flow", "sa-kipd.vercel.app"),
    ("datapulse", "DataPulse", "ML pipeline", "Drop in a dataset; get cleaning, EDA, anomaly detection, a fitted model and a report.",
     ["FastAPI", "scikit-learn", "Next.js"], "auto model selection", "sa-datapulse.vercel.app"),
    ("categorycrash", "CategoryCrash", "Real-time", "Multiplayer word game where an LLM referees every answer while the round is live.",
     ["PartyKit", "Groq", "Next.js"], "<200ms verdicts", "sa-category-crash.vercel.app"),
]
INDEX = [
    # slug, name, tag, description
    ("silicon-gazette", "Silicon Gazette", "AI", "Daily tech broadsheet written from live web search"),
    ("gitverdict", "GitVerdict", "AI", "Paste a repo URL, get a reasoned code-quality verdict"),
    ("devlens", "DevLens", "Dev tool", "A developer fingerprint from any GitHub profile"),
    ("leet-api", "leet-api", "API", "LeetCode stats + the heatmap SVG, in Go / Fiber"),
    ("exercism-api", "exercism-api", "API", "Exercism tracks and exercises as a REST API"),
    ("wordbomb", "Word Bomb", "Real-time", "Multiplayer word-bomb game over WebSockets"),
    ("fam-tree", "Fam Tree", "Product", "Drag-and-connect family tree builder"),
    ("weather", "Weather", "Product", "Global weather lookup, nothing extra on screen"),
]

STACK = [
    ("frontend", [("nextdotjs", "next.js"), ("react", "react"), ("typescript", "typescript"), ("tailwindcss", "tailwind"), ("capacitor", "capacitor")]),
    ("backend", [("go", "go · fiber"), ("python", "python"), ("fastapi", "fastapi"), ("nodedotjs", "node.js"), ("socketdotio", "websockets")]),
    ("data", [("postgresql", "postgres"), ("mysql", "mysql"), ("mongodb", "mongodb"), ("redis", "redis"), ("drizzle", "drizzle")]),
    ("ai · ml", [("langchain", "langchain"), ("scikitlearn", "scikit-learn"), ("pytorch", "pytorch"), ("huggingface", "hugging face"), ("ollama", "ollama")]),
    ("security", [("kalilinux", "kali"), ("owasp", "owasp"), ("burpsuite", "burp suite"), ("wireshark", "wireshark"), ("jsonwebtokens", "jwt · oauth")]),
    ("infra", [("docker", "docker"), ("amazonwebservices", "aws"), ("vercel", "vercel"), ("linux", "linux"), ("githubactions", "actions")]),
]

ROADMAP = [
    ("done", ["Next.js advanced patterns", "Go Fiber REST APIs", "MySQL schema design", "JWT & OAuth",
              "WebSocket real-time apps", "GenAI API integration", "NIDS · OWASP"]),
    ("in progress", ["LangChain", "Vector databases", "ML pipelines", "Kubernetes & DevOps", "React Native"]),
    ("next", ["Autonomous AI agents", "Microservices", "Data science dashboards", "AWS Solutions Architect", "Mobile-first AI SaaS"]),
]

NAV = [("01", "about"), ("02", "work"), ("03", "stack"), ("04", "signal"), ("05", "contact")]
CONTACT = [("email", "say hello"), ("linkedin", "ahill-selvaraj"), ("portfolio", "sa-portfolio-psi"), ("guestbook", "leave a signal")]


# ----------------------------------------------------------------------------- icons (cached in repo)
ICON_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons.json")


def icons():
    cache = json.load(open(ICON_CACHE)) if os.path.exists(ICON_CACHE) else {}
    for _, items in STACK:
        for slug, _ in items:
            if slug not in cache:
                s = urllib.request.urlopen(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg", timeout=20).read().decode()
                cache[slug] = re.search(r' d="([^"]+)"', s).group(1)
    json.dump(cache, open(ICON_CACHE, "w"), indent=0)
    return cache


# ----------------------------------------------------------------------------- hero
def hero():
    H = 380
    PX, PY, PW, PH = 540, 24, 276, H - 48  # rain panel
    css = []
    b = tile(W, H, uid="h")

    # rain panel
    rcss, rels = rain(PX, PY, PW, PH, step=17, size=13, rng=rng, density=1.0, speed=(3.5, 7.5))
    _, back = rain(PX + 8, PY, PW, PH, step=17, size=10, rng=rng, density=0.9, speed=(6, 11), head=False)
    rels = ['<g opacity=".45">'] + back + ["</g>"] + rels
    css.append(rcss)
    b += [f'<defs><clipPath id="rp"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>'
          f'<linearGradient id="rf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["panel"]}"/><stop offset=".22" stop-color="{C["panel"]}" stop-opacity="0"/>'
          f'<stop offset=".78" stop-color="{C["panel"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["panel"]}"/></linearGradient></defs>',
          f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>',
          f'<g clip-path="url(#rp)"><g opacity=".9">', *rels, "</g>",
          f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#rf)"/></g>',
          micro(PX + 16, PY + 24, "signal", C["deep"]),
          t(PX + PW - 16, PY + 24, "● LIVE", 10.5, C["green"], 500, "end", 1.6, cls="pulse"),
          micro(PX + 16, PY + PH - 16, "11.01°N  76.96°E", C["deep"]),
          ]
    css.append(".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}")

    # header row
    b += [f'<circle cx="46" cy="52" r="3.5" fill="{C["green"]}" class="pulse"/>',
          micro(58, 56, "ahill-0121 / profile"),
          ]

    # name with decode + periodic glitch
    size, ls = 80, 2
    adv = size * 0.6 + ls
    cycle = 10.0
    for i, ch in enumerate(NAME):
        if ch == " ":
            continue
        x = 40 + i * adv
        s = 0.2 + 0.09 * i
        wins = [(s, s + 0.6)]
        if i in (1, 6):
            g = 6.2 + i * 0.2
            wins.append((g, g + 0.28))
        css.append(windows(f"n{i}", cycle, wins, on=0, off=1))
        b.append(t(x, 176, ch, size, C["text"], 800, extra=f'style="animation:n{i} {cycle}s step-end infinite"'))
        for k in range(3):
            spans = [(a + (bb - a) * k / 3, a + (bb - a) * (k + 1) / 3) for a, bb in wins]
            css.append(windows(f"n{i}g{k}", cycle, spans))
            b.append(t(x + 6, 172, rng.choice(KATA[:46]), size * 0.8, C["green"], 400, cls="k", extra=f'opacity="0" style="animation:n{i}g{k} {cycle}s step-end infinite"'))
    # green period after the name, the only ornament
    b.append(f'<rect x="{40 + len(NAME) * adv + 4:.0f}" y="160" width="14" height="16" fill="{C["green"]}"/>')

    b.append(t(40, 220, ROLE, 16, C["body"]))

    # rotating typed line
    fs, slot = 14, 4.2
    total = slot * len(TYPED)
    b.append(t(40, 262, "$", fs, C["deep"], 500))
    for j, line in enumerate(TYPED):
        c, els = typewriter(f"l{j}", 58, 262, line, fs, C["green"], total, j * slot + 0.3, (j + 1) * slot - 0.05, still=(j == 0))
        css.append(c)
        b += els

    # meta row
    b.append(f'<line x1="40" y1="298" x2="{PX - 32}" y2="298" stroke="{C["line2"]}"/>')
    meta = [("based", "Coimbatore, IN", None), ("shipped", "12 live products", None), ("status", "open to work", C["green"])]
    for k, (lab, val, col) in enumerate(meta):
        x = 40 + k * 160
        b.append(micro(x, 326, lab))
        b.append(t(x, 348, val, 13.5, col or C["text"], 500))
    save("hero.svg", svg(W, H, b, "AHILL S. Full-stack engineer, applied AI, security.", "".join(css), (400, 500, 800), kata=True))


# ----------------------------------------------------------------------------- segmented controls
def segments(prefix, items, arrow, sub_style=False):
    n = len(items)
    sw, H = W // n, 56
    for k, (a, bb) in enumerate(items):
        r = (12 if k == 0 else 0, 12 if k == n - 1 else 0, 12 if k == n - 1 else 0, 12 if k == 0 else 0)
        b = [f'<path d="{rounded_path(0.5, 0.5, sw - 1 + (0 if k == n - 1 else 0.5), H - 1, r)}" fill="{C["bg1"]}" stroke="{C["line"]}"/>']
        if sub_style:
            b += [micro(20, 24, a), t(20, 43, bb, 13.5, C["text"], 500)]
        else:
            b += [t(20, 34, a, 11, C["green"], 700), t(46, 34, bb, 14, C["text"], 500)]
        b.append(t(sw - 20, 35, arrow, 14, C["muted"], anchor="end", cls="nudge"))
        d = "0,2px" if arrow == "↓" else "2px,-2px"
        css = ".nudge{animation:nudge 3s ease-in-out infinite}@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(" + d + ")}}"
        save(f"{prefix}-{(bb if not sub_style else a).replace(' ', '-')}.svg", svg(sw, H, b, f"{a} {bb}", css, (400, 500, 700)))


# ----------------------------------------------------------------------------- section titles
def section(idx, title, meta):
    H = 76
    tx = 40
    lx0 = tx + tw(title, 22) + 20
    lx1 = W - tw(meta, 10.5, 1.6) - 20
    b = [t(0, 50, idx, 12, C["green"], 700), t(tx, 50, title, 22, C["text"], 700),
         f'<line x1="{lx0:.0f}" y1="44.5" x2="{lx1:.0f}" y2="44.5" stroke="{C["line2"]}"/>',
         f'<rect class="sweep" x="{lx0:.0f}" y="44" width="60" height="1.5" fill="{C["green"]}"/>',
         micro(W, 49, meta, anchor="end")]
    css = ".sweep{animation:sweep 5s cubic-bezier(.6,0,.4,1) infinite}@keyframes sweep{0%%{transform:translateX(0);opacity:0}15%%{opacity:1}85%%{opacity:1}100%%{transform:translateX(%dpx);opacity:0}}" % (lx1 - lx0 - 60)
    save(f"section-{title.lower()}.svg", svg(W, H, b, f"{idx} {title}", css, (400, 500, 700)))


# ----------------------------------------------------------------------------- about
def about():
    H = 360
    w1 = 520
    w2 = W - w1 - GAP
    # bio
    b = tile(w1, H, uid="a")
    b.append(micro(28, 42, "readme"))
    for k, line in enumerate(wrap(BIO, 54)):
        b.append(t(28, 76 + k * 24, line, 14, C["text"] if k == 0 else C["body"]))
    y0 = 76 + len(wrap(BIO, 54)) * 24 + 18
    b.append(f'<line x1="28" y1="{y0}" x2="{w1 - 28}" y2="{y0}" stroke="{C["line"]}"/>')
    for k, (lab, val, sub) in enumerate(FACTS):
        x, y = 28 + (k % 2) * 240, y0 + 34 + (k // 2) * 72
        b += [micro(x, y, lab), t(x, y + 22, val, 14, C["green"] if lab == "cgpa" else C["text"], 500), t(x, y + 42, sub, 12, C["muted"])]
    save("about-readme.svg", svg(w1, H, b, "About: " + BIO, "", (400, 500)))

    # trajectory
    b = tile(w2, H, uid="b")
    b.append(micro(28, 42, "trajectory"))
    top, step = 84, 60
    b.append(f'<line x1="33.5" y1="{top}" x2="33.5" y2="{top + step * (len(TRAJECTORY) - 1)}" stroke="{C["line2"]}"/>')
    b.append(f'<rect class="flow" x="33" y="{top}" width="1.5" height="40" fill="{C["green"]}"/>')
    for k, (yr, role, org) in enumerate(TRAJECTORY):
        y = top + k * step
        if k == 0:
            b += [f'<circle cx="33.5" cy="{y}" r="9" fill="{C["green"]}" fill-opacity=".15" class="ping"/>',
                  f'<circle cx="33.5" cy="{y}" r="4" fill="{C["green"]}"/>']
        else:
            b.append(f'<circle cx="33.5" cy="{y}" r="3.5" fill="{C["bg0"]}" stroke="{C["deep"]}" stroke-width="1.5"/>')
        b += [micro(52, y - 6, yr, C["green"] if k == 0 else C["deep"]),
              t(52, y + 12, role, 13.5, C["text"], 500), t(52, y + 29, org, 11.5, C["muted"])]
    css = (".ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}@keyframes ping{0%{transform:scale(.6);opacity:1}100%{transform:scale(1.8);opacity:0}}"
           f".flow{{animation:flow 4s ease-in-out infinite}}@keyframes flow{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:1}}80%{{opacity:1}}100%{{transform:translateY({step * (len(TRAJECTORY) - 1) - 40}px);opacity:0}}}}")
    save("about-trajectory.svg", svg(w2, H, b, "Trajectory: " + "; ".join(f"{a} {r_}, {o}" for a, r_, o in TRAJECTORY), css, (400, 500)))
    return w1, w2


# ----------------------------------------------------------------------------- projects
def feature(i, slug, name, tag, desc, stack, metric, host):
    cw, H = (W - GAP) // 2, 268
    per = 2 * (cw + H)
    b = tile(cw, H, uid="f")
    b.append(t(cw - 18, H - 16, f"{i:02d}", 120, C["green"], 800, "end", extra='fill-opacity=".045"'))
    b += [t(26, 42, f"{i:02d}", 11, C["green"], 700), micro(50, 42, tag),
          f'<circle cx="{cw - 62}" cy="38" r="3" fill="{C["green"]}" class="pulse"/>', micro(cw - 26, 42, "live", C["green"], "end"),
          t(26, 88, name, 24, C["text"], 700)]
    for k, line in enumerate(wrap(desc, 44)[:3]):
        b.append(t(26, 120 + k * 21, line, 13.5, C["body"]))
    x = 26
    for s in stack:
        w = tw(s, 11) + 20
        b += [f'<rect x="{x}" y="{H - 88}" width="{w:.0f}" height="22" rx="11" fill="{C["bg0"]}" stroke="{C["line2"]}"/>',
              t(x + 10, H - 73, s, 11, C["body"])]
        x += w + 6
    b += [f'<line x1="26" y1="{H - 50}" x2="{cw - 26}" y2="{H - 50}" stroke="{C["line"]}"/>',
          t(26, H - 24, f"▸ {metric}", 12, C["green"], 500),
          t(cw - 26, H - 24, f"{host} ↗", 11.5, C["muted"], anchor="end"),
          f'<rect class="trace" x="0.5" y="0.5" width="{cw - 1}" height="{H - 1}" rx="14" fill="none" stroke="{C["green"]}" stroke-width="1" stroke-opacity=".45"/>']
    css = (".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
           f".trace{{stroke-dasharray:70 {per - 70};animation:trace 10s linear infinite;animation-delay:-{i * 2.3:.1f}s}}@keyframes trace{{to{{stroke-dashoffset:-{per}}}}}")
    save(f"work/{slug}.svg", svg(cw, H, b, f"{name}: {desc}", css, (400, 500, 700, 800)))
    return cw


def index_row(i, slug, name, tag, desc):
    H = 54
    b = tile(W, H, r=12, edge=False, uid="r")
    b += [t(24, 32, f"{i:02d}", 11, C["green"], 700), t(60, 33, name, 14.5, C["text"], 700),
          t(240, 33, desc, 13, C["body"])]
    cw = tw(tag.upper(), 10, 1.4) + 20
    b += [f'<rect x="{W - 64 - cw:.0f}" y="16" width="{cw:.0f}" height="22" rx="11" fill="none" stroke="{C["line2"]}"/>',
          t(W - 64 - cw / 2, 31, tag.upper(), 10, C["muted"], 500, "middle", 1.4),
          t(W - 24, 33, "↗", 14, C["green"], anchor="end")]
    save(f"work/row-{slug}.svg", svg(W, H, b, f"{name}: {desc}", "", (400, 500, 700)))


# ----------------------------------------------------------------------------- stack
def stack():
    ic = icons()
    H = 300
    cols = len(STACK)
    cw = (W - 40) / cols
    b = tile(W, H, uid="s")
    total = sum(len(i) for _, i in STACK)
    b += [micro(28, 42, f"stack · {total} tools"), t(W - 28, 42, "~/stack $ tree -L 1", 11.5, C["muted"], anchor="end"),
          f'<line x1="28" y1="60" x2="{W - 28}" y2="60" stroke="{C["line"]}"/>']
    n = 0
    for c, (cat, items) in enumerate(STACK):
        x = 20 + c * cw + 10
        if c:
            b.append(f'<line x1="{x - 10:.1f}" y1="84" x2="{x - 10:.1f}" y2="{H - 28}" stroke="{C["line"]}"/>')
        b.append(micro(x + 4, 94, cat, C["green"]))
        for k, (slug, label) in enumerate(items):
            y = 132 + k * 30
            g = (f'<g transform="translate({x + 4:.1f},{y - 12}) scale(.6)"><path d="{ic[slug]}" fill="{C["body"]}"/></g>'
                 + t(x + 26, y, label, 12.5, C["text"]))
            b.append(f'<g class="fx in" style="animation-delay:{0.15 + n * 0.05:.2f}s">{g}</g>')
            n += 1
    css = ".in{opacity:0;animation:in .5s ease forwards}@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
    alt = "Stack. " + ". ".join(f"{c}: " + ", ".join(l for _, l in i) for c, i in STACK)
    save("stack.svg", svg(W, H, b, alt, css, (400, 500)))


# ----------------------------------------------------------------------------- roadmap
def roadmap():
    rows = max(len(i) for _, i in ROADMAP)
    H = 104 + rows * 26 + 20
    cw = (W - 56) / 3
    b = tile(W, H, uid="m")
    b += [micro(28, 42, "roadmap"), micro(W - 28, 42, "3 tracks", anchor="end"),
          f'<line x1="28" y1="60" x2="{W - 28}" y2="60" stroke="{C["line"]}"/>']
    for c, (head, items) in enumerate(ROADMAP):
        x = 28 + c * cw
        if head == "done":
            mark, col = "✓", C["green"]
            b.append(t(x, 92, "✓", 13, C["green"], 700))
        elif head == "in progress":
            mark, col = "·", C["text"]
            b.append(f'<g transform="translate({x + 6},{87.5})"><circle r="5.5" fill="none" stroke="{C["line2"]}" stroke-width="2"/>'
                     f'<path class="spin" d="M0,-5.5 A5.5,5.5 0 0 1 5.5,0" fill="none" stroke="{C["green"]}" stroke-width="2" stroke-linecap="round"/></g>')
        else:
            mark, col = "○", C["muted"]
            b.append(f'<circle cx="{x + 6}" cy="87.5" r="5" fill="none" stroke="{C["muted"]}" stroke-width="1.5" stroke-dasharray="2 2.2"/>')
        b.append(micro(x + 22, 92, f"{head}  ·  {len(items)}", C["green"] if head != "next" else C["muted"]))
        for k, item in enumerate(items):
            y = 124 + k * 26
            prefix = {"done": "✓", "in progress": "▸", "next": "·"}[head]
            pc = {"done": C["deep"], "in progress": C["green"], "next": C["dim"]}[head]
            b += [t(x + 2, y, prefix, 12, pc, 700), t(x + 22, y, item, 13, C["text"] if head != "next" else C["body"])]
    css = ".spin{transform-origin:0 0;animation:spin 1.2s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
    alt = "Roadmap. " + ". ".join(f"{h}: " + ", ".join(i) for h, i in ROADMAP)
    save("roadmap.svg", svg(W, H, b, alt, css, (400, 500, 700)))


# ----------------------------------------------------------------------------- footer
def footer():
    H = 200
    q = "code is poetry written in logic."
    fs = 20
    w = tw(q, fs)
    x = (W - w) / 2
    rcss, rels = rain(0, 0, W, 90, step=22, size=12, rng=random.Random(3), speed=(6, 12), density=0.7, head=False)
    b = tile(W, H, uid="z")
    b += [f'<defs><clipPath id="fc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14"/></clipPath>'
          f'<linearGradient id="ff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["bg1"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["bg0"]}"/></linearGradient></defs>',
          f'<g clip-path="url(#fc)" opacity=".5">', *rels, "</g>",
          f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#ff)"/>',
          micro(W / 2, 64, "// fortune", C["deep"], "middle"),
          f'<g class="fx late">{t(W / 2, 136, "— ahill s", 12.5, C["muted"], anchor="middle")}</g>',
          micro(W / 2, 176, "end of transmission", C["green"], "middle")]
    tc, tels = typewriter("q", x, 104, q, fs, C["text"], 12, 0.5, 11.8, cps=0.08, weight=500)
    b[-3:-3] = tels
    css = (rcss + tc + ".late{opacity:0;animation:late 12s infinite}@keyframes late{0%,26%{opacity:0}32%,98%{opacity:1}100%{opacity:0}}")
    save("footer.svg", svg(W, H, b, f"{q} (ahill s). End of transmission.", css, (400, 500), kata=True))


if __name__ == "__main__":
    hero()
    segments("nav/nav", NAV, "↓")
    segments("nav/contact", CONTACT, "↗", sub_style=True)
    for idx, title, meta in [("01", "About", "whoami"), ("02", "Work", "12 shipped · all live"), ("03", "Stack", "tools i reach for"),
                             ("04", "Signal", "synced daily"), ("05", "Roadmap", "what's next"), ("06", "Contact", "open to work")]:
        section(idx, title, meta)
    w1, w2 = about()
    for n, f in enumerate(FEATURED, 1):
        feature(n, *f)
    for n, r in enumerate(INDEX, len(FEATURED) + 1):
        index_row(n, *r)
    stack()
    roadmap()
    footer()
    print(f"built - about widths {w1}/{w2} -> {w1 / W * 100:.2f}% / {w2 / W * 100:.2f}%")
