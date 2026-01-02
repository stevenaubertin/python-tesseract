"""
Unit tests for PDFToImageService using mocks

These tests complement the integration tests in test_pdf_service.py
by testing the logic in isolation using mocks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PIL import Image

from src.services.pdf_service import PDFToImageService, PDFConversionError


class TestPDFToImageServiceInit:
    """Test PDFToImageService initialization"""
    
    def test_init_default(self):
        """Test initialization with default parameters"""
        service = PDFToImageService()
        assert service.poppler_path is None
        assert service.dpi == 300
    
    def test_init_custom_dpi(self):
        """Test initialization with custom DPI"""
        service = PDFToImageService(dpi=600)
        assert service.dpi == 600
    
    def test_init_custom_poppler_path(self):
        """Test initialization with custom poppler path"""
        service = PDFToImageService(poppler_path='/usr/bin')
        assert service.poppler_path == '/usr/bin'


class TestConvertPDFToImages:
    """Test convert_pdf_to_images method"""
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_success(self, mock_convert, mock_exists):
        """Test successful PDF conversion"""
        mock_exists.return_value = True
        mock_images = [Mock(spec=Image.Image), Mock(spec=Image.Image)]
        mock_convert.return_value = mock_images
        
        service = PDFToImageService()
        result = service.convert_pdf_to_images('test.pdf')
        
        assert result == mock_images
        mock_convert.assert_called_once_with(
            'test.pdf',
            dpi=300,
            first_page=None,
            last_page=None,
            poppler_path=None
        )
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_with_page_range(self, mock_convert, mock_exists):
        """Test PDF conversion with page range"""
        mock_exists.return_value = True
        mock_images = [Mock(spec=Image.Image)]
        mock_convert.return_value = mock_images
        
        service = PDFToImageService()
        result = service.convert_pdf_to_images('test.pdf', first_page=2, last_page=4)
        
        assert result == mock_images
        mock_convert.assert_called_once_with(
            'test.pdf',
            dpi=300,
            first_page=2,
            last_page=4,
            poppler_path=None
        )
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_with_poppler_path(self, mock_convert, mock_exists):
        """Test PDF conversion with custom poppler path"""
        mock_exists.return_value = True
        mock_images = [Mock(spec=Image.Image)]
        mock_convert.return_value = mock_images
        
        service = PDFToImageService(poppler_path='/custom/path', dpi=600)
        result = service.convert_pdf_to_images('test.pdf')
        
        assert result == mock_images
        mock_convert.assert_called_once_with(
            'test.pdf',
            dpi=600,
            first_page=None,
            last_page=None,
            poppler_path='/custom/path'
        )
    
    @patch('src.services.pdf_service.Path.exists')
    def test_convert_pdf_file_not_found(self, mock_exists):
        """Test conversion of non-existent PDF raises FileNotFoundError"""
        mock_exists.return_value = False
        
        service = PDFToImageService()
        
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            service.convert_pdf_to_images('nonexistent.pdf')
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_no_pages_extracted(self, mock_convert, mock_exists):
        """Test conversion when no pages are extracted"""
        mock_exists.return_value = True
        mock_convert.return_value = []
        
        service = PDFToImageService()
        
        with pytest.raises(PDFConversionError, match="No pages extracted from PDF"):
            service.convert_pdf_to_images('test.pdf')
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_generic_error(self, mock_convert, mock_exists):
        """Test conversion handles generic errors"""
        mock_exists.return_value = True
        mock_convert.side_effect = Exception("Unexpected error")
        
        service = PDFToImageService()
        
        with pytest.raises(PDFConversionError, match="Failed to convert PDF"):
            service.convert_pdf_to_images('test.pdf')
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_pdf_reraises_conversion_error(self, mock_convert, mock_exists):
        """Test that PDFConversionError is re-raised as-is"""
        mock_exists.return_value = True
        mock_convert.return_value = []
        
        service = PDFToImageService()
        
        with pytest.raises(PDFConversionError):
            service.convert_pdf_to_images('test.pdf')


class TestConvertSinglePage:
    """Test convert_single_page method"""
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_single_page_success(self, mock_convert, mock_exists):
        """Test successful single page conversion"""
        mock_exists.return_value = True
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]
        
        service = PDFToImageService()
        result = service.convert_single_page('test.pdf', page_number=3)
        
        assert result is mock_image
        mock_convert.assert_called_once_with(
            'test.pdf',
            dpi=300,
            first_page=3,
            last_page=3,
            poppler_path=None
        )
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_single_page_default_page_1(self, mock_convert, mock_exists):
        """Test single page conversion defaults to page 1"""
        mock_exists.return_value = True
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]
        
        service = PDFToImageService()
        result = service.convert_single_page('test.pdf')
        
        assert result is mock_image
        mock_convert.assert_called_once_with(
            'test.pdf',
            dpi=300,
            first_page=1,
            last_page=1,
            poppler_path=None
        )
    
    @patch('src.services.pdf_service.Path.exists')
    @patch('src.services.pdf_service.convert_from_path')
    def test_convert_single_page_no_image(self, mock_convert, mock_exists):
        """Test single page conversion with no images returned"""
        mock_exists.return_value = True
        mock_convert.return_value = []
        
        service = PDFToImageService()
        
        with pytest.raises(PDFConversionError, match="No pages extracted from PDF"):
            service.convert_single_page('test.pdf', page_number=5)


class TestSaveImages:
    """Test save_images method"""
    
    @patch('src.services.pdf_service.Path.mkdir')
    def test_save_images_success(self, mock_mkdir):
        """Test successful saving of images"""
        mock_images = [Mock(spec=Image.Image), Mock(spec=Image.Image)]
        
        service = PDFToImageService()
        result = service.save_images(mock_images, 'output_dir')
        
        assert len(result) == 2
        assert str(result[0]).endswith('page_001.png')
        assert str(result[1]).endswith('page_002.png')
        assert mock_images[0].save.call_count == 1
        assert mock_images[1].save.call_count == 1
        mock_mkdir.assert_called_once()
    
    @patch('src.services.pdf_service.Path.mkdir')
    def test_save_images_custom_basename(self, mock_mkdir):
        """Test saving images with custom base name"""
        mock_images = [Mock(spec=Image.Image)]
        
        service = PDFToImageService()
        result = service.save_images(mock_images, 'output_dir', base_name='custom')
        
        assert len(result) == 1
        assert str(result[0]).endswith('custom_001.png')
        mock_images[0].save.assert_called_once()
    
    @patch('src.services.pdf_service.Path.mkdir')
    def test_save_images_custom_format(self, mock_mkdir):
        """Test saving images with custom format"""
        mock_images = [Mock(spec=Image.Image)]
        
        service = PDFToImageService()
        result = service.save_images(mock_images, 'output_dir', format='JPEG')
        
        assert len(result) == 1
        assert str(result[0]).endswith('page_001.jpeg')
        call_args = mock_images[0].save.call_args
        assert call_args[0][1] == 'JPEG'
    
    @patch('src.services.pdf_service.Path.mkdir')
    def test_save_images_creates_directory(self, mock_mkdir):
        """Test that output directory is created"""
        mock_images = [Mock(spec=Image.Image)]
        
        service = PDFToImageService()
        service.save_images(mock_images, 'new_output_dir')
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('src.services.pdf_service.Path.mkdir')
    def test_save_images_empty_list(self, mock_mkdir):
        """Test saving empty list of images"""
        service = PDFToImageService()
        result = service.save_images([], 'output_dir')
        
        assert result == []


class TestPDFConversionError:
    """Test PDFConversionError exception"""
    
    def test_pdf_conversion_error_is_exception(self):
        """Test PDFConversionError is an Exception"""
        error = PDFConversionError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
