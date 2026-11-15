# Meesho PDF Extractor & Manager

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/minatonamikazecoder-cpu/meesho-pdf-manager)

A web application for sellers to extract, group, and summarize data from **Meesho Supplier Manifests** and **Sub Order Labels**.

## Features

- 📦 **Supplier Manifest Extractor:**
  - Extracts manifest date.
  - Groups shipments by Courier (`Delhivery`, `Shadowfax`, `Valmo`, etc.).
  - Trims the last 5 characters from SKUs and groups identical products.
  - Sums quantities and calculates courier subtotals.
  - Overall summary across all couriers with grand totals.

- 🏷️ **Sub Order Labels Extractor:**
  - Extracts customer shipment labels across multiple pages.
  - Automatically identifies couriers from label text.
  - Groups by trimmed SKU and sums quantities per courier.
  - Overall summary across all orders.

- 📋 **Views:**
  - **Card View:** Modern, color-coded visual dashboard.
  - **Excel View:** One-click copy tab-separated data, paste-ready for Microsoft Excel / Google Sheets.

## Running Locally

```bash
git clone https://github.com/minatonamikazecoder-cpu/meesho-pdf-manager.git
cd meesho-pdf-manager

pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deployment

This app is configured for deployment on [Render](https://render.com), [Railway](https://railway.app), or [Koyeb](https://koyeb.com) using `gunicorn`:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
