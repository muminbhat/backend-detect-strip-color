from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Sample
from .serializers import SampleSerializer
import cv2
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from .models import Sample
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser


# List all samples
@api_view(['GET'])
def sample_list(request):
    items = Sample.objects.all()
    serializer = SampleSerializer(items, many=True)
    return Response(serializer.data)


# Create Sample
@api_view(['POST'])
@parser_classes((MultiPartParser, FormParser))
def create_sample(request):
    serializer = SampleSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST,)

@api_view(['GET', 'POST'])
def sample_detail(request, sample_id):
    try:
        sample = Sample.objects.get(pk=sample_id)
    except Sample.DoesNotExist:
        return Response({'message': 'Sample not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SampleSerializer(sample)
        return Response(serializer.data)

    elif request.method == 'POST':
        analysis_results = process_image(sample.sample_image)  # Replace with your image processing logic
        sample.analysis_results = analysis_results
        sample.save()
        serializer = SampleSerializer(sample)
        return Response(serializer.data)

# Image Process
def process_image(sample_image):
    try:
        # Read the uploaded image using OpenCV
        img = cv2.imdecode(np.fromstring(sample_image.read(), np.uint8), cv2.IMREAD_COLOR)

        # Convert the image to RGB (if it's in BGR format)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Perform color analysis
        # For example, you can use k-means clustering to identify dominant colors
        pixels = img_rgb.reshape((-1, 3))
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        k = 10  # Number of colors to identify
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Get the unique colors (centers)
        unique_colors = np.uint8(centers)

        # Convert unique colors to a list of RGB values
        rgb_colors = unique_colors.tolist()

        return rgb_colors

    except Exception as e:
        raise Exception(f"Image processing error: {str(e)}")

# Result List
@api_view(['GET'])
def analyze_strip(request, sample_id):
    try:
        # Get the sample from the database
        sample = Sample.objects.get(pk=sample_id)

        # Process the uploaded image
        analyzed_colors = process_image(sample.sample_image)

        # Ensure that the response contains exactly 10 colors
        if len(analyzed_colors) != 10:
            return Response({'error': 'Image does not contain 10 distinct colors'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the JSON response
        response_data = {
            'colors': analyzed_colors,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Sample.DoesNotExist:
        return Response({'error': 'Sample not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)