#!/usr/bin/env python3
"""
Matrix rain - pure transparent, no HUD, more density & themes
"""

import os
import sys
import time
import random
import shutil
import signal
import platform
import argparse
from collections import deque

# Platform-specific input
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    import msvcrt
else:
    import termios
    import tty
    import select

# ────────────────────────────────────────
# Themes (expanded)
# ────────────────────────────────────────

THEMES = {
    "matrix": {
        "head": "\033[38;2;0;255;0m",
        "bright": "\033[38;2;100;255;100m",
        "dim": "\033[38;2;0;180;0m",
        "trail": "\033[38;2;0;80;0m",
        "chars": "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ1234567890"
    },
    "blood": {
        "head": "\033[38;2;255;40;40m",
        "bright": "\033[38;2;255;100;100m",
        "dim": "\033[38;2;180;0;0m",
        "trail": "\033[38;2;90;0;0m",
        "chars": "血死殺傷痛哭叫吼怒怨恨怨嗚哇呀嘿咦呜哇啊啊啊啊"
    },
    "cyber": {
        "head": "\033[38;2;0;255;255m",
        "bright": "\033[38;2;100;255;255m",
        "dim": "\033[38;2;0;180;180m",
        "trail": "\033[38;2;0;90;90m",
        "chars": "01ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()"
    },
    "neon": {
        "head": "\033[38;2;255;0;255m",     # magenta
        "bright": "\033[38;2;255;100;255m",
        "dim": "\033[38;2;180;0;180m",
        "trail": "\033[38;2;90;0;90m",
        "chars": "ネオン輝く未来回路都市夜闇光"
    },
    "purple": {
        "head": "\033[38;2;200;0;255m",
        "bright": "\033[38;2;220;100;255m",
        "dim": "\033[38;2;140;0;180m",
        "trail": "\033[38;2;70;0;90m",
        "chars": "紫神秘夢幻魔女呪文闇夜月"
    },
    "gold": {
        "head": "\033[38;2;255;215;0m",
        "bright": "\033[38;2;255;235;100m",
        "dim": "\033[38;2;180;150;0m",
        "trail": "\033[38;2;120;90;0m",
        "chars": "GOLD RICH 财富金钱帝国王冠"
    },
    "ice": {
        "head": "\033[38;2;200;240;255m",
        "bright": "\033[38;2;220;255;255m",
        "dim": "\033[38;2;100;180;220m",
        "trail": "\033[38;2;50;100;140m",
        "chars": "❄️氷雪寒凍晶凍結北極光"
    },
    "void": {
        "head": "\033[38;2;40;40;60m",
        "bright": "\033[38;2;80;80;120m",
        "dim": "\033[38;2;20;20;40m",
        "trail": "\033[38;2;10;10;20m",
        "chars": " .•*⁎✧◦◦✦⁎*•. "
    }
}

DEFAULT_THEME = "matrix"

# ────────────────────────────────────────
# Terminal helpers
# ────────────────────────────────────────

def get_size():
    return shutil.get_terminal_size((80, 24))

def hide_cursor():
    print("\033[?25l", end="", flush=True)

def show_cursor():
    print("\033[?25h", end="", flush=True)

def alternate_screen(enable=True):
    print("\033[?1049h" if enable else "\033[?1049l", end="", flush=True)

def clear_screen():
    print("\033[2J\033[H", end="", flush=True)

# ────────────────────────────────────────
# Non-blocking key input
# ────────────────────────────────────────

if not IS_WINDOWS:
    old_settings = None
    def setup_term():
        global old_settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    def restore_term():
        if old_settings:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

    def get_key():
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None
else:
    def setup_term():
        pass

    def restore_term():
        pass

    def get_key():
        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8", errors="ignore")
        return None

# ────────────────────────────────────────
# Stream logic
# ────────────────────────────────────────

class Drop:
    def __init__(self, col, theme):
        self.col = col
        self.row = random.randint(-30, -5)
        self.length = random.randint(10, 35)
        self.speed = random.uniform(0.7, 1.8)
        self.chars = [random.choice(theme["chars"]) for _ in range(self.length)]
        self.age = 0

    def update(self):
        self.row += self.speed
        self.age += 1

    def is_dead(self, height):
        return self.row - self.length > height

    def draw(self, frame, theme):
        for i in range(self.length):
            r = int(self.row - i)
            if r < 0 or r >= len(frame):
                continue
            intensity = i / self.length
            if i == 0:
                color = theme["head"]
            elif i < 4:
                color = theme["bright"]
            elif intensity > 0.5:
                color = theme["dim"]
            else:
                color = theme["trail"]
            frame[r][self.col] = color + self.chars[i] + "\033[0m"

# ────────────────────────────────────────
# Main loop - pure transparent rain, no HUD
# ────────────────────────────────────────

def run(theme_name=DEFAULT_THEME, density=0.15, base_speed=1.0):
    theme = THEMES.get(theme_name.lower(), THEMES[DEFAULT_THEME])
    cols, rows = get_size()
    drops = []

    alternate_screen(True)
    hide_cursor()
    clear_screen()
    setup_term()

    paused = False

    try:
        while True:
            # Resize check
            new_cols, new_rows = get_size()
            if (new_cols, new_rows) != (cols, rows):
                cols, rows = new_cols, new_rows
                clear_screen()
                drops = [d for d in drops if d.col < cols]

            frame = [[" " for _ in range(cols)] for _ in range(rows)]

            # Spawn drops
            if not paused and random.random() < density:
                col = random.randint(0, cols - 1)
                drops.append(Drop(col, theme))

            # Update & draw
            new_drops = []
            for drop in drops:
                drop.update()
                if not drop.is_dead(rows):
                    drop.draw(frame, theme)
                    new_drops.append(drop)
            drops = new_drops

            # Build & print frame (no bg, no status)
            out = "".join("".join(row) + "\n" for row in frame)
            print("\033[H" + out, end="", flush=True)

            # Input handling
            key = get_key()
            if key:
                k = key.lower()
                if k in ("q", "\x03"):
                    break
                elif k == "p":
                    paused = not paused
                elif k in ("+", "="):
                    base_speed = min(5.0, base_speed + 0.25)
                elif k == "-":
                    base_speed = max(0.3, base_speed - 0.25)
                elif k == "d":
                    density = min(0.5, density + 0.01)
                elif k == "D":
                    density = max(0.05, density - 0.01)
                elif k == "t":
                    keys = list(THEMES.keys())
                    idx = (keys.index(theme_name.lower()) + 1) % len(keys)
                    theme_name = keys[idx]
                    theme = THEMES[theme_name]
                    clear_screen()  # refresh colors

            time.sleep(0.016 / base_speed)

    except KeyboardInterrupt:
        pass
    finally:
        restore_term()
        show_cursor()
        alternate_screen(False)
        clear_screen()
#        print("Matrix faded. Peace bro 🌌")

# ────────────────────────────────────────
# CLI
# ────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pure transparent Matrix rain")
    parser.add_argument("--theme", "-t", default=DEFAULT_THEME,
                        choices=list(THEMES.keys()), help="Theme name")
    parser.add_argument("--density", "-d", type=float, default=0.15,
                        help="Drop spawn chance")
    parser.add_argument("--speed", "-s", type=float, default=1.0,
                        help="Base fall speed")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, lambda s,f: sys.exit(0))
    if not IS_WINDOWS:
        signal.signal(signal.SIGWINCH, lambda s,f: None)

    run(args.theme, args.density, args.speed)
