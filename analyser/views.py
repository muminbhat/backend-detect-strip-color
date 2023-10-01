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
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.exceptions import SuspiciousFileOperation
import requests


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
        uploaded_image = cloudinary.uploader.upload(request.FILES['sample_image'])
        cloudinary_url = uploaded_image['url']
        sample = serializer.save(sample_image=cloudinary_url)
        sample.save()
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
        try:
            # Process the uploaded image
            analyzed_colors = process_image(sample.sample_image)

            # Ensure that the response contains exactly 10 colors
            if len(analyzed_colors) != 10:
                return Response({'error': 'Image does not contain 10 distinct colors'}, status=status.HTTP_400_BAD_REQUEST)

            # Store the Cloudinary image URL in the sample
            sample.sample_image = cloudinary_resource.url

            # Save the sample
            sample.save()

            # Update the analysis results
            sample.analysis_results = analyzed_colors
            sample.save()

            serializer = SampleSerializer(sample)
            return Response(serializer.data)

        except SuspiciousFileOperation:
            return Response({'error': 'Invalid file operation'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

import requests  # Make sure you import the requests library at the beginning of your Python file

# Image Process
def process_image(image_url):
    try:
        # Read the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content

        # Read the image using OpenCV
        img = cv2.imdecode(np.fromstring(image_data, np.uint8), cv2.IMREAD_COLOR)

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
        cloudinary_resource = sample.sample_image
        # Fetch the Cloudinary URL of the uploaded image
        cloudinary_url = cloudinary_resource.url
        # Process the Cloudinary image URL
        analyzed_colors = process_image(cloudinary_url)

        # Ensure that the response contains exactly 10 colors
        if len(analyzed_colors) != 10:
            return Response({'error': 'Image does not contain 10 distinct colors'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the analyzed colors in the sample's analysis_results field
        sample.analysis_results = analyzed_colors
        sample.save()

        # Prepare the JSON response
        response_data = {
            'colors': analyzed_colors,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Sample.DoesNotExist:
        return Response({'error': 'Sample not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

