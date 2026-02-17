#!/usr/bin/env python3
import argparse
import sys

from cryptapper_core import collect_coin_stats, parse_range
from cryptapper_html import build_html


def main():
    parser = argparse.ArgumentParser(
        description="Generate an HTML report of dev/community stats for cryptocurrencies."
    )
    parser.add_argument("range", help="Range like 1-50")
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML file (default: cryptapper_START-END.html)",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=1.0,
        help="Seconds to pause between coin detail requests (default: 1.0)",
    )
    args = parser.parse_args()

    try:
        start, end = parse_range(args.range)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        rows = collect_coin_stats(start, end, pause=args.pause)
    except Exception as exc:
        print(f"Error fetching data: {exc}", file=sys.stderr)
        return 1

    out_path = args.out or f"cryptapper_{start}-{end}.html"
    html = build_html(rows, start, end)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
