from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Newsletter
from .serializers import NewsletterSerializer
from rest_framework import status


@api_view(['POST'])
def post_newsletter(request):
    if request.method == 'POST':
        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            
            # Check if an entry with the same email already exists
            if Newsletter.objects.filter(email=email).exists():
                return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            # Add the Access-Control-Allow-Origin header to allow requests from any origin
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response["Access-Control-Allow-Origin"] = "*"  # Replace with your desired origin
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['OPTIONS'])
def handle_preflight(request):
    response = Response()
    response["Access-Control-Allow-Origin"] = "http://127.0.0.1:3000"  # Replace with your React app's origin
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"  # Include the allowed HTTP methods
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # Include any required headers
    response["Access-Control-Allow-Credentials"] = "true"  # Allow credentials (cookies)
    return response