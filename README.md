# ekantipur-scraper

A Playwright-based scraper for [ekantipur.com](https://ekantipur.com) that collects entertainment articles and the cartoon of the day, then writes the results to `output.json`.

## What it scrapes

### Entertainment (मनोरञ्जन)

- Dismisses the homepage paywall modal (`#pagegate`) when present
- Opens the entertainment section via the bottom nav link **मनोरञ्जन**
- Extracts the **top 5** article cards from `.category-wrapper > .category`
- Fields per article: `title`, `image_url`, `category`, `author`

### Cartoon of the day

- Returns to the homepage after scraping entertainment
- Finds `section.e-section` containing **कार्टुन** and follows that link
- Extracts the first `.cartoon-wrapper` on the cartoon page
- Fields: `title`, `image_url`, `author` (falls back to the string `"null"` if no author element is found)

## Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) (recommended) or another way to install dependencies
- Playwright browsers (Chromium)

## Setup

```bash
# Install dependencies
uv sync

# Install Playwright browser binaries
uv run playwright install chromium
```

## Usage

```bash
uv run python scraper.py
```

The script launches Chromium with a visible browser window (`headless=False`), scrapes both sections, and writes `output.json` in the project root. Nepali text is preserved in the JSON file (`ensure_ascii=False`).

## Output format

```json
{
  "entertainment": [
    {
      "title": "...",
      "image_url": "...",
      "category": "मनोरञ्जन",
      "author": "..."
    }
  ],
  "cartoon_of_the_day": {
    "title": "...",
    "image_url": "...",
    "author": "..."
  }
}
```

## Configuration

| Constant | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `https://ekantipur.com` | Site entry point |
| `OUTPUT_PATH` | `output.json` | Output file path |
| `ENTERTAINMENT_ARTICLE_LIMIT` | `5` | Max entertainment articles to scrape |

## Project structure

```
ekantipur-scraper/
├── scraper.py      # Main scraper script
├── output.json     # Generated output (not committed by default)
├── pyproject.toml
└── README.md
```

## Notes

- The site may show a modal on first visit; the scraper clicks **Skip** when `#pagegate` is visible.
- Image URLs may use `src` or `data-src` for lazy-loaded images.
- Scraping third-party sites may be subject to their terms of service; use responsibly.
