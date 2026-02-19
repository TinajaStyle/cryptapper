# Repository Guidelines

## Project Structure & Module Organization

This repository is a small Python CLI that pulls CoinGecko data and renders an HTML report. Current layout:

- `cryptapper.py` — CLI entrypoint.
- `cryptapper_core.py` — API calls and data aggregation.
- `cryptapper_html.py` — HTML rendering.

If the project grows, keep code under `src/` and tests under `tests/`.

## Build, Test, and Development Commands

Key commands:

- `python3 cryptapper.py 1-50` — fetch top 50 by market cap and write `cryptapper_1-50.html`.
- `python3 cryptapper.py 1-50 --out report.html` — write to a custom filename.
- `python3 cryptapper.py 1-50 --pause 1.5` — slow down detail requests to reduce rate-limit risk.

## Coding Style & Naming Conventions

Follow standard Python style:

- 4 spaces for indentation.
- `snake_case` for functions/variables, `PascalCase` for classes.
- Keep helpers in `cryptapper_core.py` and HTML concerns in `cryptapper_html.py`.

## Testing Guidelines

No testing framework is configured yet. If tests are added, use `pytest` and place files under `tests/` with names like `test_*.py`.

## Commit & Pull Request Guidelines

There is no commit history to infer conventions from. Until a convention is defined, use clear, imperative messages such as:

- `Add user onboarding flow`
- `Fix token refresh edge case`

For pull requests, include a concise summary, linked issues (if any), and an example HTML output file or screenshot if you change rendering.

## Configuration & Secrets

The script uses public CoinGecko endpoints and does not require API keys, but optional tokens improve rate limits:

- `GITHUB_TOKEN` — GitHub API authentication.
- `COINGECKO_API_KEY` — CoinGecko API key.
- `COINGECKO_API_KEY_HEADER` — header name (default: `x-cg-demo-api-key`; set `x-cg-pro-api-key` for Pro).

Never commit secrets.

## GitHub Push Checklist

- Ensure `README.md` and `AGENTS.md` are up to date.
- Run a quick smoke test: `python3 cryptapper.py 1-5 --out /tmp/cryptapper_test.html`.
- Commit with a clear message, then push:
  - `git status`
  - `git add -A`
  - `git commit -m "Update cryptapper report generation"`
  - `git push`
