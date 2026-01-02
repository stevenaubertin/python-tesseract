"""
Example: Advanced OCR with detailed data extraction

This example shows advanced features like extracting bounding boxes,
confidence scores, and detailed OCR data.
"""
from pathlib import Path
from src.parsers.ocr_pipeline import OCRPipeline


def main():
    """Demonstrate advanced OCR features."""
    
    # Initialize pipeline
    pipeline = OCRPipeline(
        tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        tessdata_prefix=r'C:\Program Files\Tesseract-OCR\tessdata',
        dpi=300,
        lang='eng'
    )
    
    image_path = "sample.png"
    
    if not Path(image_path).exists():
        print(f"Please provide an image: {image_path}")
        return
    
    # Extract detailed OCR data
    print("=" * 60)
    print("Extracting detailed OCR data...")
    print("=" * 60)
    
    data = pipeline.process_image(image_path, extract_data=True)
    
    # Analyze the data
    print(f"\nTotal elements detected: {len(data['text'])}")
    
    # Filter non-empty text elements
    valid_elements = [
        (text, conf, left, top, width, height)
        for text, conf, left, top, width, height in zip(
            data['text'], data['conf'], 
            data['left'], data['top'],
            data['width'], data['height']
        )
        if text.strip() and int(conf) > 0
    ]
    
    print(f"Valid text elements: {len(valid_elements)}")
    
    # Show elements with their positions
    print("\nText elements with positions:")
    for text, conf, left, top, width, height in valid_elements[:10]:
        print(f"  '{text}' @ ({left}, {top}) [{width}x{height}] - {conf}% confidence")
    
    # Extract words with high confidence
    print("\n" + "=" * 60)
    print("High-confidence words (>90%):")
    print("=" * 60)
    
    result = pipeline.process_image(image_path, min_confidence=90.0)
    
    print(f"\nTotal high-confidence words: {result['total_words']}")
    print(f"Average confidence: {result['avg_confidence']:.2f}%")
    
    # Group words by line (approximate based on y-coordinate)
    words_by_line = {}
    for word_data in result['words']:
        y_pos = word_data['bbox']['top']
        line_key = y_pos // 20  # Group words within 20 pixels
        
        if line_key not in words_by_line:
            words_by_line[line_key] = []
        
        words_by_line[line_key].append(word_data)
    
    # Print words grouped by line
    print("\nWords grouped by line:")
    for line_key in sorted(words_by_line.keys()):
        words = words_by_line[line_key]
        line_text = ' '.join(w['text'] for w in words)
        avg_conf = sum(w['confidence'] for w in words) / len(words)
        print(f"  Line {line_key}: {line_text} ({avg_conf:.1f}%)")


if __name__ == "__main__":
    main()
