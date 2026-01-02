"""
Unit tests for TesseractOCRParser using mocks

These tests complement the integration tests in test_ocr_parser.py
by testing the logic in isolation using mocks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PIL import Image
import pytesseract

from src.parsers.ocr_parser import TesseractOCRParser, OCRError


class TestTesseractOCRParserInit:
    """Test TesseractOCRParser initialization"""
    
    def test_init_default(self):
        """Test initialization with default parameters"""
        parser = TesseractOCRParser()
        assert parser.lang == 'eng'
    
    def test_init_with_custom_lang(self):
        """Test initialization with custom language"""
        parser = TesseractOCRParser(lang='fra')
        assert parser.lang == 'fra'
    
    @patch('src.parsers.ocr_parser.pytesseract')
    def test_init_with_tesseract_cmd(self, mock_pytesseract):
        """Test initialization with custom tesseract command"""
        test_cmd = '/usr/bin/tesseract'
        parser = TesseractOCRParser(tesseract_cmd=test_cmd)
        assert mock_pytesseract.pytesseract.tesseract_cmd == test_cmd
    
    @patch.dict('os.environ', {}, clear=True)
    def test_init_with_tessdata_prefix(self):
        """Test initialization with custom tessdata prefix"""
        import os
        test_prefix = '/usr/share/tesseract'
        parser = TesseractOCRParser(tessdata_prefix=test_prefix)
        assert os.environ.get('TESSDATA_PREFIX') == test_prefix


class TestLoadImage:
    """Test _load_image method"""
    
    def test_load_image_from_pil_image(self):
        """Test loading from PIL Image object"""
        parser = TesseractOCRParser()
        mock_image = Mock(spec=Image.Image)
        
        result = parser._load_image(mock_image)
        assert result is mock_image
    
    @patch('src.parsers.ocr_parser.Path.exists')
    @patch('src.parsers.ocr_parser.Image.open')
    def test_load_image_from_path(self, mock_open, mock_exists):
        """Test loading image from file path"""
        parser = TesseractOCRParser()
        mock_exists.return_value = True
        mock_image = Mock(spec=Image.Image)
        mock_open.return_value = mock_image
        
        result = parser._load_image('test.png')
        assert result is mock_image
        mock_open.assert_called_once()
    
    @patch('src.parsers.ocr_parser.Path.exists')
    def test_load_image_file_not_found(self, mock_exists):
        """Test loading non-existent image raises FileNotFoundError"""
        parser = TesseractOCRParser()
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            parser._load_image('nonexistent.png')
    
    @patch('src.parsers.ocr_parser.Path.exists')
    @patch('src.parsers.ocr_parser.Image.open')
    def test_load_image_corrupt_file(self, mock_open, mock_exists):
        """Test loading corrupt image raises OCRError"""
        parser = TesseractOCRParser()
        mock_exists.return_value = True
        mock_open.side_effect = Exception("Corrupt image")
        
        with pytest.raises(OCRError, match="Failed to load image"):
            parser._load_image('corrupt.png')


class TestExtractText:
    """Test extract_text method"""
    
    @patch('src.parsers.ocr_parser.pytesseract.image_to_string')
    def test_extract_text_success(self, mock_image_to_string):
        """Test successful text extraction"""
        parser = TesseractOCRParser()
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (100, 100)
        mock_image.mode = 'RGB'
        mock_image_to_string.return_value = '  Extracted text  '
        
        result = parser.extract_text(mock_image)
        
        assert result == 'Extracted text'
        mock_image_to_string.assert_called_once_with(
            mock_image,
            lang='eng',
            config=''
        )
    
    @patch('src.parsers.ocr_parser.pytesseract.image_to_string')
    def test_extract_text_with_config(self, mock_image_to_string):
        """Test text extraction with custom config"""
        parser = TesseractOCRParser(lang='fra')
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (100, 100)
        mock_image.mode = 'RGB'
        mock_image_to_string.return_value = 'Texte français'
        
        result = parser.extract_text(mock_image, config='--psm 6')
        
        assert result == 'Texte français'
        mock_image_to_string.assert_called_once_with(
            mock_image,
            lang='fra',
            config='--psm 6'
        )
    
    @patch('src.parsers.ocr_parser.pytesseract.image_to_string')
    def test_extract_text_tesseract_error(self, mock_image_to_string):
        """Test text extraction handles Tesseract errors"""
        parser = TesseractOCRParser()
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (100, 100)
        mock_image.mode = 'RGB'
        mock_image_to_string.side_effect = pytesseract.TesseractError(1, "Tesseract failed")
        
        with pytest.raises(OCRError, match="OCR processing failed"):
            parser.extract_text(mock_image)


class TestExtractData:
    """Test extract_data method"""
    
    @patch('src.parsers.ocr_parser.pytesseract.image_to_data')
    def test_extract_data_success(self, mock_image_to_data):
        """Test successful data extraction"""
        parser = TesseractOCRParser()
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (200, 200)
        
        mock_data = {
            'text': ['Hello', 'World', ''],
            'conf': ['95', '88', '-1'],
            'left': [10, 50, 0],
            'top': [10, 10, 0],
            'width': [30, 40, 0],
            'height': [15, 15, 0]
        }
        mock_image_to_data.return_value = mock_data
        
        result = parser.extract_data(mock_image)
        
        assert result == mock_data
        mock_image_to_data.assert_called_once_with(
            mock_image,
            lang='eng',
            config='',
            output_type=pytesseract.Output.DICT
        )
    
    @patch('src.parsers.ocr_parser.pytesseract.image_to_data')
    def test_extract_data_tesseract_error(self, mock_image_to_data):
        """Test data extraction handles Tesseract errors"""
        parser = TesseractOCRParser()
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (100, 100)
        mock_image_to_data.side_effect = pytesseract.TesseractError(1, "Failed")
        
        with pytest.raises(OCRError, match="OCR data extraction failed"):
            parser.extract_data(mock_image)


class TestExtractTextWithConfidence:
    """Test extract_text_with_confidence method"""
    
    @patch.object(TesseractOCRParser, 'extract_data')
    def test_extract_text_with_confidence_no_filter(self, mock_extract_data):
        """Test extracting text with confidence scores"""
        parser = TesseractOCRParser()
        
        mock_extract_data.return_value = {
            'text': ['Hello', '', 'World', 'Test'],
            'conf': ['95', '-1', '88', '75'],
            'left': [10, 0, 50, 90],
            'top': [10, 0, 10, 10],
            'width': [30, 0, 40, 35],
            'height': [15, 0, 15, 15]
        }
        
        result = parser.extract_text_with_confidence(Mock(spec=Image.Image))
        
        assert result['full_text'] == 'Hello World Test'
        assert result['total_words'] == 3
        assert len(result['words']) == 3
        assert result['words'][0]['text'] == 'Hello'
        assert result['words'][0]['confidence'] == 95
        assert result['words'][0]['bbox']['left'] == 10
        assert abs(result['avg_confidence'] - 86.0) < 0.1
    
    @patch.object(TesseractOCRParser, 'extract_data')
    def test_extract_text_with_confidence_min_filter(self, mock_extract_data):
        """Test extracting text with minimum confidence filter"""
        parser = TesseractOCRParser()
        
        mock_extract_data.return_value = {
            'text': ['Hello', 'World', 'Test'],
            'conf': ['95', '88', '50'],
            'left': [10, 50, 90],
            'top': [10, 10, 10],
            'width': [30, 40, 35],
            'height': [15, 15, 15]
        }
        
        result = parser.extract_text_with_confidence(
            Mock(spec=Image.Image),
            min_confidence=80
        )
        
        assert result['full_text'] == 'Hello World'
        assert result['total_words'] == 2
        assert len(result['words']) == 2
        assert abs(result['avg_confidence'] - 91.5) < 0.1
    
    @patch.object(TesseractOCRParser, 'extract_data')
    def test_extract_text_with_confidence_empty_result(self, mock_extract_data):
        """Test extracting text when all words filtered out"""
        parser = TesseractOCRParser()
        
        mock_extract_data.return_value = {
            'text': ['Low', 'Quality'],
            'conf': ['30', '40'],
            'left': [10, 50],
            'top': [10, 10],
            'width': [30, 40],
            'height': [15, 15]
        }
        
        result = parser.extract_text_with_confidence(
            Mock(spec=Image.Image),
            min_confidence=90
        )
        
        assert result['full_text'] == ''
        assert result['total_words'] == 0
        assert len(result['words']) == 0
        assert result['avg_confidence'] == 0


class TestOCRError:
    """Test OCRError exception"""
    
    def test_ocr_error_is_exception(self):
        """Test OCRError is an Exception"""
        error = OCRError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
