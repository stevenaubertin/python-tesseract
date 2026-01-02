"""
Example: Basic OCR usage with python-tesseract

This example shows how to use the OCR pipeline to extract text from images and PDFs.
"""
from pathlib import Path
from src.parsers.ocr_pipeline import OCRPipeline


def main():
    """Demonstrate basic OCR functionality."""
    
    # Initialize the OCR pipeline
    # On Windows, you may need to specify tesseract path:
    pipeline = OCRPipeline(
        tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        tessdata_prefix=r'C:\Program Files\Tesseract-OCR\tessdata',
        dpi=300,
        lang='eng'
    )
    
    # Example 1: Extract text from an image
    print("=" * 60)
    print("Example 1: Extract text from image")
    print("=" * 60)
    
    image_path = "sample.png"
    if Path(image_path).exists():
        text = pipeline.process_image(image_path)
        print(f"\nExtracted text:\n{text}\n")
    else:
        print(f"Image not found: {image_path}\n")
    
    # Example 2: Extract text with confidence filtering
    print("=" * 60)
    print("Example 2: Extract text with confidence threshold")
    print("=" * 60)
    
    if Path(image_path).exists():
        result = pipeline.process_image(image_path, min_confidence=80.0)
        print(f"\nFull text: {result['full_text']}")
        print(f"Average confidence: {result['avg_confidence']:.2f}%")
        print(f"Total words: {result['total_words']}\n")
        
        # Show first 5 words with their confidence scores
        print("First 5 words with confidence:")
        for word in result['words'][:5]:
            print(f"  '{word['text']}' - {word['confidence']}%")
    
    # Example 3: Process PDF (single page)
    print("\n" + "=" * 60)
    print("Example 3: Extract text from PDF page")
    print("=" * 60)
    
    pdf_path = "sample.pdf"
    if Path(pdf_path).exists():
        text = pipeline.process_pdf(pdf_path, page_number=1)
        print(f"\nPage 1 text:\n{text}\n")
    else:
        print(f"PDF not found: {pdf_path}\n")
    
    # Example 4: Process all PDF pages
    print("=" * 60)
    print("Example 4: Extract text from all PDF pages")
    print("=" * 60)
    
    if Path(pdf_path).exists():
        pages = pipeline.process_pdf(pdf_path)
        for i, page_text in enumerate(pages, start=1):
            print(f"\n--- Page {i} ---")
            print(page_text[:200] + "..." if len(page_text) > 200 else page_text)
    
    # Example 5: Auto-detect file type
    print("\n" + "=" * 60)
    print("Example 5: Auto-detect and process file")
    print("=" * 60)
    
    file_path = "document.pdf"  # or "image.png"
    if Path(file_path).exists():
        result = pipeline.process(file_path)
        if isinstance(result, list):
            print(f"Processed {len(result)} pages")
        else:
            print(f"Extracted text: {result[:100]}...")
    else:
        print(f"File not found: {file_path}\n")


if __name__ == "__main__":
    main()
