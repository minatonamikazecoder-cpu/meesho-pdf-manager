# Meesho PDF Extractor & Manager

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/minatonamikazecoder-cpu/meesho-pdf-manager)

A high-performance web application for Meesho sellers to extract, group, and summarize data from **Supplier Manifests** and **Sub Order Labels**.

## Project Structure

```
meesho-pdf-manager/
├── app.py                  # Main Flask application & routes
├── parsers/                # Core PDF extraction engines
│   ├── __init__.py
│   ├── manifest_parser.py  # Supplier Manifest parser (picklist & courier groups)
│   └── labels_parser.py    # Sub Order Labels parser (ultra-fast C++ PDFium)
├── templates/
│   └── index.html          # Tailwind CSS dashboard with Card & Excel views
├── sample_pdfs/            # Local test PDFs (ignored in git)
├── uploads/                # Temporary file uploads (auto-cleaned)
├── requirements.txt        # Production dependencies
├── Procfile                # Gunicorn process definition
├── render.yaml             # Render 1-click blueprint configuration
└── README.md
```

## Features

- 📦 **Supplier Manifest Extractor:**
  - Extracts manifest date.
  - Groups shipments by Courier (`Delhivery`, `Shadowfax`, `Valmo`, etc.).
  - Trims last 5 characters from SKUs and sums quantities per courier.
  - Overall total across all couriers.

- 🏷️ **Sub Order Labels Extractor:**
  - Ultra-fast engine powered by C++ Google PDFium (`pypdfium2`).
  - Supports massive files: handles **500 to 1,000+ page PDFs in seconds** without timeout.
  - Automatically identifies couriers (`Delhivery`, `Shadowfax`, `Valmo`, `Xpress Bees`, `Ecom Express`, etc.).
  - Groups by trimmed SKU and sums quantities per courier and overall.

- 📋 **Views:**
  - **Card View:** Color-coded visual cards per courier with subtotals.
  - **Excel View:** One-click copy tab-separated data, paste-ready for Excel / Google Sheets.

## Running Locally

```bash
git clone https://github.com/minatonamikazecoder-cpu/meesho-pdf-manager.git
cd meesho-pdf-manager

pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deployment

Deployable with 1-click on [Render](https://render.com) using the badge above, or via Gunicorn:

```bash
gunicorn --timeout 600 --workers 2 app:app
```
