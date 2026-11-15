"""
Parser for Meesho Supplier Manifest PDF.
Extracts courier-wise shipment data, groups by trimmed SKU, and sums quantities.
"""

import pdfplumber
from collections import defaultdict, OrderedDict


def parse_manifest(filepath: str) -> dict:
    """
    Parse a Supplier Manifest PDF and return structured data.
    
    Returns:
        {
            'date': str,
            'courier_groups': OrderedDict of courier -> [(trimmed_sku, qty)],
            'courier_subtotals': dict of courier -> int,
            'overall': [(trimmed_sku, qty)],
            'grand_total': int,
        }
    """
    clean_skus = []           # Reference SKUs from picklist pages
    courier_items = OrderedDict()  # courier -> [(raw_sku, qty)]
    date_str = None

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            tables = page.extract_tables()

            # --- Extract date (first occurrence) ---
            if date_str is None:
                for line in text.split('\n'):
                    if 'Date' in line and ':' in line:
                        date_str = line.split(':', 1)[1].strip()
                        break

            # --- Picklist pages: collect clean SKU names ---
            if 'Picklist' in text:
                if tables:
                    for table in tables:
                        for row in table:
                            if row and row[0] and row[0] != 'SKU':
                                clean_skus.append(row[0].strip())

            # --- Courier pages: extract shipment rows ---
            elif 'Courier' in text:
                courier_name = None
                for line in text.split('\n'):
                    if 'Courier' in line and ':' in line:
                        courier_name = line.split(':', 1)[1].strip()
                        break

                if courier_name and tables:
                    if courier_name not in courier_items:
                        courier_items[courier_name] = []

                    for table in tables:
                        for row in table:
                            # Skip header row and empty rows
                            if not row or not row[0] or row[0] == 'S. No.':
                                continue
                            if len(row) >= 5:
                                raw_sku = (row[3] or '').strip()
                                qty_str = (row[4] or '0').strip()
                                try:
                                    qty = int(qty_str)
                                except ValueError:
                                    qty = 0
                                if raw_sku and qty > 0:
                                    courier_items[courier_name].append((raw_sku, qty))

    # --- Resolve dirty SKUs using picklist reference ---
    def resolve_sku(dirty_sku: str) -> str:
        no_newline = dirty_sku.replace('\n', '')
        with_space = dirty_sku.replace('\n', ' ')

        for clean in clean_skus:
            if clean == no_newline or clean == with_space:
                return clean
        return no_newline  # fallback

    # --- Trim SKU: remove last 5 characters and trim whitespace ---
    def trim_sku(sku: str) -> str:
        return sku[:-5].strip() if len(sku) > 5 else sku.strip()

    # --- Group by courier, then by trimmed SKU, sum quantities ---
    courier_groups = OrderedDict()
    courier_subtotals = {}
    overall = defaultdict(int)

    for courier, items in courier_items.items():
        grouped = defaultdict(int)
        for raw_sku, qty in items:
            clean = resolve_sku(raw_sku)
            trimmed = trim_sku(clean)
            grouped[trimmed] += qty
            overall[trimmed] += qty
        # Sort by quantity descending
        sorted_group = sorted(grouped.items(), key=lambda x: -x[1])
        courier_groups[courier] = sorted_group
        courier_subtotals[courier] = sum(grouped.values())

    sorted_overall = sorted(overall.items(), key=lambda x: -x[1])
    grand_total = sum(overall.values())

    return {
        'date': date_str or 'Unknown',
        'courier_groups': courier_groups,
        'courier_subtotals': courier_subtotals,
        'overall': sorted_overall,
        'grand_total': grand_total,
    }
