"""
PDF to Image conversion service

Handles conversion of PDF documents to images using pdf2image library.
"""
from typing import List, Optional
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class PDFConversionError(Exception):
    """Raised when PDF conversion fails"""
    pass


class PDFToImageService:
    """Service for converting PDF documents to images"""
    
    def __init__(self, poppler_path: Optional[str] = None, dpi: int = 300):
        """
        Initialize PDF to Image service.
        
        Args:
            poppler_path: Path to poppler binaries (optional)
            dpi: Resolution for image conversion (default: 300)
        """
        self.poppler_path = poppler_path
        self.dpi = dpi
        logger.info(f"PDFToImageService initialized with DPI: {dpi}")
    
    def convert_pdf_to_images(
        self, 
        pdf_path: str | Path,
        first_page: Optional[int] = None,
        last_page: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Convert PDF to list of PIL Images.
        
        Args:
            pdf_path: Path to PDF file
            first_page: First page to convert (1-indexed, optional)
            last_page: Last page to convert (1-indexed, optional)
            
        Returns:
            List of PIL Image objects
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PDFConversionError: If conversion fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Converting PDF: {pdf_path} (pages {first_page or 'all'}-{last_page or 'all'})")
        
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                first_page=first_page,
                last_page=last_page,
                poppler_path=self.poppler_path
            )
            
            if not images:
                raise PDFConversionError(
                    f"No pages extracted from PDF. This usually means:\n"
                    f"  1. Poppler version is incompatible\n"
                    f"  2. PDF is corrupted or protected\n"
                    f"  3. Poppler binaries not properly configured"
                )
            
            logger.info(f"Successfully converted {len(images)} page(s)")
            return images
            
        except Exception as e:
            if isinstance(e, PDFConversionError):
                raise
            logger.error(f"PDF conversion failed: {e}")
            raise PDFConversionError(f"Failed to convert PDF: {e}") from e
    
    def convert_single_page(
        self, 
        pdf_path: str | Path,
        page_number: int = 1
    ) -> Image.Image:
        """
        Convert a single page of PDF to PIL Image.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number to convert (1-indexed)
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PDFConversionError: If conversion fails
        """
        images = self.convert_pdf_to_images(
            pdf_path, 
            first_page=page_number, 
            last_page=page_number
        )
        
        if not images:
            raise PDFConversionError(f"Failed to convert page {page_number}")
        
        return images[0]
    
    def save_images(
        self,
        images: List[Image.Image],
        output_dir: str | Path,
        base_name: str = "page",
        format: str = "PNG"
    ) -> List[Path]:
        """
        Save images to disk.
        
        Args:
            images: List of PIL Images
            output_dir: Output directory
            base_name: Base name for output files
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            List of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for idx, image in enumerate(images, start=1):
            output_path = output_dir / f"{base_name}_{idx:03d}.{format.lower()}"
            image.save(output_path, format.upper())
            saved_paths.append(output_path)
            logger.debug(f"Saved: {output_path}")
        
        logger.info(f"Saved {len(saved_paths)} image(s) to {output_dir}")
        return saved_paths
