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
    lines.append("        <th>Homepage</th>")
    lines.append("        <th>GitHub</th>")
    lines.append("        <th class=\"num\">GitHub Stars</th>")
    lines.append("        <th>Twitter</th>")
    lines.append("        <th>Reddit</th>")
    lines.append("        <th>Telegram</th>")
    lines.append("      </tr>")
    lines.append("    </thead>")
    lines.append("    <tbody>")

    def _link(url):
        if not url:
            return "N/A"
        esc = html.escape(url)
        return f"<a href=\"{esc}\" target=\"_blank\" rel=\"noopener\">{esc}</a>"

    for row in rows:
        lines.append("      <tr>")
        lines.append(f"        <td class=\"num\">{html.escape(_fmt(row.get('rank')))}</td>")
        lines.append(f"        <td>{html.escape(_fmt(row.get('name')))}</td>")
        symbol = row.get("symbol")
        symbol = symbol.upper() if isinstance(symbol, str) else symbol
        lines.append(f"        <td>{html.escape(_fmt(symbol))}</td>")
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('market_cap')))}</td>"
        )
        lines.append(f"        <td>{_link(row.get('homepage'))}</td>")
        lines.append(f"        <td>{_link(row.get('github'))}</td>")
        lines.append(
            f"        <td class=\"num\">{html.escape(_fmt(row.get('dev_stars')))}</td>"
        )
        lines.append(f"        <td>{_link(row.get('twitter'))}</td>")
        lines.append(f"        <td>{_link(row.get('reddit'))}</td>")
        lines.append(f"        <td>{_link(row.get('telegram'))}</td>")
        lines.append("      </tr>")

    lines.append("    </tbody>")
    lines.append("  </table>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)
