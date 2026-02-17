import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.coingecko.com/api/v3"
USER_AGENT = "cryptapper/0.1 (+https://example.local)"


class ApiError(RuntimeError):
    pass


def _http_get_json(url, retries=3, backoff=1.0):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_err = exc
            status = getattr(exc, "code", None)
            if status in (429, 500, 502, 503, 504) and attempt < retries - 1:
                retry_after = exc.headers.get("Retry-After")
                sleep_for = float(retry_after) if retry_after else backoff * (attempt + 1)
                time.sleep(sleep_for)
                continue
            raise
        except Exception as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
                continue
            raise
    raise ApiError(f"Request failed: {last_err}")


def parse_range(rng):
    if "-" not in rng:
        raise ValueError("Range must be in the form START-END, e.g. 1-50")
    start_s, end_s = rng.split("-", 1)
    start = int(start_s)
    end = int(end_s)
    if start < 1 or end < 1 or end < start:
        raise ValueError("Range must be positive and START <= END")
    return start, end


def fetch_markets(start, end):
    per_page = 250
    start_page = (start - 1) // per_page + 1
    end_page = (end - 1) // per_page + 1
    markets = []
    for page in range(start_page, end_page + 1):
        url = (
            f"{BASE_URL}/coins/markets?vs_currency=usd"
            f"&order=market_cap_desc&per_page={per_page}&page={page}"
            f"&sparkline=false"
        )
        markets.extend(_http_get_json(url))
        time.sleep(0.3)
    markets.sort(key=lambda x: x.get("market_cap_rank") or 10**9)
    return markets[start - 1 : end]


def fetch_coin_details(coin_id):
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "false",
        "community_data": "false",
        "developer_data": "true",
        "sparkline": "false",
    }
    qs = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/coins/{coin_id}?{qs}"
    return _http_get_json(url)


def collect_coin_stats(start, end, pause=1.0):
    markets = fetch_markets(start, end)
    rows = []
    for item in markets:
        coin_id = item.get("id")
        base = {
            "rank": item.get("market_cap_rank"),
            "name": item.get("name"),
            "symbol": item.get("symbol"),
            "market_cap": item.get("market_cap"),
        }
        try:
            details = fetch_coin_details(coin_id)
        except Exception:
            details = {}

        dev = details.get("developer_data") or {}
        links = details.get("links") or {}
        repos = links.get("repos_url") or {}

        def _first(items):
            for item in items or []:
                if item:
                    return item
            return None

        homepage = _first(links.get("homepage"))
        github = _first(repos.get("github"))
        twitter_handle = links.get("twitter_screen_name")
        twitter = f"https://twitter.com/{twitter_handle}" if twitter_handle else None
        reddit = links.get("subreddit_url")
        telegram_id = links.get("telegram_channel_identifier")
        if telegram_id:
            telegram = f"https://t.me/{telegram_id}"
        else:
            telegram = _first(links.get("chat_url"))

        base.update(
            {
                "dev_stars": dev.get("stars"),
                "homepage": homepage,
                "github": github,
                "twitter": twitter,
                "reddit": reddit,
                "telegram": telegram,
            }
        )

        rows.append(base)
        time.sleep(pause)

    return rows
