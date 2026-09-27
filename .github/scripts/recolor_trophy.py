"""Recolors the light-theme trophy SVG to the Matrix palette (run after the trophy action)."""
import re

PATH = "assets/trophy.svg"
MAP = {  # light theme -> matrix
    "#FFF": "#080C0B", "#fff": "#080C0B", "#e1e4e8": "#1E2925", "#0366d6": "#3DD68F",
    "#333": "#E0E6E3", "#666": "#1C8A57", "#777": "#8FA39A", "#000": "#E0E6E3",
}
svg = open(PATH, encoding="utf-8").read()
svg = re.sub(r'(?<=")(#[0-9A-Fa-f]{3,6})(?=")', lambda m: MAP.get(m.group(1), m.group(1)), svg)
open(PATH, "w", encoding="utf-8", newline="\n").write(svg)
print("trophy recolored")
