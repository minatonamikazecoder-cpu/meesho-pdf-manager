"""
Flask web app for Meesho PDF extraction:
1. Supplier Manifest: Picklist & Courier Packing Lists
2. Sub Order Labels: High-performance multi-page shipping labels parser (handles 1,000+ pages)
"""

from flask import Flask, render_template, request
from parsers import parse_manifest, parse_labels
from werkzeug.utils import secure_filename
import os
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024  # 150 MB max upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def manifest():
    data = None
    error = None

    if request.method == 'POST':
        file = request.files.get('pdf')
        if not file or not file.filename:
            error = 'Please select a Supplier Manifest PDF file.'
        elif not file.filename.lower().endswith('.pdf'):
            error = 'Only PDF files are allowed.'
        else:
            safe_name = secure_filename(file.filename) or 'manifest.pdf'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            file.save(filepath)
            try:
                data = parse_manifest(filepath)
                if not data or data.get('grand_total', 0) == 0:
                    error = 'No manifest data could be found in this PDF. Please check if this is a Supplier Manifest PDF.'
            except Exception as e:
                traceback.print_exc()
                error = f'Failed to process Supplier Manifest: {str(e)}'
            finally:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass

    return render_template(
        'index.html',
        active_tab='manifest',
        page_title='Supplier Manifest Manager',
        page_desc='Upload Supplier Manifest PDF → Courier-wise SKU summary',
        upload_placeholder='Drop your Supplier Manifest PDF here or click to browse',
        data=data,
        error=error,
    )


@app.route('/labels', methods=['GET', 'POST'])
def labels():
    data = None
    error = None

    if request.method == 'POST':
        file = request.files.get('pdf')
        if not file or not file.filename:
            error = 'Please select a Sub Order Labels PDF file.'
        elif not file.filename.lower().endswith('.pdf'):
            error = 'Only PDF files are allowed.'
        else:
            safe_name = secure_filename(file.filename) or 'labels.pdf'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            file.save(filepath)
            try:
                data = parse_labels(filepath)
                if not data or data.get('grand_total', 0) == 0:
                    error = 'No shipping labels could be parsed from this PDF. Please verify this is a Sub Order Labels PDF.'
            except Exception as e:
                traceback.print_exc()
                error = f'Failed to process Sub Order Labels: {str(e)}'
            finally:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass

    return render_template(
        'index.html',
        active_tab='labels',
        page_title='Sub Order Labels Manager',
        page_desc='Upload Sub Order Labels PDF → Multi-page courier & SKU summary (Fast: supports 1,000+ pages)',
        upload_placeholder='Drop your Sub Order Labels PDF here or click to browse',
        data=data,
        error=error,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
