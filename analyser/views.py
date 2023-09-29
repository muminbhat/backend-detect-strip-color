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


# Image Process
def process_image(image):
    try:
        # Read the uploaded image using OpenCV
        img = cv2.imdecode(np.fromstring(
            image.read(), np.uint8), cv2.IMREAD_COLOR)

        # Convert the image to RGB (if it's in BGR format)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Perform color analysis
        # For example, you can use k-means clustering to identify dominant colors
        pixels = img_rgb.reshape((-1, 3))
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        k = 10  # Number of colors to identify
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Get the unique colors (centers)
        unique_colors = np.uint8(centers)

        # Convert unique colors to a list of RGB values
        rgb_colors = unique_colors.tolist()

        return rgb_colors

    except Exception as e:
        raise Exception(f"Image processing error: {str(e)}")

# Result List


@api_view(['GET', 'POST'])
def analyze_sample(request, sample_id):
    if request.method == 'POST':
        # Get the sample by ID
        try:
            sample = Sample.objects.get(pk=sample_id)
        except Sample.DoesNotExist:
            return Response({'message': 'Sample not found'}, status=404)

        # Process the image
        analysis_results = process_image(sample.strip_image)  # Replace with your image processing logic

        # Update the Sample model with analysis results
        sample.analysis_results = analysis_results
        sample.save()

        return Response({'message': 'Analysis completed successfully'})

    elif request.method == 'GET':
        # Retrieve and return analysis results for the sample
        try:
            sample = Sample.objects.get(pk=sample_id)
        except Sample.DoesNotExist:
            return Response({'message': 'Sample not found'}, status=404)

        analysis_results = sample.analysis_results

        return Response({'analysis_results': analysis_results})
