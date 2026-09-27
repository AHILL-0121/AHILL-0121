"""Renders the live 'signal' panels from GitHub data (run daily by .github/workflows/matrix-stats.yml).

  assets/signal-contrib.svg   contribution heatmap + streaks (public contributions calendar, no token needed)
  assets/signal-repos.svg     repos / shipped / followers / days on GitHub
  assets/signal-langs.svg     languages by repository
"""
import json, os, re, sys, urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matrix import C, HEAT, W, micro, save, svg, t, tile  # noqa: E402

USER = "AHILL-0121"
TOKEN = os.environ.get("GITHUB_TOKEN")
GAP = 8
TODAY = datetime.now(timezone.utc)


def get(url, as_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    raw = urllib.request.urlopen(req, timeout=30).read().decode()
    return json.loads(raw) if as_json else raw


# ----------------------------------------------------------------------------- contributions
def contributions():
    html = get(f"https://github.com/users/{USER}/contributions", as_json=False)
    days = {}
    for cell in re.finditer(r'data-date="(\d{4}-\d\d-\d\d)" id="(contribution-day-component-[\d-]+)" data-level="(\d)"', html):
        d, cid, lvl = cell.groups()
        m = re.search(r'for="%s"[^>]*>([^<]*)' % re.escape(cid), html)
        n = 0
        if m and not m.group(1).startswith("No"):
            n = int(re.match(r"(\d+)", m.group(1).replace(",", "")).group(1))
        days[date.fromisoformat(d)] = (n, int(lvl))
    return dict(sorted(days.items()))


def streaks(days):
    cur = best = run = 0
    for d, (n, _) in days.items():
        run = run + 1 if n else 0
        best = max(best, run)
    # current streak may continue through today with no commit yet
    ordered = list(days.items())
    i = len(ordered) - 1
    if ordered and ordered[i][1][0] == 0:
        i -= 1
    while i >= 0 and ordered[i][1][0] > 0:
        cur += 1
        i -= 1
    return cur, best


def contrib_panel(days):
    total = sum(n for n, _ in days.values())
    cur, best = streaks(days)
    top_day, (top_n, _) = max(days.items(), key=lambda kv: kv[1][0])
    active = sum(1 for n, _ in days.values() if n)

    H = 318
    cell, gap = 11, 3
    step = cell + gap
    first = min(days)
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # sunday column start
    weeks = ((max(days) - start).days // 7) + 1
    gx = W - 28 - weeks * step + gap
    gy = 188

    b = tile(W, H, uid="c")
    b += [micro(28, 42, "contributions · last 12 months"),
          micro(W - 28, 42, f"synced {TODAY:%d %b %Y}", anchor="end"),
          f'<line x1="28" y1="60" x2="{W - 28}" y2="60" stroke="{C["line"]}"/>']
    stats = [(f"{total:,}", "contributions"), (f"{cur}", "current streak"), (f"{best}", "longest streak"), (f"{active}", "active days")]
    for k, (val, lab) in enumerate(stats):
        x = 28 + k * 200
        b.append(f'<g class="fx up" style="animation-delay:{k * 0.1:.1f}s">'
                 + t(x, 110, val, 32, C["green"] if k == 1 else C["text"], 700)
                 + t(x + len(val) * 19.2 + 8, 110, "days" if k in (1, 2) else "", 12, C["muted"])
                 + micro(x, 134, lab) + "</g>")

    # month labels
    seen = set()
    for wk in range(weeks):
        d = start + timedelta(days=wk * 7)
        if d.day <= 7 and d.month not in seen and wk < weeks - 1:
            seen.add(d.month)
            b.append(t(gx + wk * step, gy - 10, d.strftime("%b").lower(), 10, C["muted"]))
    for r, lab in ((1, "mon"), (3, "wed"), (5, "fri")):
        b.append(t(28, gy + r * step + 9, lab, 10, C["dim"]))

    cells = []
    for d, (n, lvl) in days.items():
        wk, dow = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = gx + wk * step, gy + dow * step
        cells.append(f'<rect class="fx cl" style="animation-delay:{wk * 0.018:.3f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lvl]}"/>')
    b += cells
    # scanning beam
    b += [f'<defs><linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{C["bright"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["bright"]}" stop-opacity=".35"/></linearGradient>'
          f'<clipPath id="gc"><rect x="{gx}" y="{gy}" width="{weeks * step}" height="{7 * step}"/></clipPath></defs>',
          f'<g clip-path="url(#gc)"><rect class="beam" x="{gx - 40}" y="{gy}" width="40" height="{7 * step}" fill="url(#beam)"/></g>']
    b.append(micro(28, H - 22, f"best day · {top_n} on {top_day:%d %b}"))
    legend_x = W - 28 - 5 * 14 - 34
    b.append(t(legend_x - 8, H - 22, "less", 10, C["muted"], anchor="end"))
    for k, col in enumerate(HEAT):
        b.append(f'<rect x="{legend_x + k * 14}" y="{H - 32}" width="{cell}" height="{cell}" rx="2.5" fill="{col}"/>')
    b.append(t(legend_x + 5 * 14 + 4, H - 22, "more", 10, C["muted"]))

    css = (".cl{opacity:0;animation:cl .4s ease forwards}@keyframes cl{to{opacity:1}}"
           ".up{opacity:0;animation:up .6s ease forwards}@keyframes up{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
           f".beam{{animation:beam 7s cubic-bezier(.5,0,.5,1) 1.2s infinite}}@keyframes beam{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({weeks * step + 40}px)}}}}")
    save("signal-contrib.svg", svg(W, H, b, f"{total} contributions in the last year; current streak {cur} days, longest {best} days.", css, (400, 500, 700)))
    return total, cur, best


# ----------------------------------------------------------------------------- repos + languages
def repo_panels():
    user = get(f"https://api.github.com/users/{USER}")
    repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    live = sum(1 for r in repos if r.get("homepage"))
    stars = sum(r["stargazers_count"] for r in repos)
    since = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    last = max(repos, key=lambda r: r["pushed_at"])
    cw = (W - GAP) // 2
    H = 210

    tiles = [(len(repos), "repositories"), (live, "shipped live"), (user["followers"], "followers"), ((TODAY - since).days, "days on github")]
    if stars > live:
        tiles[1] = (stars, "stars")
    b = tile(cw, H, uid="p")
    b += [micro(26, 42, "telemetry"), f'<line x1="26" y1="60" x2="{cw - 26}" y2="60" stroke="{C["line"]}"/>']
    for k, (val, lab) in enumerate(tiles):
        x, y = 26 + (k % 2) * 190, 104 + (k // 2) * 62
        b.append(f'<g class="fx up" style="animation-delay:{k * 0.1:.1f}s">{t(x, y, f"{val:,}", 28, C["green"] if k == 1 else C["text"], 700)}{micro(x, y + 20, lab)}</g>')
    b.append(t(cw - 26, 42, f"last push · {last['name'].lower()}", 11, C["muted"], anchor="end"))
    css = ".up{opacity:0;animation:up .6s ease forwards}@keyframes up{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
    save("signal-repos.svg", svg(cw, H, b, f"{len(repos)} repositories, {live} shipped live, {user['followers']} followers.", css, (400, 500, 700)))

    langs = Counter(r["language"] for r in repos if r["language"]).most_common(5)
    total = sum(n for _, n in langs) or 1
    b = tile(cw, H, uid="l")
    b += [micro(26, 42, "languages · by repo"), micro(cw - 26, 42, f"{len(repos)} repos", anchor="end"),
          f'<line x1="26" y1="60" x2="{cw - 26}" y2="60" stroke="{C["line"]}"/>']
    bx, bw = 150, cw - 26 - 150 - 44
    for k, (lang, n) in enumerate(langs):
        y = 90 + k * 24
        b += [t(26, y + 4, lang.lower().replace("jupyter notebook", "jupyter"), 12.5, C["text"]),
              f'<rect x="{bx}" y="{y - 5}" width="{bw}" height="8" rx="4" fill="{C["bg0"]}" stroke="{C["line"]}"/>',
              f'<rect class="fx bar" style="animation-delay:{0.2 + k * 0.12:.2f}s" x="{bx}" y="{y - 5}" width="{max(8, bw * n / langs[0][1]):.1f}" height="8" rx="4" fill="{C["green"]}" fill-opacity="{1 - k * 0.15:.2f}"/>',
              t(cw - 26, y + 4, f"{n / total * 100:.0f}%", 11.5, C["muted"], anchor="end")]
    css = ".bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar 1.1s cubic-bezier(.2,.8,.2,1) forwards}@keyframes bar{to{transform:scaleX(1)}}"
    save("signal-langs.svg", svg(cw, H, b, "Languages: " + ", ".join(f"{l} {n}" for l, n in langs), css, (400, 500)))
    return len(repos), live


if __name__ == "__main__":
    print("contrib", contrib_panel(contributions()))
    print("repos", repo_panels())
