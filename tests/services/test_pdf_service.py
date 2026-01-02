"""
Tests for PDFToImageService

Tests PDF to image conversion functionality.
"""
import pytest
from pathlib import Path
from PIL import Image
import tempfile
import os

from src.services.pdf_service import PDFToImageService, PDFConversionError


class TestPDFToImageService:
    """Test suite for PDFToImageService"""
    
    @pytest.fixture
    def service(self):
        """Create a PDFToImageService instance"""
        return PDFToImageService(dpi=150)  # Lower DPI for faster tests
    
    @pytest.fixture
    def service_with_poppler(self):
        """Create a PDFToImageService instance with poppler path"""
        # Adjust poppler path if available in your environment
        return PDFToImageService(dpi=150, poppler_path=None)
    
    def test_initialization_default(self):
        """Test service initialization with default parameters"""
        service = PDFToImageService()
        assert service.dpi == 300
        assert service.poppler_path is None
    
    def test_initialization_custom_dpi(self):
        """Test service initialization with custom DPI"""
        service = PDFToImageService(dpi=150)
        assert service.dpi == 150
    
    def test_initialization_with_poppler_path(self):
        """Test service initialization with poppler path"""
        poppler_path = r'C:\poppler\bin'
        service = PDFToImageService(poppler_path=poppler_path)
        assert service.poppler_path == poppler_path
    
    def test_convert_pdf_file_not_found(self, service):
        """Test that FileNotFoundError is raised for non-existent PDF"""
        with pytest.raises(FileNotFoundError) as exc_info:
            service.convert_pdf_to_images("nonexistent.pdf")
        assert "PDF file not found" in str(exc_info.value)
    
    def test_convert_single_page_file_not_found(self, service):
        """Test that FileNotFoundError is raised for non-existent PDF"""
        with pytest.raises(FileNotFoundError) as exc_info:
            service.convert_single_page("nonexistent.pdf", page_number=1)
        assert "PDF file not found" in str(exc_info.value)
    
    @pytest.mark.skipif(
        not Path("SO-90328.pdf").exists(),
        reason="Test PDF file not available"
    )
    def test_convert_pdf_to_images_returns_error_old_poppler(self, service):
        """Test PDF conversion with old poppler (expected to fail gracefully)"""
        # This test expects to fail due to old Poppler version
        with pytest.raises(PDFConversionError) as exc_info:
            service.convert_pdf_to_images("SO-90328.pdf")
        assert "No pages extracted" in str(exc_info.value)
    
    @pytest.mark.skipif(
        not Path("SO-90328.pdf").exists(),
        reason="Test PDF file not available"
    )
    def test_convert_single_page_returns_error_old_poppler(self, service):
        """Test single page conversion with old poppler"""
        with pytest.raises(PDFConversionError) as exc_info:
            service.convert_single_page("SO-90328.pdf", page_number=1)
        assert "No pages extracted" in str(exc_info.value)
    
    def test_save_images(self, service):
        """Test saving images to disk"""
        # Create test images
        test_images = [
            Image.new('RGB', (100, 100), color='red'),
            Image.new('RGB', (100, 100), color='blue')
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            
            # Save images
            saved_paths = service.save_images(
                test_images,
                output_dir,
                base_name="test",
                format="PNG"
            )
            
            # Verify
            assert len(saved_paths) == 2
            assert all(p.exists() for p in saved_paths)
            assert saved_paths[0].name == "test_001.png"
            assert saved_paths[1].name == "test_002.png"
            
            # Verify images can be loaded and close them
            img1 = Image.open(saved_paths[0])
            assert img1.size == (100, 100)
            img1.close()  # Close the image to release file handle
    
    def test_save_images_creates_directory(self, service):
        """Test that save_images creates output directory if it doesn't exist"""
        test_images = [Image.new('RGB', (50, 50), color='green')]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "new_subdir"
            assert not output_dir.exists()
            
            saved_paths = service.save_images(
                test_images,
                output_dir,
                base_name="page"
            )
            
            assert output_dir.exists()
            assert len(saved_paths) == 1
    
    def test_save_images_different_formats(self, service):
        """Test saving images in different formats"""
        test_image = [Image.new('RGB', (100, 100), color='white')]
        
        formats = ['PNG', 'JPEG', 'BMP']
        
        for fmt in formats:
            with tempfile.TemporaryDirectory() as tmpdir:
                saved_paths = service.save_images(
                    test_image,
                    tmpdir,
                    base_name="img",
                    format=fmt
                )
                
                assert saved_paths[0].suffix.lower() == f'.{fmt.lower()}'
                assert saved_paths[0].exists()
    
    def test_save_images_empty_list(self, service):
        """Test saving empty list of images"""
        with tempfile.TemporaryDirectory() as tmpdir:
            saved_paths = service.save_images(
                [],
                tmpdir,
                base_name="test"
            )
            
            assert len(saved_paths) == 0


class TestPDFConversionError:
    """Test PDFConversionError exception"""
    
    def test_exception_message(self):
        """Test exception can be raised with message"""
        with pytest.raises(PDFConversionError) as exc_info:
            raise PDFConversionError("Test error message")
        
        assert "Test error message" in str(exc_info.value)
    
    def test_exception_inheritance(self):
        """Test that PDFConversionError is an Exception"""
        assert issubclass(PDFConversionError, Exception)
