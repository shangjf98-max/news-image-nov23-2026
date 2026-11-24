[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/shangjf98-max/news-image-nov23-2026/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/shangjf98-max/news-image-nov23-2026/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# News Image — 23 November 2026

Entry for the [make.fun](https://make.fun) bounty
[news-image-20261123](https://make.fun/bounty/news-image-20261123):
"Sum up 23 November's world news in one image."

`main.py` (Python 3.13 standard library only, no fonts, no image files, no
network) draws a deterministic 1024×1024 PNG of 23 November 2026 in one
image: 36 stories across 6 regions and 12 fields — 3 illustrated lead
stories, 12 illustrated cards, 21 one-line briefs, a UTC timeline, a
numbers strip, a dotted world map with numbered pins, a DATE CHECK box of
older news left out, and a confidence legend on every story.

Run it twice and the bytes are identical:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out/entry.png out2/entry.png   # identical
```

The top stories of the day: Nvidia reinstates Jensen Huang as CEO
(shares +31%, +$952bn, the largest one-day gain ever), Zelensky confirms
Ukrainian sea drones sank the Russian corvette Merkury off Libya, and the
EU proposes its 22nd Russia sanctions package.
