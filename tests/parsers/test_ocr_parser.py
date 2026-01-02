"""
Tests for TesseractOCRParser

Tests OCR text extraction functionality.
"""
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile
import os

from src.parsers.ocr_parser import TesseractOCRParser, OCRError


# Tesseract configuration - update paths as needed
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSDATA_PREFIX = r'C:\Program Files\Tesseract-OCR\tessdata'


class TestTesseractOCRParser:
    """Test suite for TesseractOCRParser"""
    
    @pytest.fixture
    def parser(self):
        """Create a TesseractOCRParser instance"""
        return TesseractOCRParser(
            tesseract_cmd=TESSERACT_CMD,
            tessdata_prefix=TESSDATA_PREFIX,
            lang='eng'
        )
    
    @pytest.fixture
    def test_image_with_text(self):
        """Create a test image with text"""
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Hello World", fill='black')
        return img
    
    @pytest.fixture
    def test_image_file(self, test_image_with_text):
        """Create a temporary test image file"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_image_with_text.save(f.name, 'PNG')
            yield f.name
        # Cleanup
        if os.path.exists(f.name):
            os.unlink(f.name)
    
    def test_initialization_default(self):
        """Test parser initialization with default parameters"""
        parser = TesseractOCRParser()
        assert parser.lang == 'eng'
    
    def test_initialization_custom_lang(self):
        """Test parser initialization with custom language"""
        parser = TesseractOCRParser(lang='fra')
        assert parser.lang == 'fra'
    
    def test_initialization_with_paths(self):
        """Test parser initialization with tesseract paths"""
        parser = TesseractOCRParser(
            tesseract_cmd=TESSERACT_CMD,
            tessdata_prefix=TESSDATA_PREFIX
        )
        assert parser.lang == 'eng'
    
    def test_load_image_from_pil(self, parser, test_image_with_text):
        """Test loading PIL Image object"""
        img = parser._load_image(test_image_with_text)
        assert isinstance(img, Image.Image)
        assert img.size == (400, 100)
    
    def test_load_image_from_file_path_string(self, parser, test_image_file):
        """Test loading image from string path"""
        img = parser._load_image(test_image_file)
        assert isinstance(img, Image.Image)
    
    def test_load_image_from_file_path_object(self, parser, test_image_file):
        """Test loading image from Path object"""
        img = parser._load_image(Path(test_image_file))
        assert isinstance(img, Image.Image)
    
    def test_load_image_file_not_found(self, parser):
        """Test that FileNotFoundError is raised for non-existent file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            parser._load_image("nonexistent_image.png")
        assert "Image file not found" in str(exc_info.value)
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_text_from_pil_image(self, parser, test_image_with_text):
        """Test extracting text from PIL Image"""
        text = parser.extract_text(test_image_with_text)
        assert isinstance(text, str)
        # Text should contain "Hello" or "World"
        assert "Hello" in text or "World" in text
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_text_from_file(self, parser, test_image_file):
        """Test extracting text from image file"""
        text = parser.extract_text(test_image_file)
        assert isinstance(text, str)
        assert "Hello" in text or "World" in text
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    @pytest.mark.skipif(
        not Path("data/test_output-000001.ppm").exists(),
        reason="Test PPM file not available"
    )
    def test_extract_text_from_real_document(self, parser):
        """Test extracting text from real document"""
        text = parser.extract_text("data/test_output-000001.ppm")
        assert isinstance(text, str)
        assert len(text) > 0
        # Should contain some expected text from the invoice
        assert "Vergers" in text or "commande" in text
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_data_from_image(self, parser, test_image_with_text):
        """Test extracting detailed data from image"""
        data = parser.extract_data(test_image_with_text)
        
        # Verify data structure
        assert isinstance(data, dict)
        assert 'text' in data
        assert 'conf' in data
        assert 'left' in data
        assert 'top' in data
        assert 'width' in data
        assert 'height' in data
        
        # Verify data types
        assert isinstance(data['text'], list)
        assert isinstance(data['conf'], list)
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_text_with_confidence_default(self, parser, test_image_with_text):
        """Test extracting text with confidence scores (no filtering)"""
        result = parser.extract_text_with_confidence(test_image_with_text)
        
        assert isinstance(result, dict)
        assert 'full_text' in result
        assert 'words' in result
        assert 'avg_confidence' in result
        assert 'total_words' in result
        
        assert isinstance(result['full_text'], str)
        assert isinstance(result['words'], list)
        assert isinstance(result['avg_confidence'], (int, float))
        assert isinstance(result['total_words'], int)
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_text_with_confidence_filtering(self, parser, test_image_with_text):
        """Test extracting text with confidence filtering"""
        # Get all words
        result_all = parser.extract_text_with_confidence(
            test_image_with_text,
            min_confidence=0.0
        )
        
        # Get high confidence words only
        result_filtered = parser.extract_text_with_confidence(
            test_image_with_text,
            min_confidence=80.0
        )
        
        # Filtered should have same or fewer words
        assert result_filtered['total_words'] <= result_all['total_words']
        
        # All filtered words should have confidence >= 80
        for word in result_filtered['words']:
            assert word['confidence'] >= 80.0
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_word_bounding_boxes(self, parser, test_image_with_text):
        """Test that bounding boxes are included in results"""
        result = parser.extract_text_with_confidence(test_image_with_text)
        
        if result['words']:
            word = result['words'][0]
            assert 'bbox' in word
            bbox = word['bbox']
            
            assert 'left' in bbox
            assert 'top' in bbox
            assert 'width' in bbox
            assert 'height' in bbox
            
            # All values should be non-negative
            assert bbox['left'] >= 0
            assert bbox['top'] >= 0
            assert bbox['width'] >= 0
            assert bbox['height'] >= 0
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_text_empty_image(self, parser):
        """Test extracting text from blank image"""
        blank_img = Image.new('RGB', (100, 100), color='white')
        text = parser.extract_text(blank_img)
        
        # Blank image should return empty or minimal text
        assert isinstance(text, str)
        assert len(text) < 10  # Should be mostly empty
    
    def test_extract_text_with_custom_config(self, parser, test_image_with_text):
        """Test extracting text with custom Tesseract config"""
        # This may or may not work depending on Tesseract installation
        try:
            text = parser.extract_text(
                test_image_with_text,
                config='--psm 6'  # Assume uniform block of text
            )
            assert isinstance(text, str)
        except OCRError:
            # Expected if Tesseract is not installed
            pass


class TestOCRError:
    """Test OCRError exception"""
    
    def test_exception_message(self):
        """Test exception can be raised with message"""
        with pytest.raises(OCRError) as exc_info:
            raise OCRError("Test OCR error")
        
        assert "Test OCR error" in str(exc_info.value)
    
    def test_exception_inheritance(self):
        """Test that OCRError is an Exception"""
        assert issubclass(OCRError, Exception)
    
    def test_exception_from_tesseract_error(self):
        """Test OCRError can wrap other exceptions"""
        original = ValueError("Original error")
        
        with pytest.raises(OCRError) as exc_info:
            try:
                raise original
            except ValueError as e:
                raise OCRError(f"OCR failed: {e}") from e
        
        assert "OCR failed" in str(exc_info.value)
        assert exc_info.value.__cause__ == original
