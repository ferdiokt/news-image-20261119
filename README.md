# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/ferdiokt/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/ferdiokt/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One 1024x1024 image that sums up the world's news of Thursday 19 November 2026: 33 stories from 6 regions, 3 leads, 12 numbered cards on a map, briefs by city, a timeline of local times and a date-check box of stories left out. Every story carries a REPORTED / CLAIM / FORECAST tag; links for each are in SOURCES.md.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=576mav8k&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>

## How it is made

- `stories.py` is the story ledger: tag, local time, fact and at least two source URLs per story.
- `render.py` draws `entry.png` from the ledger with Pillow (every word, icon and map shape is drawn in code) and writes `SOURCES.md`.
- `main.py` (Python 3.13, standard library) checks the committed PNG and copies it to `/output/entry.png`, so both runs write the same bytes.
