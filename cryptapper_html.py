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
    lines.append("    th.sortable { cursor: pointer; }")
    lines.append("    th.sortable::after { content: ' ⇅'; color: #888; font-size: 0.9em; }")
    lines.append("  </style>")
    lines.append("  <script>")
    lines.append("    function sortTable(n, type) {")
    lines.append("      const table = document.getElementById('crypto-table');")
    lines.append("      const tbody = table.tBodies[0];")
    lines.append("      const rows = Array.from(tbody.rows);")
    lines.append("      const current = table.getAttribute('data-sort-col');")
    lines.append("      const dir = (current === String(n) && table.getAttribute('data-sort-dir') === 'asc') ? 'desc' : 'asc';")
    lines.append("      rows.sort((a, b) => {")
    lines.append("        const aText = a.cells[n].innerText.trim();")
    lines.append("        const bText = b.cells[n].innerText.trim();")
    lines.append("        let av = aText;")
    lines.append("        let bv = bText;")
    lines.append("        if (type === 'num') {")
    lines.append("          av = parseFloat(aText.replace(/,/g, ''));")
    lines.append("          bv = parseFloat(bText.replace(/,/g, ''));")
    lines.append("          if (isNaN(av)) av = -Infinity;")
    lines.append("          if (isNaN(bv)) bv = -Infinity;")
    lines.append("        } else {")
    lines.append("          av = aText.toLowerCase();")
    lines.append("          bv = bText.toLowerCase();")
    lines.append("        }")
    lines.append("        if (av < bv) return dir === 'asc' ? -1 : 1;")
    lines.append("        if (av > bv) return dir === 'asc' ? 1 : -1;")
    lines.append("        return 0;")
    lines.append("      });")
    lines.append("      rows.forEach(row => tbody.appendChild(row));")
    lines.append("      table.setAttribute('data-sort-col', String(n));")
    lines.append("      table.setAttribute('data-sort-dir', dir);")
    lines.append("    }")
    lines.append("  </script>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append(f"  <h1>Top {start}-{end} Cryptocurrencies by Market Cap</h1>")
    lines.append("  <table id=\"crypto-table\" data-sort-col=\"\" data-sort-dir=\"asc\">")
    lines.append("    <thead>")
    lines.append("      <tr>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(0, 'num')\">Rank</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(1, 'text')\">Name</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(2, 'text')\">Symbol</th>")
    lines.append("        <th class=\"sortable num\" onclick=\"sortTable(3, 'num')\">Market Cap (USD)</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(4, 'text')\">Homepage</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(5, 'text')\">GitHub</th>")
    lines.append("        <th class=\"sortable num\" onclick=\"sortTable(6, 'num')\">GitHub Stars</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(7, 'text')\">Languages</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(8, 'text')\">Twitter</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(9, 'text')\">Reddit</th>")
    lines.append("        <th class=\"sortable\" onclick=\"sortTable(10, 'text')\">Telegram</th>")
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
        languages = row.get("github_languages") or []
        lang_text = ", ".join(languages[:3]) if languages else "N/A"
        lines.append(f"        <td>{html.escape(lang_text)}</td>")
        lines.append(f"        <td>{_link(row.get('twitter'))}</td>")
        lines.append(f"        <td>{_link(row.get('reddit'))}</td>")
        lines.append(f"        <td>{_link(row.get('telegram'))}</td>")
        lines.append("      </tr>")

    lines.append("    </tbody>")
    lines.append("  </table>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)
