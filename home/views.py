from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class BlogView(APIView):
    def get(self, request):
        # authentication_classes = [JWTAuthentication]
        # permission_classes = [IsAuthenticated]

        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response({
            "message":True,
            "data":serializer.data
        }, status.HTTP_200_OK)
    
class TagView(APIView):
    def get(self,request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response({
            "message":True,
            "data":serializer.data
        },status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data 
        serializer = TagSerializer(data=data)
        if not serializer.is_valid():
            return Response({
            "message":True,
            "data":serializer.errors
            })
        tag = Tag.objects.create(tag=serializer.data['tag'])
        tag.save()
        return Response({
            "message":True,
            "data":{}
        },status.HTTP_201_CREATED)
    

class CategoryView(APIView):
    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        print(serializer.data)

        return Response({
            "message":True,
            "data":serializer.data
        },status.HTTP_200_OK)
    
    def post(self,request):
        data = request.data 
        serializer = CategorySerializer(data=data)
        if not serializer.is_valid():
            return Response({
            "message":True,
            "data":serializer.errors
            })
        category = Category.objects.create(tag=serializer.data['category'])
        category.save()
        return Response({
            "message":True,
            "data":{}
        },status.HTTP_201_CREATED)



