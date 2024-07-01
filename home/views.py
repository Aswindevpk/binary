from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from accounts.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class BlogView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response({
            "status":True,
            "data":serializer.data
        }, status.HTTP_200_OK)
    
class TagView(APIView):
    def get(self,request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response({
            "status":True,
            "data":serializer.data
        },status.HTTP_200_OK)
    
class CategoryView(APIView):
    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response({
            "status":True,
            "data":serializer.data
        },status.HTTP_200_OK)

class BlogDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request,slug):
        blog = Blog.objects.get(slug=slug)
        comments = Comment.objects.filter(blog=blog)
        print(blog)
        blog_serializer = BlogSerializer(blog)

        comments_serializer = CommentSerializer(comments, many=True)
    
        return Response({
            "status":True,
            "data":{
                "blog":blog_serializer.data,
                "comments":comments_serializer.data
            }
        },status.HTTP_200_OK)

class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        id = request.data['id']
        user = CustomUser.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response({
            "status":True,
            "data":serializer.data
        },status.HTTP_200_OK)

class PlansView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
