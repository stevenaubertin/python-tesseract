"""
Example: PDF to Image Conversion

This example shows how to use the PDF service independently
to convert PDFs to images.
"""
from pathlib import Path
from src.services.pdf_service import PDFToImageService


def main():
    """Demonstrate PDF to image conversion."""
    
    # Initialize PDF service
    service = PDFToImageService(
        poppler_path=None,  # Set if poppler is not in PATH
        dpi=300
    )
    
    pdf_path = "sample.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Please provide a PDF file: {pdf_path}")
        return
    
    # Example 1: Convert all pages
    print("=" * 60)
    print("Example 1: Convert all PDF pages to images")
    print("=" * 60)
    
    try:
        images = service.convert_pdf_to_images(pdf_path)
        print(f"\nConverted {len(images)} pages")
        
        for i, img in enumerate(images, start=1):
            print(f"  Page {i}: {img.size} ({img.mode})")
        
        # Save images to disk
        output_dir = Path("output")
        saved_paths = service.save_images(
            images,
            output_dir,
            base_name="page",
            format="PNG"
        )
        
        print(f"\nSaved {len(saved_paths)} images to {output_dir}/")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Convert specific page
    print("\n" + "=" * 60)
    print("Example 2: Convert single page")
    print("=" * 60)
    
    try:
        image = service.convert_single_page(pdf_path, page_number=1)
        print(f"\nConverted page 1: {image.size} ({image.mode})")
        
        # Save single image
        output_path = Path("output") / "page_1.png"
        output_path.parent.mkdir(exist_ok=True)
        image.save(output_path, "PNG")
        print(f"Saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Convert page range
    print("\n" + "=" * 60)
    print("Example 3: Convert page range (2-4)")
    print("=" * 60)
    
    try:
        images = service.convert_pdf_to_images(
            pdf_path,
            first_page=2,
            last_page=4
        )
        print(f"\nConverted {len(images)} pages (2-4)")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
