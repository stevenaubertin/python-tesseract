"""
Pytest configuration file

Provides fixtures and configuration for the test suite.
"""
import pytest
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture(scope="session")
def tesseract_available():
    """Check if Tesseract is available"""
    import shutil
    return shutil.which('tesseract') is not None


@pytest.fixture(scope="session")
def test_pdf_available():
    """Check if test PDF file is available"""
    return Path("data/SO-90328.pdf").exists()


@pytest.fixture(scope="session")
def test_image_available():
    """Check if test image file is available"""
    return Path("data/test_output-000001.ppm").exists()
