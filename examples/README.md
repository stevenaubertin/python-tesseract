# Examples

This directory contains example scripts demonstrating how to use the python-tesseract library.

## Examples

### 1. `basic_usage.py`
Basic OCR operations:
- Extract text from images
- Extract text from PDFs
- Process with confidence filtering
- Auto-detect file types

```bash
python examples/basic_usage.py
```

### 2. `advanced_usage.py`
Advanced OCR features:
- Extract detailed OCR data with bounding boxes
- Filter by confidence threshold
- Group words by lines
- Analyze text positions

```bash
python examples/advanced_usage.py
```

### 3. `pdf_conversion.py`
PDF to image conversion:
- Convert all PDF pages to images
- Convert specific pages
- Convert page ranges
- Save images to disk

```bash
python examples/pdf_conversion.py
```

## Setup

Before running the examples, ensure you have:

1. Installed dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Installed Tesseract OCR:
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

3. Updated the Tesseract path in the examples if needed (Windows only)

## Sample Files

The examples expect sample files in the project root:
- `sample.png` - Sample image file
- `sample.pdf` - Sample PDF file

You can use your own files by updating the paths in the examples.
