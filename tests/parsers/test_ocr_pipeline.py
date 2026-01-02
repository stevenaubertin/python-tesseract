"""
Tests for OCRPipeline

Tests the main OCR orchestrator.
"""
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import tempfile
import os

from src.parsers.ocr_pipeline import OCRPipeline
from src.parsers.ocr_parser import OCRError
from src.services.pdf_service import PDFConversionError


# Tesseract configuration
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSDATA_PREFIX = r'C:\Program Files\Tesseract-OCR\tessdata'


class TestOCRPipeline:
    """Test suite for OCRPipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create an OCRPipeline instance"""
        return OCRPipeline(
            tesseract_cmd=TESSERACT_CMD,
            tessdata_prefix=TESSDATA_PREFIX,
            dpi=150,
            lang='eng'
        )
    
    @pytest.fixture
    def test_image_with_text(self):
        """Create a test image with text"""
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Test Document 123", fill='black')
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
        """Test pipeline initialization with default parameters"""
        pipeline = OCRPipeline()
        assert pipeline.pdf_service is not None
        assert pipeline.ocr_parser is not None
    
    def test_initialization_custom_params(self):
        """Test pipeline initialization with custom parameters"""
        pipeline = OCRPipeline(
            tesseract_cmd=TESSERACT_CMD,
            tessdata_prefix=TESSDATA_PREFIX,
            poppler_path=None,
            dpi=200,
            lang='eng'
        )
        
        assert pipeline.pdf_service.dpi == 200
        assert pipeline.ocr_parser.lang == 'eng'
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_image_from_pil(self, pipeline, test_image_with_text):
        """Test processing PIL Image object"""
        text = pipeline.process_image(test_image_with_text)
        
        assert isinstance(text, str)
        assert "Test" in text or "Document" in text or "123" in text
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_image_from_file(self, pipeline, test_image_file):
        """Test processing image file"""
        text = pipeline.process_image(test_image_file)
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_image_with_data(self, pipeline, test_image_with_text):
        """Test processing image with detailed data extraction"""
        data = pipeline.process_image(test_image_with_text, extract_data=True)
        
        assert isinstance(data, dict)
        assert 'text' in data
        assert 'conf' in data
        assert isinstance(data['text'], list)
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_image_with_confidence(self, pipeline, test_image_with_text):
        """Test processing image with confidence filtering"""
        result = pipeline.process_image(
            test_image_with_text,
            min_confidence=50.0
        )
        
        assert isinstance(result, dict)
        assert 'full_text' in result
        assert 'words' in result
        assert 'avg_confidence' in result
        assert 'total_words' in result
        
        # All words should meet confidence threshold
        for word in result['words']:
            assert word['confidence'] >= 50.0
    
    def test_process_image_file_not_found(self, pipeline):
        """Test that FileNotFoundError is raised for non-existent image"""
        with pytest.raises(FileNotFoundError):
            pipeline.process_image("nonexistent.png")
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    @pytest.mark.skipif(
        not Path("data/test_output-000001.ppm").exists(),
        reason="Test PPM file not available"
    )
    def test_process_real_image(self, pipeline):
        """Test processing real document image"""
        text = pipeline.process_image("data/test_output-000001.ppm")
        
        assert isinstance(text, str)
        assert len(text) > 100  # Should have substantial content
    
    def test_process_pdf_file_not_found(self, pipeline):
        """Test that FileNotFoundError is raised for non-existent PDF"""
        with pytest.raises(FileNotFoundError):
            pipeline.process_pdf("nonexistent.pdf")
    
    @pytest.mark.skipif(
        not Path("data/SO-90328.pdf").exists(),
        reason="Test PDF file not available"
    )
    def test_process_pdf_old_poppler(self, pipeline):
        """Test PDF processing with old poppler (expected to fail)"""
        # This test expects PDFConversionError due to old Poppler
        with pytest.raises(PDFConversionError):
            pipeline.process_pdf("data/SO-90328.pdf", page_number=1)
    
    @pytest.mark.skipif(
        not Path("data/SO-90328.pdf").exists(),
        reason="Test PDF file not available"
    )
    def test_process_pdf_all_pages_old_poppler(self, pipeline):
        """Test processing all PDF pages with old poppler"""
        with pytest.raises(PDFConversionError):
            pipeline.process_pdf("data/SO-90328.pdf")
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_auto_detect_image(self, pipeline, test_image_file):
        """Test auto-detection of image file type"""
        text = pipeline.process(test_image_file)
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    @pytest.mark.skipif(
        not Path("data/SO-90328.pdf").exists(),
        reason="Test PDF file not available"
    )
    def test_process_auto_detect_pdf(self, pipeline):
        """Test auto-detection of PDF file type"""
        # Expected to fail with old Poppler
        with pytest.raises(PDFConversionError):
            pipeline.process("data/SO-90328.pdf")
    
    def test_process_file_not_found(self, pipeline):
        """Test auto-detect with non-existent file"""
        with pytest.raises(FileNotFoundError):
            pipeline.process("nonexistent.xyz")
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_process_with_all_options(self, pipeline, test_image_file):
        """Test process with all optional parameters"""
        result = pipeline.process(
            test_image_file,
            extract_data=False,
            page_number=None,  # Ignored for images
            min_confidence=60.0
        )
        
        assert isinstance(result, dict)
        assert 'total_words' in result
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_confidence_threshold_variations(self, pipeline, test_image_with_text):
        """Test different confidence thresholds"""
        # Low threshold
        result_low = pipeline.process_image(
            test_image_with_text,
            min_confidence=30.0
        )
        
        # High threshold
        result_high = pipeline.process_image(
            test_image_with_text,
            min_confidence=90.0
        )
        
        # Low threshold should have more or equal words
        assert result_low['total_words'] >= result_high['total_words']
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_extract_data_mode(self, pipeline, test_image_with_text):
        """Test extract_data mode returns raw OCR data"""
        data = pipeline.process_image(
            test_image_with_text,
            extract_data=True
        )
        
        # Should return raw Tesseract data structure
        assert isinstance(data, dict)
        assert 'text' in data
        assert 'conf' in data
        assert 'left' in data
        assert 'top' in data
        assert 'width' in data
        assert 'height' in data
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists(),
        reason="Tesseract not installed"
    )
    def test_multiple_operations(self, pipeline, test_image_file):
        """Test multiple operations on same pipeline instance"""
        # First operation
        text1 = pipeline.process_image(test_image_file)
        assert isinstance(text1, str)
        
        # Second operation
        result2 = pipeline.process_image(
            test_image_file,
            min_confidence=50.0
        )
        assert isinstance(result2, dict)
        
        # Third operation
        data3 = pipeline.process_image(
            test_image_file,
            extract_data=True
        )
        assert isinstance(data3, dict)


class TestOCRPipelineIntegration:
    """Integration tests for OCRPipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create an OCRPipeline instance"""
        return OCRPipeline(
            tesseract_cmd=TESSERACT_CMD,
            tessdata_prefix=TESSDATA_PREFIX
        )
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists() or not Path("data/test_output-000001.ppm").exists(),
        reason="Tesseract or test file not available"
    )
    def test_end_to_end_image_processing(self, pipeline):
        """Test complete workflow: image file -> text extraction"""
        # Process image
        text = pipeline.process("data/test_output-000001.ppm")
        
        # Verify result
        assert isinstance(text, str)
        assert len(text) > 0
        
        # Should contain expected content
        assert any(word in text for word in ["Vergers", "commande", "Total"])
    
    @pytest.mark.skipif(
        not Path(TESSERACT_CMD).exists() or not Path("data/test_output-000001.ppm").exists(),
        reason="Tesseract or test file not available"
    )
    def test_end_to_end_with_confidence_filter(self, pipeline):
        """Test complete workflow with confidence filtering"""
        # Process with high confidence threshold
        result = pipeline.process(
            "data/test_output-000001.ppm",
            min_confidence=80.0
        )
        
        # Verify result
        assert isinstance(result, dict)
        assert result['total_words'] > 0
        assert result['avg_confidence'] >= 80.0
        
        # All words should meet threshold
        for word in result['words']:
            assert word['confidence'] >= 80.0
