from django.shortcuts import render
from rest_framework.decorators import api_view 
from .models import * 
from .serializers import * 
from rest_framework.response import Response 
from rest_framework import status

# Create your views here.
@api_view(['Get'])
def get_moments(request, format=None):
    moments = Moment.objects.all()
    serializer = MomentSerializer(moments, many=True)
    return Response(serializer.data)

@api_view(['Get'])
def get_user_moments(request, pk, format=None):
    user_moments = Moment.objects.get_user_moments(user_id=pk)
    serializer = MomentSerializer(user_moments, many=True)
    return Response(serializer.data)

# @api_view(['Post'])
# def post_moment(request, pk, format=None):
#     serializer = MomentSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

