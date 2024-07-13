from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from accounts.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework import generics

class UserView(generics.ListAPIView):
    serializer_class= UserSerializer
    
    def get_queryset(self):
        #select 5 users who is active
        return CustomUser.objects.filter(is_active=True,is_staff=False,is_verified=True).order_by('?')[:5]

class CategoryBlogListView(generics.ListAPIView):
    serializer_class = HomeBlogSerializer
    
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Blog.objects.filter(published=True,category_id=category_id)
    
class RecentBlogListView(generics.ListAPIView):
    serializer_class = RecentBlogSerializer
    
    def get_queryset(self):
        return Blog.objects.order_by('-created_at')[:4]  # recent blogs

class BlogView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request,slug=None):
        #return blog along with comments
        try:
            blog = Blog.objects.get(slug=slug)
            blog_serializer = BlogSerializer(blog)
            return Response({
                    "status":True,
                    "data":{
                    "blog":blog_serializer.data,
            }},status.HTTP_200_OK)
                
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self,request,*args, **kwargs):
        serializer = BlogSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                    'status':False,
                    'message':serializer.errors,
                    'verified':True
                }, status.HTTP_400_BAD_REQUEST)
        blog = serializer.save()
        BlogId = blog.uid
        return Response({
            "status":True,
            'message':'blog created',
            'BlogId':BlogId
        },status=status.HTTP_201_CREATED)
        
    
    def patch(self,request,id=None):
        #updates the blog
        try:
            blog=Blog.objects.get(uid=id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            updated_blog = serializer.save()
            return Response({'slug': updated_blog.slug, 'message': 'Blog updated successfully!'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,slug=None):
        try:
            blog = Blog.objects.get(slug=slug)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

        blog.delete()
        return Response({'message': 'Blog deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
    
class TagView(APIView):
    def get(self,request):
        random_tags = Tag.objects.order_by('?')[:5]  # Fetch 5 random tags from the database
        serializer = TagSerializer(random_tags, many=True)
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

class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        image_file = request.data.get('image')

        if image_file:
            uploaded_image = UploadedImage.objects.create(image=image_file)
            image_url = request.build_absolute_uri(uploaded_image.image.url)
            return Response({'imageUrl': image_url}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)