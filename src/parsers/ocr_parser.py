"""
OCR Parser for extracting text from images using Tesseract

Provides functionality to extract text and detailed data from images.
"""
from typing import Dict, Any, Optional, Union
from pathlib import Path
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Raised when OCR processing fails"""
    pass


class TesseractOCRParser:
    """Parser for extracting text from images using Tesseract OCR"""
    
    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        tessdata_prefix: Optional[str] = None,
        lang: str = 'eng'
    ):
        """
        Initialize Tesseract OCR Parser.
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
            tessdata_prefix: Path to tessdata directory (optional)
            lang: Language code for OCR (default: 'eng')
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Tesseract command set to: {tesseract_cmd}")
        
        if tessdata_prefix:
            import os
            os.environ['TESSDATA_PREFIX'] = tessdata_prefix
            logger.info(f"TESSDATA_PREFIX set to: {tessdata_prefix}")
        
        self.lang = lang
        logger.info(f"TesseractOCRParser initialized with language: {lang}")
    
    def _load_image(self, image_source: Union[str, Path, Image.Image]) -> Image.Image:
        """
        Load image from file path or return PIL Image if already loaded.
        
        Args:
            image_source: Path to image file or PIL Image object
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            OCRError: If image cannot be loaded
        """
        if isinstance(image_source, Image.Image):
            return image_source
        
        image_path = Path(image_source)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            return Image.open(image_path)
        except Exception as e:
            raise OCRError(f"Failed to load image: {e}") from e
    
    def extract_text(
        self,
        image_source: Union[str, Path, Image.Image],
        config: str = ''
    ) -> str:
        """
        Extract text from image.
        
        Args:
            image_source: Path to image file or PIL Image object
            config: Additional Tesseract configuration string
            
        Returns:
            Extracted text as string
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            OCRError: If OCR processing fails
        """
        image = self._load_image(image_source)
        
        logger.info(f"Extracting text from image (size: {image.size}, mode: {image.mode})")
        
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=config
            )
            
            logger.debug(f"Extracted {len(text)} characters")
            return text.strip()
            
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise OCRError(f"OCR processing failed: {e}") from e
    
    def extract_data(
        self,
        image_source: Union[str, Path, Image.Image],
        config: str = ''
    ) -> Dict[str, Any]:
        """
        Extract detailed OCR data from image.
        
        Returns structured data including text, confidence scores, and bounding boxes.
        
        Args:
            image_source: Path to image file or PIL Image object
            config: Additional Tesseract configuration string
            
        Returns:
            Dictionary containing OCR data with keys:
                - text: List of text elements
                - conf: List of confidence scores
                - left, top, width, height: Bounding box coordinates
                - level, page_num, block_num, par_num, line_num, word_num
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            OCRError: If OCR processing fails
        """
        image = self._load_image(image_source)
        
        logger.info(f"Extracting detailed data from image (size: {image.size})")
        
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate statistics
            text_elements = sum(1 for t in data['text'] if t.strip())
            valid_conf = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(valid_conf) / len(valid_conf) if valid_conf else 0
            
            logger.info(f"Extracted {text_elements} text elements, avg confidence: {avg_confidence:.2f}%")
            
            return data
            
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract data extraction failed: {e}")
            raise OCRError(f"OCR data extraction failed: {e}") from e
    
    def extract_text_with_confidence(
        self,
        image_source: Union[str, Path, Image.Image],
        min_confidence: float = 0.0,
        config: str = ''
    ) -> Dict[str, Any]:
        """
        Extract text with confidence scores, optionally filtering by minimum confidence.
        
        Args:
            image_source: Path to image file or PIL Image object
            min_confidence: Minimum confidence threshold (0-100)
            config: Additional Tesseract configuration string
            
        Returns:
            Dictionary with:
                - full_text: Complete extracted text
                - words: List of dicts with {text, confidence, bbox}
                - avg_confidence: Average confidence score
                - total_words: Total number of words
        """
        data = self.extract_data(image_source, config)
        
        words = []
        for i, text in enumerate(data['text']):
            if not text.strip():
                continue
            
            conf = int(data['conf'][i])
            if conf < min_confidence:
                continue
            
            words.append({
                'text': text,
                'confidence': conf,
                'bbox': {
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i]
                }
            })
        
        valid_conf = [w['confidence'] for w in words if w['confidence'] > 0]
        avg_conf = sum(valid_conf) / len(valid_conf) if valid_conf else 0
        
        full_text = ' '.join(w['text'] for w in words)
        
        return {
            'full_text': full_text,
            'words': words,
            'avg_confidence': avg_conf,
            'total_words': len(words)
        }
