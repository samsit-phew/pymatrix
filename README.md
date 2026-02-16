# Matrix Rain – Pure Python Terminal Edition

Deps-free, cross-platform, transparent Matrix-style digital rain for your terminal.  
No curses, no pip installs — just run it with stock Python 3.8+.

Better than classic `cmatrix`: more themes, live controls, smooth resize, no ugly HUD.

![matrix-rain-screenshot](https://via.placeholder.com/800x400/000000/00ff00?text=Matrix+Raining+in+Terminal)  
*(replace with your own screenshot later bro 🔥)*

## Features

- **Pure transparent rain** — only falling chars, no black background blocks
- **Live keyboard controls** while running:
  - `q` / Ctrl+C → quit
  - `p` → pause/resume
  - `+` / `-` → speed up/down
  - `d` / `D` → increase/decrease density
  - `t` → cycle themes
- **8 built-in themes** (more coming): matrix, blood, cyber, neon, purple, gold, ice, void
- Auto-resizes with your terminal window
- Works on **Linux, macOS, Windows** out of the box

## Quick Start

```bash
# Just clone and run (no dependencies!)
git clone https://github.com/samsit-phew/pymatrix.git
cd pymatrix
chmod +x pymatrix

./pymatrix
