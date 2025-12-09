import pytest
from unittest.mock import patch, MagicMock
from scout import Scout

class TestScout:
    @pytest.fixture
    def scout(self):
        return Scout()

    @patch('feedparser.parse')
    def test_fetch_news(self, mock_parse, scout, sample_rss_entry):
        # Mock the feed data
        mock_feed = MagicMock()
        mock_feed.entries = [sample_rss_entry]
        mock_parse.return_value = mock_feed

        news = scout.fetch_news()
        
        assert len(news) == 2 # 2 feeds * 1 item each (mocked same for both)
        assert news[0]['headline_en'] == "Max Verstappen wins again"
        assert news[0]['image_url'] == "http://example.com/max.jpg"

    def test_translate_headline(self, scout):
        original = "Hello World"
        translated = scout.translate_headline(original)
        assert translated == "[TA] Hello World"
