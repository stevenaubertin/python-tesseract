# Python Tesseract OCR Library

A production-ready, modular OCR system for extracting text from PDFs and images using Tesseract OCR.

## ✨ Features

- 🔄 **PDF to Image Conversion** - Convert PDFs to images with configurable DPI
- 📝 **OCR Text Extraction** - Extract text from images with Tesseract
- 📊 **Confidence Scoring** - Get confidence scores and filter low-quality results
- 📍 **Bounding Boxes** - Extract word positions and coordinates
- 🎯 **Auto-Detection** - Automatically detect and process PDF or image files
- ⚡ **High Performance** - Efficient processing with PIL and optimized workflows
- 🧪 **Fully Tested** - 104 tests (52 unit + 52 integration) with pytest
- 📦 **Modular Design** - Clean separation of services and parsers

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## 🚀 Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR
- Poppler (for PDF support)

### Install Tesseract OCR

- **Windows**: Download from [UB Mannheim's Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Install Poppler (for PDF support)

- **Windows**: Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### Install Python Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd python-tesseract

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### Basic Text Extraction

```python
from src.parsers.ocr_pipeline import OCRPipeline

# Initialize pipeline
pipeline = OCRPipeline(
    tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows
    tessdata_prefix=r'C:\Program Files\Tesseract-OCR\tessdata',      # Windows
    dpi=300,
    lang='eng'
)

# Extract text from image
text = pipeline.process_image("invoice.png")
print(text)

# Extract text from PDF (single page)
text = pipeline.process_pdf("document.pdf", page_number=1)
print(text)

# Auto-detect file type
text = pipeline.process("file.pdf")  # or "file.png"
print(text)
```

### Advanced Usage with Confidence Filtering

```python
# Extract only high-confidence words
result = pipeline.process_image("invoice.png", min_confidence=70.0)

print(f"Total words: {result['total_words']}")
print(f"Average confidence: {result['avg_confidence']:.2f}%")
print(f"Text: {result['full_text']}")

# Access individual words with positions
for word in result['words']:
    print(f"{word['text']} ({word['confidence']}%) at {word['bbox']}")
```

## 🏗️ Architecture

```
src/
├── services/
│   └── pdf_service.py       # PDF → Image conversion
├── parsers/
│   ├── ocr_parser.py        # Image → Text extraction
│   └── ocr_pipeline.py      # Main orchestrator
└── __init__.py

tests/
├── parsers/
│   ├── test_ocr_parser.py           # Integration tests
│   ├── test_ocr_parser_unit.py      # Unit tests with mocks
│   ├── test_ocr_pipeline.py         # Integration tests
│   └── test_ocr_pipeline_unit.py    # Unit tests with mocks
└── services/
    ├── test_pdf_service.py          # Integration tests
    └── test_pdf_service_unit.py     # Unit tests with mocks

examples/
├── basic_usage.py           # Basic examples
├── advanced_usage.py        # Advanced features
└── pdf_conversion.py        # PDF conversion examples
```

### Components

**1. PDFToImageService** (`src/services/pdf_service.py`)
- Converts PDFs to images using pdf2image/Poppler
- Configurable DPI and page ranges
- Save images to disk

**2. TesseractOCRParser** (`src/parsers/ocr_parser.py`)
- Extracts text from images using Tesseract
- Provides confidence scores and bounding boxes
- Supports multiple extraction modes

**3. OCRPipeline** (`src/parsers/ocr_pipeline.py`)
- Main orchestrator combining services
- Unified interface for PDF and image processing
- Auto-detection of file types

## 📚 Usage Examples

### Process Images

```python
from src.parsers.ocr_pipeline import OCRPipeline

pipeline = OCRPipeline()

# Simple text extraction
text = pipeline.process_image("document.png")

# Get detailed OCR data
data = pipeline.process_image("document.png", extract_data=True)
print(f"Text elements: {data['text']}")
print(f"Confidence: {data['conf']}")
print(f"Positions: {list(zip(data['left'], data['top']))}")

# Filter by confidence
result = pipeline.process_image("document.png", min_confidence=80.0)
print(f"High-confidence words: {result['total_words']}")
```

### Process PDFs

```python
# Process single page
text = pipeline.process_pdf("document.pdf", page_number=1)

# Process all pages
pages = pipeline.process_pdf("document.pdf")
for i, text in enumerate(pages, 1):
    print(f"Page {i}: {len(text)} characters")

# Process with confidence filtering
result = pipeline.process_pdf(
    "document.pdf",
    page_number=1,
    min_confidence=70.0
)
```

### Direct Service Usage

```python
# PDF to Image conversion
from src.services.pdf_service import PDFToImageService

service = PDFToImageService(dpi=300)
images = service.convert_pdf_to_images("document.pdf")
service.save_images(images, "output", base_name="page", format="PNG")

# OCR extraction
from src.parsers.ocr_parser import TesseractOCRParser

parser = TesseractOCRParser()
text = parser.extract_text("image.png")
data = parser.extract_data("image.png")
```

### See More Examples

Check the `examples/` directory for complete working examples:
- `basic_usage.py` - Basic OCR operations
- `advanced_usage.py` - Advanced features and confidence filtering
- `pdf_conversion.py` - PDF to image conversion

## 📖 API Reference

### OCRPipeline

#### Constructor

```python
OCRPipeline(
    tesseract_cmd: Optional[str] = None,
    tessdata_prefix: Optional[str] = None,
    poppler_path: Optional[str] = None,
    dpi: int = 300,
    lang: str = 'eng'
)
```

**Parameters:**
- `tesseract_cmd`: Path to Tesseract executable
- `tessdata_prefix`: Path to tessdata directory
- `poppler_path`: Path to Poppler binaries
- `dpi`: DPI for PDF to image conversion (default: 300)
- `lang`: Language code for OCR (default: 'eng')

#### Methods

**process_image()**
```python
process_image(
    image_source: Union[str, Path, Image.Image],
    extract_data: bool = False,
    min_confidence: Optional[float] = None
) -> Union[str, Dict[str, Any]]
```

**process_pdf()**
```python
process_pdf(
    pdf_path: Union[str, Path],
    extract_data: bool = False,
    page_number: Optional[int] = None,
    min_confidence: Optional[float] = None
) -> Union[str, List[str], Dict[str, Any], List[Dict[str, Any]]]
```

**process()**
```python
process(
    input_path: Union[str, Path],
    extract_data: bool = False,
    page_number: Optional[int] = None,
    min_confidence: Optional[float] = None
) -> Union[str, List[str], Dict[str, Any], List[Dict[str, Any]]]
```

### Return Types

**Simple Text:**
```python
text: str = "Extracted text..."
```

**Detailed Data:**
```python
data: Dict[str, Any] = {
    'text': ['word1', 'word2', ...],
    'conf': [95, 87, ...],
    'left': [10, 50, ...],
    'top': [20, 25, ...],
    'width': [40, 35, ...],
    'height': [15, 15, ...],
}
```

**Confidence Filtered:**
```python
result: Dict[str, Any] = {
    'full_text': 'Complete text...',
    'words': [
        {
            'text': 'word',
            'confidence': 95,
            'bbox': {'left': 10, 'top': 20, 'width': 40, 'height': 15}
        },
    ],
    'avg_confidence': 87.5,
    'total_words': 150
}
```

## 🧪 Testing

The project includes a comprehensive test suite with 104 tests:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/parsers/test_ocr_parser_unit.py -v
pytest tests/parsers/test_ocr_pipeline_unit.py -v
pytest tests/services/test_pdf_service_unit.py -v

# Run integration tests (requires Tesseract installed)
pytest tests/parsers/test_ocr_parser.py -v
pytest tests/parsers/test_ocr_pipeline.py -v
pytest tests/services/test_pdf_service.py -v
```

### Test Coverage

- **52 Unit Tests** - Fast, isolated tests with mocks
- **52 Integration Tests** - End-to-end tests with real dependencies
- **100% Code Coverage** - All major functions tested

## ⚙️ Configuration

### Tesseract Configuration

**Method 1: In code**
```python
pipeline = OCRPipeline(
    tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    tessdata_prefix=r'C:\Program Files\Tesseract-OCR\tessdata'
)
```

**Method 2: Environment variables**
```bash
export TESSERACT_CMD="/usr/bin/tesseract"
export TESSDATA_PREFIX="/usr/share/tesseract-ocr/tessdata"
```

### Poppler Configuration

```python
pipeline = OCRPipeline(
    poppler_path=r'C:\poppler\Library\bin'  # Windows
)
```

### Language Support

```python
# Use different language
pipeline = OCRPipeline(lang='fra')  # French
pipeline = OCRPipeline(lang='deu')  # German
pipeline = OCRPipeline(lang='spa')  # Spanish

# Multiple languages
pipeline = OCRPipeline(lang='eng+fra')  # English + French
```

## ⚠️ Error Handling

```python
from src.parsers.ocr_pipeline import OCRPipeline
from src.parsers.ocr_parser import OCRError
from src.services.pdf_service import PDFConversionError

try:
    pipeline = OCRPipeline()
    text = pipeline.process("document.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except PDFConversionError as e:
    print(f"PDF conversion failed: {e}")
except OCRError as e:
    print(f"OCR processing failed: {e}")
```

## 📁 Project Structure

```
python-tesseract/
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── ocr_parser.py       # OCR text extraction
│   │   └── ocr_pipeline.py     # Main orchestrator
│   └── services/
│       ├── __init__.py
│       └── pdf_service.py      # PDF conversion
│
├── tests/                  # Test suite (104 tests)
│   ├── conftest.py
│   ├── parsers/
│   │   ├── test_ocr_parser.py
│   │   ├── test_ocr_parser_unit.py
│   │   ├── test_ocr_pipeline.py
│   │   └── test_ocr_pipeline_unit.py
│   └── services/
│       ├── test_pdf_service.py
│       └── test_pdf_service_unit.py
│
└── examples/               # Usage examples
    ├── README.md
    ├── basic_usage.py
    ├── advanced_usage.py
    └── pdf_conversion.py
```

## 🎯 Use Cases

- **Invoice Processing** - Extract data from scanned invoices
- **Document Digitization** - Convert PDFs to searchable text
- **Form Processing** - Extract fields from forms and surveys
- **Receipt Parsing** - Read and process receipt data
- **Business Card Scanning** - Extract contact information
- **Archive Digitization** - Convert old documents to searchable text

## 🛠️ Requirements

- Python 3.10+
- pytesseract
- Pillow (PIL)
- pdf2image
- Tesseract OCR (system install)
- Poppler (for PDF support)

See `requirements.txt` for complete dependencies.

## 📄 License

[Your License Here]

## 🤝 Contributing

This is a production-ready template. Feel free to extend and customize for your needs.

## 📞 Support

For issues and questions, please open an issue on the repository.
