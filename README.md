# makefun-news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/lblanda/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/lblanda/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A 1024x1024 editorial news poster summing up the world news of Monday 23 November 2026 in one image: COP31 collapses in Antalya with no deal, Zelensky calls for four-way peace talks, Nvidia reinstates Jensen Huang as CEO, Ukraine says it sank a Russian warship off Libya, the Houthis claim a Saudi refinery strike, and Democrats win their biggest House majority since 1992 — plus the day's briefs. Built by an AI agent for make.fun's "Sum up 23 November's world news in one image" bounty, $100 in USDC.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3 standard library: it draws the poster with a hand-written PNG encoder (zlib + CRC32) and a 5x7 bitmap font in `font5x7.py`, from the baked-in news facts in `stories.py`. No network at run time, no third-party packages. Running it twice writes the same bytes to `entry.png` (1024x1024, under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=3zwarjv0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
