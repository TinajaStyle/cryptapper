#!/usr/bin/env python3
import argparse
import sys

from cryptapper_core import (
    collect_coin_stats,
    list_scanned_ranges,
    load_report_rows,
    parse_range,
    save_scan,
)
from cryptapper_html import build_html


def main():
    parser = argparse.ArgumentParser(
        description="Scan crypto stats into SQLite or generate an HTML report."
    )
    parser.add_argument("range", help="Range like 1-50")
    parser.add_argument(
        "--db",
        default="cryptapper.db",
        help="SQLite database path (default: cryptapper.db)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML report from stored database data",
    )
    parser.add_argument(
        "--scanned-ranges",
        action="store_true",
        help="Print scanned ranges stored in the database and exit",
    )
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

    if args.scanned_ranges:
        ranges = list_scanned_ranges(args.db)
        if not ranges:
            print("No scanned ranges found.")
            return 0
        for start_rank, end_rank, created_at, run_id in ranges:
            print(f"{start_rank}-{end_rank} (run {run_id}, {created_at})")
        return 0

    try:
        start, end = parse_range(args.range)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.report:
        rows, _covering = load_report_rows(args.db, start, end)
        if not rows:
            print("Error: requested range not available in database.", file=sys.stderr)
            ranges = list_scanned_ranges(args.db)
            if ranges:
                print("Scanned ranges:", file=sys.stderr)
                for start_rank, end_rank, created_at, run_id in ranges:
                    print(
                        f"- {start_rank}-{end_rank} (run {run_id}, {created_at})",
                        file=sys.stderr,
                    )
            return 1

        out_path = args.out or f"cryptapper_{start}-{end}.html"
        html = build_html(rows, start, end)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {out_path}")
        return 0

    try:
        rows = collect_coin_stats(start, end, pause=args.pause)
    except Exception as exc:
        print(f"Error fetching data: {exc}", file=sys.stderr)
        return 1

    save_scan(args.db, start, end, rows)
    print(f"Saved {start}-{end} to {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
