#!/usr/bin/env python3
"""Generate explicitly labeled, backdated contribution art for 2025."""
import datetime as dt
import json
import os
from pathlib import Path
import random
import subprocess

ROOT = Path(__file__).resolve().parent
SPRITES = [
    ['00100000100', '00010001000', '00111111100', '01101110110', '11111111111', '10100000101', '00011011000'],
    ['00001110000', '00111111100', '01111111110', '11011011011', '11111111111', '00100100100', '01011011010'],
    ['00011111000', '01111111110', '11111111111', '11100100111', '11111111111', '00011011000', '00100100100'],
]

def git(*args, **kwargs):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], **kwargs).decode().strip()

if (ROOT / '.git').exists():
    raise SystemExit('Refusing to regenerate an existing repository. Use a fresh copy.')
random.SystemRandom().shuffle(SPRITES)
start = dt.date(2024, 12, 29)  # Sunday before the first day of 2025.
pixels = {}
for x0, sprite in zip([4, 21, 38], SPRITES):
    for y, row in enumerate(sprite):
        for x, cell in enumerate(row):
            if cell == '1':
                date = start + dt.timedelta(days=(x0 + x) * 7 + y)
                assert date.year == 2025
                pixels[date.isoformat()] = 4
# Small stars between the three invaders.
for x, y in [(17, 1), (17, 5), (34, 2), (34, 5)]:
    date = start + dt.timedelta(days=x * 7 + y)
    pixels[date.isoformat()] = 1
pixels = dict(sorted(pixels.items()))
(ROOT / 'art.json').write_text(json.dumps({'year': 2025, 'name': 'Space Invaders', 'commits_per_date': pixels}, indent=2) + '\n')
colors = {0: '#161b22', 1: '#0e4429', 4: '#39d353'}
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="810" height="155" viewBox="0 0 810 155">', '<rect width="810" height="155" rx="12" fill="#0d1117"/>', '<text x="18" y="25" fill="#e6edf3" font-family="monospace" font-size="14">2025 / SPACE INVADERS</text>']
for x in range(53):
    for y in range(7):
        date = start + dt.timedelta(days=x * 7 + y)
        if date.year != 2025:
            continue
        svg.append(f'<rect x="{18+x*14}" y="{38+y*14}" width="11" height="11" rx="2" fill="{colors[pixels.get(date.isoformat(), 0)]}"/>')
svg.append('</svg>')
(ROOT / 'preview.svg').write_text('\n'.join(svg) + '\n')
(ROOT / 'README.md').write_text('''# 2025 contribution art: Space Invaders

![Space Invaders contribution art](preview.svg)

Intentional pixel art for [davlabs-us’s 2025 contribution graph](https://github.com/davlabs-us?tab=overview&from=2025-01-01&to=2025-12-31).

These commits are decorative, backdated art pixels, not a record of software work performed in 2025. Author and committer timestamps are set to noon UTC on each painted day. The art lives on the default `main` branch in this standalone repository.

`art.json` records the exact dates and counts. `generate.py` creates a fresh repository with a randomized arrangement of three retro alien sprites. To recreate it, copy the generator into an empty directory and run `python3 generate.py`. Do not push another copy to the same account, because its contributions would add to this one.

To remove this artwork from the contribution graph, delete this dedicated repository on GitHub; GitHub may take time to recalculate the graph.
''')
git('init', '-b', 'main')
git('config', 'user.name', 'davlabs-us')
git('config', 'user.email', '20848773+davlabs-us@users.noreply.github.com')
git('add', 'README.md', 'generate.py', 'art.json', 'preview.svg')
tree = git('write-tree')
parent = None
for date, count in pixels.items():
    for i in range(count):
        env = dict(os.environ, GIT_AUTHOR_DATE=f'{date}T12:00:00+00:00', GIT_COMMITTER_DATE=f'{date}T12:00:00+00:00')
        args = ['commit-tree', tree]
        if parent:
            args += ['-p', parent]
        parent = git(*args, input=f'Contribution art: Space Invaders pixel {date} ({i+1}/{count})\n'.encode(), env=env)
git('update-ref', 'refs/heads/main', parent)
git('reset', '--hard', 'main')
# Verify every commit maps exactly to the requested year, pixel date, and count.
from collections import Counter
actual = Counter(line.replace('Z', '+00:00') for line in git('log', '--format=%aI').splitlines())
assert actual == Counter({f'{date}T12:00:00+00:00': count for date, count in pixels.items()})
assert git('status', '--porcelain') == ''
print(f'Validated {sum(pixels.values())} commits across {len(pixels)} painted days.')
for y in range(7):
    print(''.join('██' if pixels.get((start + dt.timedelta(days=x*7+y)).isoformat(), 0) else '  ' for x in range(53)))
