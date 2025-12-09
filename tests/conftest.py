import pytest
import os
import sys

# Add project root to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_news_item():
    return {
        "id": "test_id_123",
        "headline_en": "Test Headline",
        "headline_ta": "[TA] Test Headline",
        "image_url": "http://example.com/image.jpg",
        "link": "http://example.com/news/123",
        "type": "news",
        "source": "RSS"
    }

@pytest.fixture
def sample_rss_entry():
    class Entry:
        def __init__(self):
            self.title = "Max Verstappen wins again"
            self.link = "http://example.com/f1/max-wins"
            self.id = "http://example.com/f1/max-wins"
            self.media_content = [{'url': 'http://example.com/max.jpg'}]
    return Entry()
