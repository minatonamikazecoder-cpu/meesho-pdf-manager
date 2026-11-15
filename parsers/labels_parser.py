"""
High-Performance Parser for Meesho Sub Order Labels PDF.
Built with C++ Google PDFium (pypdfium2) for ultra-fast processing
capable of handling 500 - 1,000+ pages in seconds without timeouts.

Extracts:
1. Courier heading (Valmo, Delhivery, Shadowfax, Xpress Bees, etc.)
2. SKU and quantity from Product Details
3. Trims last 5 characters from SKU and groups them
4. Sums quantities per courier and overall
"""

import pypdfium2
from collections import defaultdict, OrderedDict
import re

KNOWN_COURIERS = [
    'Xpress Bees',
    'Xpressbees',
    'Delhivery',
    'Shadowfax',
    'Valmo',
    'Ecom Express',
    'Ecom',
    'Blue Dart',
    'Bluedart',
    'DTDC',
    'Smartr',
    'Ekart',
    'Amazon Shipping'
]


def trim_sku(sku: str) -> str:
    """Remove last 5 characters from SKU and trim whitespace."""
    if not sku:
        return ""
    clean = sku.strip()
    return clean[:-5].strip() if len(clean) > 5 else clean


def parse_labels(filepath: str) -> dict:
    """
    Parse Sub Order Labels PDF and return structured, grouped data.
    Ultra-fast: uses C++ pdfium text-stream extraction.

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

    doc = pypdfium2.PdfDocument(filepath)

    for page in doc:
        try:
            textpage = page.get_textpage()
            text = textpage.get_text_range() or ""
        except Exception:
            continue

        if not text:
            continue

        # --- Detect courier from page text ---
        courier = "Unknown"
        text_lower = text.lower()
        for c in KNOWN_COURIERS:
            if c.lower() in text_lower:
                courier = 'Xpress Bees' if 'xpress' in c.lower() else c
                break

        # --- Extract date from invoice section (first found) ---
        if date_str is None:
            date_match = re.search(r'(\d{2}[./-]\d{2}[./-]\d{4})', text)
            if date_match:
                date_str = date_match.group(1)

        # --- Extract SKU and Qty from Product Details ---
        lines = text.split('\r\n') if '\r\n' in text else text.split('\n')
        sku = None
        qty = 1
        in_product_details = False

        for line in lines:
            line_str = line.strip()
            if 'Product Details' in line_str:
                in_product_details = True
                continue

            if in_product_details:
                # Stop if reached next section
                if any(stop in line_str for stop in ['TAX INVOICE', 'BILL TO', 'Description', 'Sold by', 'If undelivered']):
                    break
                # Skip header
                if 'SKU' in line_str and 'Size' in line_str:
                    continue

                m = line_regex.match(line_str)
                if m:
                    sku_val, size_val, qty_val, color_val, order_no = m.groups()
                    sku = sku_val.strip()
                    try:
                        qty = int(qty_val)
                    except (ValueError, TypeError):
                        qty = 1
                    break
                elif 'Free Size' in line_str:
                    parts = line_str.split('Free Size')
                    sku = parts[0].strip()
                    if len(parts) > 1:
                        rest = parts[1].strip().split()
                        if rest:
                            try:
                                qty = int(rest[0])
                            except (ValueError, TypeError):
                                qty = 1
                    break

        if sku:
            orders.append((courier, sku, qty))

    # --- Group by courier, then by trimmed SKU, sum quantities ---
    courier_data = OrderedDict()
    overall = defaultdict(int)

    # Preserve order of courier appearance
    seen_couriers = []
    for courier, sku, qty in orders:
        if courier not in seen_couriers:
            seen_couriers.append(courier)

    for courier in seen_couriers:
        grouped = defaultdict(int)
        for c, sku, qty in orders:
            if c == courier:
                trimmed = trim_sku(sku)
                if trimmed:
                    grouped[trimmed] += qty
                    overall[trimmed] += qty
        courier_data[courier] = sorted(grouped.items(), key=lambda x: -x[1])

    courier_subtotals = {}
    for courier, items in courier_data.items():
        courier_subtotals[courier] = sum(q for _, q in items)

    sorted_overall = sorted(overall.items(), key=lambda x: -x[1])
    grand_total = sum(overall.values())

    return {
        'date': date_str or 'Unknown',
        'courier_groups': courier_data,
        'courier_subtotals': courier_subtotals,
        'overall': sorted_overall,
        'grand_total': grand_total,
    }
