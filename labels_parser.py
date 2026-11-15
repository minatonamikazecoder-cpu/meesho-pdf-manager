"""
Parser for Meesho Sub Order Labels PDF.
Each page = 1 order. Extracts courier, SKU, qty from each page.
Groups by courier → trimmed SKU (removes last 5 characters) → sum quantities.
Also provides overall summary across all couriers.
"""

import pdfplumber
from collections import defaultdict, OrderedDict
import re

KNOWN_COURIERS = [
    'Valmo',
    'Shadowfax',
    'Delhivery',
    'Xpressbees',
    'Ecom Express',
    'Blue Dart',
    'DTDC',
    'Smartr'
]


def trim_sku(sku: str) -> str:
    """Remove last 5 characters from SKU and trim whitespace."""
    return sku[:-5].strip() if len(sku) > 5 else sku.strip()


def parse_labels(filepath: str) -> dict:
    """
    Parse a Sub Order Labels PDF and return structured data.

    Returns:
        {
            'date': str,
            'courier_groups': OrderedDict of courier -> [(trimmed_sku, qty)],
            'courier_subtotals': dict of courier -> int,
            'overall': [(trimmed_sku, qty)],
            'grand_total': int,
        }
    """
    orders = []  # list of (courier, sku, qty)
    date_str = None

    line_regex = re.compile(
        r'^(.*?)\s+(Free\s+Size|[A-Za-z0-9_-]+)\s+(\d+)\s+(\S+)\s+([0-9_]+)$',
        re.IGNORECASE
    )

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            tables = page.extract_tables()

            # --- Detect courier from page text ---
            courier = "Unknown"
            for c in KNOWN_COURIERS:
                if c.lower() in text.lower():
                    courier = c
                    break

            # --- Extract date from invoice section ---
            if date_str is None:
                # Look for date pattern like "07.11.2026" or "07/11/2026"
                date_match = re.search(r'(\d{2}[./-]\d{2}[./-]\d{4})', text)
                if date_match:
                    date_str = date_match.group(1)

            # --- Extract SKU and Qty from Product Details ---
            page_extracted = False
            if tables:
                for table in tables:
                    for row in table:
                        if not row or not row[0]:
                            continue
                        cell = str(row[0])
                        if 'Product Details' in cell:
                            for line in cell.split('\n'):
                                line = line.strip()
                                if not line or 'Product' in line or ('SKU' in line and 'Size' in line):
                                    continue
                                # Match standard line: SKU Size Qty Color OrderNo
                                m = line_regex.match(line)
                                if m:
                                    sku, size, qty_val, color, order_no = m.groups()
                                    try:
                                        qty = int(qty_val)
                                    except ValueError:
                                        qty = 1
                                    orders.append((courier, sku.strip(), qty))
                                    page_extracted = True
                                    break
                                elif 'Free Size' in line:
                                    parts = line.split('Free Size')
                                    sku = parts[0].strip()
                                    qty = 1
                                    if len(parts) > 1:
                                        rest = parts[1].strip().split()
                                        if rest:
                                            try:
                                                qty = int(rest[0])
                                            except ValueError:
                                                qty = 1
                                    orders.append((courier, sku, qty))
                                    page_extracted = True
                                    break
                        if page_extracted:
                            break
                    if page_extracted:
                        break

    # --- Group by courier, then by trimmed SKU, sum quantities ---
    courier_data = OrderedDict()
    overall = defaultdict(int)

    # Preserve order of appearance for couriers
    seen_couriers = []
    for courier, sku, qty in orders:
        if courier not in seen_couriers:
            seen_couriers.append(courier)

    for courier in seen_couriers:
        grouped = defaultdict(int)
        for c, sku, qty in orders:
            if c == courier:
                trimmed = trim_sku(sku)
                grouped[trimmed] += qty
                overall[trimmed] += qty
        courier_data[courier] = sorted(grouped.items(), key=lambda x: -x[1])

    courier_subtotals = {}
    for courier, items in courier_data.items():
        courier_subtotals[courier] = sum(qty for _, qty in items)

    sorted_overall = sorted(overall.items(), key=lambda x: -x[1])
    grand_total = sum(overall.values())

    return {
        'date': date_str or 'Unknown',
        'courier_groups': courier_data,
        'courier_subtotals': courier_subtotals,
        'overall': sorted_overall,
        'grand_total': grand_total,
    }
