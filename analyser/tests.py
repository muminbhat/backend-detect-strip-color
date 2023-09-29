from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings  # Import Django's settings

# Create your tests here.
class ImageAnalysisTestCase(TestCase):
    def test_analyze_strip(self):
        # Create a test image file
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"image_content",
            content_type="image/jpeg"
        )

        # Make a POST request to the view with the test image
        response = self.client.post('/api/analyser/process/', {'strip_image': image})

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response contains 10 colors (customize this based on your implementation)
        data = response.json()
        self.assertEqual(len(data['colors']), 10)