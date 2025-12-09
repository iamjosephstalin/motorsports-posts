import pytest
from unittest.mock import patch, MagicMock
import os
from studio import Studio

class TestStudio:
    @pytest.fixture
    def studio(self, tmp_path):
        # Use a temporary directory for output
        s = Studio()
        s.output_path = str(tmp_path)
        return s

    @patch('requests.get')
    @patch('PIL.Image.open')
    def test_generate_image(self, mock_open, mock_get, studio, mock_news_item):
        # Mock requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fakeimagebytes"
        mock_get.return_value = mock_response

        # Mock Image.open to return a dummy image
        mock_img = MagicMock()
        mock_img.size = (1000, 1000)
        mock_img.width = 1000
        mock_img.height = 1000
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        mock_img.crop.return_value = mock_img
        
        # Determine behavior for context manager (scout.download_image)
        # Actually studio.download_image writes to file, so we mock that too or just the requests part.
        # studio.generate_image calls self.download_image
        
        # Let's mock download_image directly to avoid file I/O complexity for unit test
        with patch.object(studio, 'download_image', return_value="dummy_path.jpg") as mock_download:
             # Mock Image.open to load the "dummy_path"
             mock_open.return_value = mock_img
             
             output_path = studio.generate_image(mock_news_item)
             
             assert output_path is not None
             assert os.path.basename(output_path).startswith("post_")
             # assert file created? - In this mock setup, we are mocking save likely if we want full isolation,
             # but `img.save` is a method on the PIL object. 
             mock_img.save.assert_called()

    def test_resize_logic(self, studio):
        # Test the math for resizing
        # Create a real small image
        from PIL import Image
        img = Image.new('RGB', (100, 200))
        
        # Case 1: Target is wider
        resized = studio._resize_and_crop(img, 200, 200)
        assert resized.size == (200, 200)
