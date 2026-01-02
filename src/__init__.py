"""
Main package initialization
"""
from .parsers.ocr_pipeline import OCRPipeline
from .parsers.ocr_parser import TesseractOCRParser, OCRError
from .services.pdf_service import PDFToImageService, PDFConversionError

__version__ = "1.0.0"
__all__ = [
    'OCRPipeline',
    'TesseractOCRParser',
    'PDFToImageService',
    'OCRError',
    'PDFConversionError'
]
