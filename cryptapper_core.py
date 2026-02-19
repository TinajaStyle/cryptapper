import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlparse

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


def _warn(message):
    print(f"Warning: {message}", file=sys.stderr)


def parse_range(rng):
    if "-" not in rng:
        raise ValueError("Range must be in the form START-END, e.g. 1-50")
    start_s, end_s = rng.split("-", 1)
    start = int(start_s)
    end = int(end_s)
    if start < 1 or end < 1 or end < start:
        raise ValueError("Range must be positive and START <= END")
    return start, end


def fetch_market_page(page, per_page):
    url = (
        f"{BASE_URL}/coins/markets?vs_currency=usd"
        f"&order=market_cap_desc&per_page={per_page}&page={page}"
        f"&sparkline=false"
    )
    return _http_get_json(url)


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


def is_stablecoin(details):
    categories = details.get("categories") or []
    for category in categories:
        if "stable" in str(category).lower():
            return True
    return False


def _repo_from_url(url):
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    return f"{parts[0]}/{parts[1]}"


def fetch_github_languages(repo, retries=2, pause=0.5):
    if not repo:
        return []
    url = f"https://api.github.com/repos/{repo}/languages"
    try:
        data = _http_get_json(url, retries=retries, backoff=1.0)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            _warn(f"GitHub repo not found: {repo}")
            return None
        _warn(f"GitHub languages failed for {repo}: {exc}")
        return []
    except Exception as exc:
        _warn(f"GitHub languages failed for {repo}: {exc}")
        return []
    time.sleep(pause)
    if not isinstance(data, dict):
        return []
    ordered = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    return [name for name, _ in ordered]


def fetch_github_repo_info(repo, retries=2, pause=0.5):
    if not repo:
        return None
    url = f"https://api.github.com/repos/{repo}"
    try:
        data = _http_get_json(url, retries=retries, backoff=1.0)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            _warn(f"GitHub repo not found: {repo}")
            return None
        _warn(f"GitHub repo info failed for {repo}: {exc}")
        return None
    except Exception as exc:
        _warn(f"GitHub repo info failed for {repo}: {exc}")
        return None
    time.sleep(pause)
    if not isinstance(data, dict):
        return None
    return {
        "full_name": data.get("full_name"),
        "html_url": data.get("html_url"),
        "stars": data.get("stargazers_count"),
    }


def fetch_top_repo_for_user(user, retries=2, pause=0.5):
    if not user:
        return None, None
    query = urllib.parse.quote(f"user:{user}")
    url = (
        f"https://api.github.com/search/repositories?q={query}"
        f"&sort=stars&order=desc&per_page=1"
    )
    try:
        data = _http_get_json(url, retries=retries, backoff=1.0)
    except Exception as exc:
        _warn(f"GitHub repo search failed for {user}: {exc}")
        return None, None
    time.sleep(pause)
    items = data.get("items") if isinstance(data, dict) else None
    if not items:
        return None, None
    item = items[0] or {}
    return item.get("full_name"), item.get("html_url")


def resolve_github_languages(github_url, lang_cache, user_cache, repo_cache):
    if not github_url:
        return [], github_url, None
    parsed = urlparse(github_url)
    if parsed.netloc.lower() != "github.com":
        return [], github_url, None
    parts = [p for p in parsed.path.split("/") if p]
    if not parts:
        return [], github_url, None

    owner = parts[0]
    repo = parts[1] if len(parts) >= 2 else None

    def _fallback_to_user(user):
        if user in user_cache:
            top_repo, top_url = user_cache[user]
        else:
            top_repo, top_url = fetch_top_repo_for_user(user)
            user_cache[user] = (top_repo, top_url)
        if not top_repo:
            return [], github_url, None
        if top_repo in lang_cache:
            languages = lang_cache[top_repo]
        else:
            languages = fetch_github_languages(top_repo) or []
            lang_cache[top_repo] = languages
        if top_repo in repo_cache:
            info = repo_cache[top_repo]
        else:
            info = fetch_github_repo_info(top_repo)
            repo_cache[top_repo] = info
        resolved_url = (info or {}).get("html_url") or top_url or f"https://github.com/{top_repo}"
        stars = (info or {}).get("stars")
        return languages, resolved_url, stars

    if not repo:
        return _fallback_to_user(owner)

    full_repo = f"{owner}/{repo}"
    if full_repo in lang_cache:
        languages = lang_cache[full_repo]
    else:
        languages = fetch_github_languages(full_repo)
    if languages is None:
        return _fallback_to_user(owner)
    lang_cache[full_repo] = languages
    if full_repo in repo_cache:
        info = repo_cache[full_repo]
    else:
        info = fetch_github_repo_info(full_repo)
        repo_cache[full_repo] = info
    stars = (info or {}).get("stars")
    return languages, github_url, stars


def collect_coin_stats(start, end, pause=1.0, per_page=250):
    rows = []
    lang_cache = {}
    user_cache = {}
    repo_cache = {}
    start_page = (start - 1) // per_page + 1
    end_page = (end - 1) // per_page + 1
    offset_start = (start - 1) % per_page
    offset_end = (end - 1) % per_page

    for page in range(start_page, end_page + 1):
        try:
            markets = fetch_market_page(page, per_page)
        except Exception as exc:
            _warn(f"market page {page} failed: {exc}")
            continue
        if not markets:
            break

        page_start = offset_start if page == start_page else 0
        page_end = offset_end if page == end_page else len(markets) - 1
        page_slice = markets[page_start : page_end + 1]

        for item in page_slice:
            coin_id = item.get("id")
            try:
                details = fetch_coin_details(coin_id)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    _warn(f"coin details not found for {coin_id} (404)")
                    details = {}
                else:
                    _warn(f"coin details failed for {coin_id}: {exc}")
                    details = {}
            except Exception as exc:
                _warn(f"coin details failed for {coin_id}: {exc}")
                details = {}

            if is_stablecoin(details):
                time.sleep(pause)
                continue

            base = {
                "rank": item.get("market_cap_rank"),
                "name": item.get("name"),
                "symbol": item.get("symbol"),
                "market_cap": item.get("market_cap"),
            }
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

            languages, github_resolved, gh_stars = resolve_github_languages(
                github, lang_cache, user_cache, repo_cache
            )
            stars = gh_stars if gh_stars is not None else dev.get("stars")

            base.update(
                {
                    "dev_stars": stars,
                    "github_languages": languages,
                    "homepage": homepage,
                    "github": github_resolved,
                    "twitter": twitter,
                    "reddit": reddit,
                    "telegram": telegram,
                }
            )

            rows.append(base)
            time.sleep(pause)

    return rows
