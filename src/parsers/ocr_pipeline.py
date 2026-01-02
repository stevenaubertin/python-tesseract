"""
OCR Pipeline - Main orchestrator for PDF/Image to text extraction

Combines PDFToImageService and TesseractOCRParser for complete OCR workflow.
"""
from typing import Union, List, Optional, Dict, Any
from pathlib import Path
from PIL import Image
import logging

from ..services.pdf_service import PDFToImageService, PDFConversionError
from .ocr_parser import TesseractOCRParser, OCRError

logger = logging.getLogger(__name__)


class OCRPipeline:
    """
    Main OCR pipeline that handles both PDF and image inputs.
    
    Workflow:
        PDF -> Images -> Text Data
        Image -> Text Data
    """
    
    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        tessdata_prefix: Optional[str] = None,
        poppler_path: Optional[str] = None,
        dpi: int = 300,
        lang: str = 'eng'
    ):
        """
        Initialize OCR Pipeline.
        
        Args:
            tesseract_cmd: Path to tesseract executable
            tessdata_prefix: Path to tessdata directory
            poppler_path: Path to poppler binaries
            dpi: DPI for PDF to image conversion
            lang: Language code for OCR
        """
        self.pdf_service = PDFToImageService(poppler_path=poppler_path, dpi=dpi)
        self.ocr_parser = TesseractOCRParser(
            tesseract_cmd=tesseract_cmd,
            tessdata_prefix=tessdata_prefix,
            lang=lang
        )
        logger.info("OCRPipeline initialized")
    
    def process_image(
        self,
        image_source: Union[str, Path, Image.Image],
        extract_data: bool = False,
        min_confidence: Optional[float] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process a single image and extract text.
        
        Args:
            image_source: Path to image or PIL Image object
            extract_data: If True, return detailed data; if False, return text only
            min_confidence: Minimum confidence threshold for text extraction
            
        Returns:
            Extracted text string or detailed data dictionary
        """
        logger.info(f"Processing image: {image_source}")
        
        try:
            if min_confidence is not None:
                return self.ocr_parser.extract_text_with_confidence(
                    image_source,
                    min_confidence=min_confidence
                )
            elif extract_data:
                return self.ocr_parser.extract_data(image_source)
            else:
                return self.ocr_parser.extract_text(image_source)
                
        except (FileNotFoundError, OCRError) as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    def process_pdf(
        self,
        pdf_path: Union[str, Path],
        extract_data: bool = False,
        page_number: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> Union[str, List[str], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process PDF and extract text from all pages or specific page.
        
        Args:
            pdf_path: Path to PDF file
            extract_data: If True, return detailed data; if False, return text only
            page_number: Specific page to process (1-indexed), or None for all pages
            min_confidence: Minimum confidence threshold for text extraction
            
        Returns:
            - Single page: text string or data dict
            - Multiple pages: list of text strings or list of data dicts
        """
        logger.info(f"Processing PDF: {pdf_path} (page: {page_number or 'all'})")
        
        try:
            # Convert PDF to images
            if page_number:
                images = [self.pdf_service.convert_single_page(pdf_path, page_number)]
            else:
                images = self.pdf_service.convert_pdf_to_images(pdf_path)
            
            # Process each image
            results = []
            for idx, image in enumerate(images, start=1):
                logger.debug(f"Processing page {idx}/{len(images)}")
                result = self.process_image(image, extract_data, min_confidence)
                results.append(result)
            
            # Return single result or list
            if page_number:
                return results[0]
            else:
                return results
                
        except (FileNotFoundError, PDFConversionError, OCRError) as e:
            logger.error(f"PDF processing failed: {e}")
            raise
    
    def process(
        self,
        input_path: Union[str, Path],
        extract_data: bool = False,
        page_number: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> Union[str, List[str], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process input file (auto-detects PDF or image) and extract text.
        
        Args:
            input_path: Path to PDF or image file
            extract_data: If True, return detailed data; if False, return text only
            page_number: For PDFs, specific page to process (1-indexed)
            min_confidence: Minimum confidence threshold for text extraction
            
        Returns:
            Extracted text or detailed data (single or list depending on input)
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine file type and process accordingly
        if input_path.suffix.lower() == '.pdf':
            return self.process_pdf(input_path, extract_data, page_number, min_confidence)
        else:
            # Treat as image
            if page_number:
                logger.warning(f"page_number parameter ignored for image input: {input_path}")
            return self.process_image(input_path, extract_data, min_confidence)
