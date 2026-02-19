# Cryptapper

Small Python CLI that pulls CoinGecko market-cap data, enriches it with developer/community links, and generates an HTML report.

## Requirements

- Python 3.8+

## Usage

```bash
python3 cryptapper.py 1-50
```

Output: `cryptapper_1-50.html`

Options:

```bash
python3 cryptapper.py 1-50 --out report.html
python3 cryptapper.py 20-60 --pause 1.5
```

Notes:

- Stablecoins are skipped within the requested market-cap slice.
- GitHub languages are inferred from the first GitHub repo link or a fallback repo.
- This project is not fully tested.

## API Tokens (Optional)

Set environment variables for higher rate limits:

```bash
export GITHUB_TOKEN=...
export COINGECKO_API_KEY=...
# Optional if you have a Pro key:
export COINGECKO_API_KEY_HEADER=x-cg-pro-api-key
```

## Output Columns

- Rank, Name, Symbol, Market Cap (USD)
- Homepage, GitHub, GitHub Stars, Languages
- Twitter, Reddit, Telegram

## Project Layout

- `cryptapper.py` — CLI entrypoint.
- `cryptapper_core.py` — API calls and data aggregation.
- `cryptapper_html.py` — HTML rendering.
