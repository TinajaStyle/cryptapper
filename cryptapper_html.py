import html


def _fmt(value):
    if value is None or value == "":
        return "N/A"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return f"{value:,}"
    return str(value)


def build_html(rows, start, end):
    lines = []
    lines.append("<!doctype html>")
    lines.append("<html lang=\"en\">")
    lines.append("<head>")
    lines.append("  <meta charset=\"utf-8\" />")
    lines.append(f"  <title>Cryptapper {start}-{end}</title>")
    lines.append("  <style>")
    lines.append("    body { font-family: Arial, sans-serif; margin: 24px; }")
    lines.append("    h1 { margin-bottom: 8px; }")
    lines.append("    table { border-collapse: collapse; width: 100%; }")
    lines.append("    th, td { border: 1px solid #ddd; padding: 8px; }")
    lines.append("    th { background: #f5f5f5; text-align: left; }")
    lines.append("    tr:nth-child(even) { background: #fafafa; }")
    lines.append("    .num { text-align: right; font-variant-numeric: tabular-nums; }")
    lines.append("  </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append(f"  <h1>Top {start}-{end} Cryptocurrencies by Market Cap</h1>")
    lines.append("  <table>")
    lines.append("    <thead>")
    lines.append("      <tr>")
    lines.append("        <th>Rank</th>")
    lines.append("        <th>Name</th>")
    lines.append("        <th>Symbol</th>")
    lines.append("        <th class=\"num\">Market Cap (USD)</th>")
    lines.append("        <th class=\"num\">GitHub Stars</th>")
    lines.append("        <th class=\"num\">GitHub Forks</th>")
    lines.append("        <th class=\"num\">Issues (Open/Closed)</th>")
    lines.append("        <th class=\"num\">PRs Merged</th>")
    lines.append("        <th class=\"num\">Commits (4w)</th>")
    lines.append("        <th class=\"num\">Reddit Subs</th>")
    lines.append("        <th class=\"num\">Reddit Active 48h</th>")
    lines.append("        <th class=\"num\">Telegram Users</th>")
    lines.append("      </tr>")
    lines.append("    </thead>")
    lines.append("    <tbody>")

    for row in rows:
        issues = "N/A"
        open_issues = row.get("dev_open_issues")
        closed_issues = row.get("dev_closed_issues")
        if open_issues is not None or closed_issues is not None:
            issues = f"{_fmt(open_issues)}/{_fmt(closed_issues)}"

        lines.append("      <tr>")
        lines.append(f"        <td class=\"num\">{html.escape(_fmt(row.get('rank')))}</td>")
        lines.append(f"        <td>{html.escape(_fmt(row.get('name')))}</td>")
        symbol = row.get("symbol")
        symbol = symbol.upper() if isinstance(symbol, str) else symbol
        lines.append(f"        <td>{html.escape(_fmt(symbol))}</td>")
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('market_cap')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('dev_stars')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('dev_forks')))}</td>"
        )
        lines.append(f"        <td class=\"num\">{html.escape(issues)}</td>")
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('dev_prs_merged')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('dev_commits_4w')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('reddit_subscribers')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('reddit_active_48h')))}</td>"
        )
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('telegram_users')))}</td>"
        )
        lines.append("      </tr>")

    lines.append("    </tbody>")
    lines.append("  </table>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)
