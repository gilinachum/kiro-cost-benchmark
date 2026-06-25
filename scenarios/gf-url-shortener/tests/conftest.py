import sys
import os
import pytest

# Add parent directory to path so 'shortener' module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def clean_state():
    """Reset shortener state between tests."""
    import shortener
    # Clear internal storage
    with shortener._lock:
        shortener._url_to_code.clear()
        shortener._code_to_url.clear()
    yield
