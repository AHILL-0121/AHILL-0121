"""Renders assets/stats.svg (Matrix telemetry panel) from the GitHub API.

Uses GITHUB_TOKEN when present (adds the contributions-this-year number via GraphQL);
works unauthenticated with the REST numbers only.
"""
import json, os, urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape

USER = "AHILL-0121"
BG, LINE, GREEN, DIM, TEXT, MUTED = "#080C0B", "#1E2925", "#3DD68F", "#1C8A57", "#E0E6E3", "#8FA39A"
MONO = "'IBM Plex Mono','JetBrains Mono',Consolas,'Courier New',monospace"
TOKEN = os.environ.get("GITHUB_TOKEN")


def api(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    return json.load(urllib.request.urlopen(req, timeout=30))


def t(x, y, s, size=14, fill=TEXT, extra=""):
    return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" {extra}>{s}</text>'


user = api(f"https://api.github.com/users/{USER}")
repos = [r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
live = sum(1 for r in repos if r.get("homepage"))
langs = Counter(r["language"] for r in repos if r["language"])
top = langs.most_common(6)
last = max(repos, key=lambda r: r["pushed_at"])
since = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
days = (datetime.now(timezone.utc) - since).days

contrib = None
if TOKEN:
    q = {"query": 'query{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions}}}}' % USER}
    try:
        contrib = api("https://api.github.com/graphql", q)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception:
        pass

tiles = [("repos", len(repos)), ("shipped live", live) if live >= stars else ("stars", stars), ("followers", user["followers"]),
         ("commits / yr" if contrib is not None else "days online", contrib if contrib is not None else days)]

W, H = 1000, 250
css = [".n{opacity:0;animation:up .6s ease forwards}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}",
       ".bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.2,.8,.2,1) forwards}@keyframes grow{to{transform:scaleX(1)}}",
       ".cur{animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}",
       "@media (prefers-reduced-motion:reduce){*{animation:none!important}.n{opacity:1}.bar{transform:none}}"]
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub telemetry for {USER}">',
     "<style>" + "".join(css) + "</style>",
     f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>',
     t(24, 32, f'$ <tspan fill="{TEXT}">./telemetry --user {USER}</tspan>', 13, DIM),
     t(W - 24, 32, f'<tspan class="cur" fill="{GREEN}">●</tspan> synced {datetime.now(timezone.utc):%Y-%m-%d}', 11, DIM, 'text-anchor="end"'),
     f'<line x1="24" y1="46" x2="{W - 24}" y2="46" stroke="{LINE}"/>']

# number tiles, left half
for k, (label, val) in enumerate(tiles):
    x, y = 24 + (k % 2) * 230, 96 + (k // 2) * 78
    p.append(f'<g class="n" style="animation-delay:{0.15 * k:.2f}s">{t(x, y, f"{val:,}", 34, GREEN, "font-weight=\"700\"")}{t(x, y + 22, escape(label.upper()), 11, DIM, "letter-spacing=\"2\"")}</g>')
p.append(t(24, H - 20, f'last push → <tspan fill="{GREEN}">{escape(last["name"])}</tspan>', 12, MUTED))

# language bars, right half
lx, bw = 520, 330
p.append(t(lx, 76, "LANGUAGES BY REPO", 11, DIM, 'letter-spacing="2"'))
peak = top[0][1] if top else 1
for k, (lang, n) in enumerate(top):
    y = 100 + k * 23
    w = max(6, bw * n / peak)
    p.append(t(lx, y + 9, escape(lang.lower()), 12, TEXT))
    p.append(f'<rect x="{lx + 110}" y="{y}" width="{bw}" height="10" rx="2" fill="{LINE}"/>')
    p.append(f'<rect class="bar" style="animation-delay:{0.3 + 0.12 * k:.2f}s" x="{lx + 110}" y="{y}" width="{w:.1f}" height="10" rx="2" fill="{GREEN}" fill-opacity="{1 - k * 0.12:.2f}"/>')
    p.append(t(W - 24, y + 9, str(n), 12, MUTED, 'text-anchor="end"'))
p.append("</svg>")

with open("assets/stats.svg", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(p) + "\n")
print("stats:", tiles, top)
