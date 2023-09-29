from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Sample
from .serializers import SampleSerializer

@api_view(['GET'])
def sample_list(request):
    items = Sample.objects.all()
    serializer = SampleSerializer(items, many=True)
    return Response(serializer.data)