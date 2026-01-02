"""
Unit tests for OCRPipeline using mocks

These tests complement the integration tests in test_ocr_pipeline.py
by testing the logic in isolation using mocks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PIL import Image

from src.parsers.ocr_pipeline import OCRPipeline
from src.services.pdf_service import PDFConversionError
from src.parsers.ocr_parser import OCRError


class TestOCRPipelineInit:
    """Test OCRPipeline initialization"""
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_init_default(self, mock_parser, mock_service):
        """Test initialization with default parameters"""
        pipeline = OCRPipeline()
        
        mock_service.assert_called_once_with(poppler_path=None, dpi=300)
        mock_parser.assert_called_once_with(
            tesseract_cmd=None,
            tessdata_prefix=None,
            lang='eng'
        )
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_init_custom_parameters(self, mock_parser, mock_service):
        """Test initialization with custom parameters"""
        pipeline = OCRPipeline(
            tesseract_cmd='/usr/bin/tesseract',
            tessdata_prefix='/usr/share/tesseract',
            poppler_path='/usr/bin',
            dpi=600,
            lang='fra'
        )
        
        mock_service.assert_called_once_with(poppler_path='/usr/bin', dpi=600)
        mock_parser.assert_called_once_with(
            tesseract_cmd='/usr/bin/tesseract',
            tessdata_prefix='/usr/share/tesseract',
            lang='fra'
        )


class TestProcessImage:
    """Test process_image method"""
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_text_only(self, mock_parser_class, mock_service_class):
        """Test processing image and extracting text only"""
        mock_parser = Mock()
        mock_parser.extract_text.return_value = "Extracted text"
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        mock_image = Mock(spec=Image.Image)
        
        result = pipeline.process_image(mock_image, extract_data=False)
        
        assert result == "Extracted text"
        mock_parser.extract_text.assert_called_once_with(mock_image)
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_with_data(self, mock_parser_class, mock_service_class):
        """Test processing image and extracting detailed data"""
        mock_parser = Mock()
        mock_data = {'text': ['Hello'], 'conf': [95]}
        mock_parser.extract_data.return_value = mock_data
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        mock_image = Mock(spec=Image.Image)
        
        result = pipeline.process_image(mock_image, extract_data=True)
        
        assert result == mock_data
        mock_parser.extract_data.assert_called_once_with(mock_image)
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_with_confidence(self, mock_parser_class, mock_service_class):
        """Test processing image with confidence threshold"""
        mock_parser = Mock()
        mock_result = {
            'full_text': 'Hello World',
            'words': [{'text': 'Hello', 'confidence': 95}],
            'avg_confidence': 95.0,
            'total_words': 1
        }
        mock_parser.extract_text_with_confidence.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        mock_image = Mock(spec=Image.Image)
        
        result = pipeline.process_image(mock_image, min_confidence=80.0)
        
        assert result == mock_result
        mock_parser.extract_text_with_confidence.assert_called_once_with(
            mock_image,
            min_confidence=80.0
        )
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_file_not_found(self, mock_parser_class, mock_service_class):
        """Test processing non-existent image raises exception"""
        mock_parser = Mock()
        mock_parser.extract_text.side_effect = FileNotFoundError("Image not found")
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        
        with pytest.raises(FileNotFoundError):
            pipeline.process_image('nonexistent.png')
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_ocr_error(self, mock_parser_class, mock_service_class):
        """Test processing image with OCR error"""
        mock_parser = Mock()
        mock_parser.extract_text.side_effect = OCRError("OCR failed")
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        
        with pytest.raises(OCRError):
            pipeline.process_image(Mock(spec=Image.Image))


class TestProcessPDF:
    """Test process_pdf method"""
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_all_pages(self, mock_parser_class, mock_service_class):
        """Test processing all pages of a PDF"""
        mock_service = Mock()
        mock_images = [Mock(spec=Image.Image), Mock(spec=Image.Image)]
        mock_service.convert_pdf_to_images.return_value = mock_images
        mock_service_class.return_value = mock_service
        
        mock_parser = Mock()
        mock_parser.extract_text.side_effect = ["Page 1 text", "Page 2 text"]
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process_pdf('test.pdf')
        
        assert result == ["Page 1 text", "Page 2 text"]
        mock_service.convert_pdf_to_images.assert_called_once_with('test.pdf')
        assert mock_parser.extract_text.call_count == 2
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_single_page(self, mock_parser_class, mock_service_class):
        """Test processing single page of a PDF"""
        mock_service = Mock()
        mock_image = Mock(spec=Image.Image)
        mock_service.convert_single_page.return_value = mock_image
        mock_service_class.return_value = mock_service
        
        mock_parser = Mock()
        mock_parser.extract_text.return_value = "Page 3 text"
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process_pdf('test.pdf', page_number=3)
        
        assert result == "Page 3 text"
        mock_service.convert_single_page.assert_called_once_with('test.pdf', 3)
        mock_parser.extract_text.assert_called_once()
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_with_data(self, mock_parser_class, mock_service_class):
        """Test processing PDF with detailed data extraction"""
        mock_service = Mock()
        mock_images = [Mock(spec=Image.Image)]
        mock_service.convert_pdf_to_images.return_value = mock_images
        mock_service_class.return_value = mock_service
        
        mock_parser = Mock()
        mock_data = {'text': ['Hello'], 'conf': [95]}
        mock_parser.extract_data.return_value = mock_data
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process_pdf('test.pdf', extract_data=True)
        
        assert result == [mock_data]
        mock_parser.extract_data.assert_called_once()
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_with_confidence(self, mock_parser_class, mock_service_class):
        """Test processing PDF with confidence filtering"""
        mock_service = Mock()
        mock_images = [Mock(spec=Image.Image)]
        mock_service.convert_pdf_to_images.return_value = mock_images
        mock_service_class.return_value = mock_service
        
        mock_parser = Mock()
        mock_result = {'full_text': 'Hello', 'avg_confidence': 95.0}
        mock_parser.extract_text_with_confidence.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process_pdf('test.pdf', min_confidence=80.0)
        
        assert result == [mock_result]
        mock_parser.extract_text_with_confidence.assert_called_once()
    
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_conversion_error(self, mock_parser_class, mock_service_class):
        """Test processing PDF with conversion error"""
        mock_service = Mock()
        mock_service.convert_pdf_to_images.side_effect = PDFConversionError("Conversion failed")
        mock_service_class.return_value = mock_service
        
        pipeline = OCRPipeline()
        
        with pytest.raises(PDFConversionError):
            pipeline.process_pdf('test.pdf')


class TestProcess:
    """Test process method (auto-detection)"""
    
    @patch('src.parsers.ocr_pipeline.Path')
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_pdf_file(self, mock_parser_class, mock_service_class, mock_path_class):
        """Test auto-detecting and processing PDF file"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.suffix = '.pdf'
        mock_path_class.return_value = mock_path
        
        mock_service = Mock()
        mock_images = [Mock(spec=Image.Image)]
        mock_service.convert_pdf_to_images.return_value = mock_images
        mock_service_class.return_value = mock_service
        
        mock_parser = Mock()
        mock_parser.extract_text.return_value = "PDF text"
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process('test.pdf')
        
        assert result == ["PDF text"]
    
    @patch('src.parsers.ocr_pipeline.Path')
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_file(self, mock_parser_class, mock_service_class, mock_path_class):
        """Test auto-detecting and processing image file"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.suffix = '.png'
        mock_path_class.return_value = mock_path
        
        mock_parser = Mock()
        mock_parser.extract_text.return_value = "Image text"
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process('test.png')
        
        assert result == "Image text"
    
    @patch('src.parsers.ocr_pipeline.Path')
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_file_not_found(self, mock_parser_class, mock_service_class, mock_path_class):
        """Test processing non-existent file"""
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path
        
        pipeline = OCRPipeline()
        
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            pipeline.process('nonexistent.pdf')
    
    @patch('src.parsers.ocr_pipeline.Path')
    @patch('src.parsers.ocr_pipeline.PDFToImageService')
    @patch('src.parsers.ocr_pipeline.TesseractOCRParser')
    def test_process_image_ignores_page_number(self, mock_parser_class, mock_service_class, mock_path_class):
        """Test that page_number is ignored for image files"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.suffix = '.jpg'
        mock_path_class.return_value = mock_path
        
        mock_parser = Mock()
        mock_parser.extract_text.return_value = "Image text"
        mock_parser_class.return_value = mock_parser
        
        pipeline = OCRPipeline()
        result = pipeline.process('test.jpg', page_number=5)
        
        assert result == "Image text"
        mock_parser.extract_text.assert_called_once()
