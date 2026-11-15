"""
Flask web app for Meesho PDF extraction:
1. Supplier Manifest: Picklist & Courier Packing Lists
2. Sub Order Labels: Multi-page shipping labels with courier & SKU grouping
"""

from flask import Flask, render_template, request, redirect, url_for
from manifest_parser import parse_manifest
from labels_parser import parse_labels
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            try:
                data = parse_manifest(filepath)
            except Exception as e:
                error = f'Failed to parse Supplier Manifest: {str(e)}'

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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            try:
                data = parse_labels(filepath)
            except Exception as e:
                error = f'Failed to parse Sub Order Labels: {str(e)}'

    return render_template(
        'index.html',
        active_tab='labels',
        page_title='Sub Order Labels Manager',
        page_desc='Upload Sub Order Labels PDF → Multi-page courier & SKU summary',
        upload_placeholder='Drop your Sub Order Labels PDF here or click to browse',
        data=data,
        error=error,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
