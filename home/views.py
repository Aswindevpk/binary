from django.forms import ValidationError
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from accounts.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

class ListArticleView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self,request):
        topic = request.GET.get('topic')
        if topic:
            articles = Article.objects.filter(topics__name=topic).distinct()
        else:
          articles = Article.objects.all()

        serializer = ListArticleSerializer(articles,many=True)
        return Response({
                    "status":True,
                    "data":serializer.data
                    },status.HTTP_200_OK)
    
    def post(self, request):
        try:
            serializer = ArticleSerializer(data=request.data)
            if serializer.is_valid():
                article = serializer.save()
                return Response({'id': article.uid, 'message': 'Blog created successfully!'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Article.DoesNotExist:
            return Response({'error': 'No article found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request,id=None):
        try:
            article = Article.objects.get(uid=id)
            serializer = ListArticleSerializer(article)
            return Response({
                    "status":True,
                    "data":{
                    "article":serializer.data,
            }},status.HTTP_200_OK)
                
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            return Response({'error': 'No article found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self,request,id=None):
        #updates the blog
        try:
            article=Article.objects.get(uid=id)
            serializer = ArticleSerializer(article, data=request.data, partial=True)
            if serializer.is_valid():
                updated_article = serializer.save()
                return Response({'id': updated_article.uid, 'message': 'Blog updated successfully!'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Article.DoesNotExist:
            return Response({'error': 'No article found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self,request,id=None):
        try:
            article = Article.objects.get(uid=id)
            article.delete()
            return Response({'message': 'Blog deleted successfully!'}, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
class TopicView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            limit = int(request.GET.get('limit'))
            if limit:
                topics = Topic.objects.order_by("?")[:limit]
            else:
                topics = Topic.objects.all()
            serializer = TopicSerializer(topics, many=True)
            return Response({
                "status":True,
                "data":serializer.data
            },status.HTTP_200_OK)
        
        except Topic.DoesNotExist:
            return Response({'error': 'No topics found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ProfileView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            id = request.user.id            # take user id from the request
            user = CustomUser.objects.get(id=id)
            serializer = UserSerializer(user)
            return Response({
                "status":True,
                "data":serializer.data
            },status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'No topics found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


    def post(self,request):
        try:
            id = request.data['id']
            user = CustomUser.objects.get(id=id)
            serializer = UserSerializer(user)
            if serializer.is_valid():
                return Response({
                    "status":True,
                    "data":serializer.data
                },status.HTTP_200_OK)
            return Response({
                    "status":False,
                    "data":serializer.errors
            },status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'No user found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   

    def patch(self,request):
        #updates the blog
        try:
            id = request.user.id
            user=CustomUser.objects.get(id=id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response({'id': updated_user.uid, 'message': 'profile updated successfully!'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'No user found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListCommentView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self,request,id=None):
        try:
            comments = Comment.objects.filter(article__id=id)
            serializer = CommentSerializer(comments, many=True)
            return Response({
                "status":True,
                "data":serializer.data
            },status.HTTP_200_OK)
        
        except Comment.DoesNotExist:
            return Response({'error': 'No comment Found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self,request,id=None):
        try:
            serializer = CommentSerializer(request.data)
            if serializer.is_valid():
                comment = serializer.save()
                return Response({
                    "status":True,
                    "data":{
                        "uid": comment.uid
                    }
                },status.HTTP_201_CREATED)
            return Response({
                "status":False,
                "data":serializer.errors
            },status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self,request,id=None):
        try:
            comments = Comment.objects.filter(article__id=id)
            serializer = CommentSerializer(comments, many=True)
            return Response({
                "status":True,
                "data":serializer.data
            },status.HTTP_200_OK)
        
        except Comment.DoesNotExist:
            return Response({'error': 'No comment Found !'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def ArticleClap(request,id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=request.user.id)
            article = Article.objects.get(uid=id)

            clap,created = Clap.objects.get_or_create(article=article,user=user)

            if created:
                return Response({
                "status":True,
                "message": "Clap added successfully"
                },status.HTTP_201_CREATED)
            else:
                return Response({
                "status":False,
                "message": "You have already clapped for this article"
                },status.HTTP_409_CONFLICT)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def FollowAuthor(request,id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=request.user.id)
            author_to_follow = CustomUser.objects.get(id=id)

            follow,created = Follow.objects.get_or_create(follower=user,followed=author_to_follow)

            if created:
                return Response({
                "status":True,
                "message": f"You have started following {author_to_follow.username}"
                },status.HTTP_201_CREATED)
            else:
                return Response({
                "status":False,
                "message": "You have already followed The author before !"
                },status.HTTP_409_CONFLICT)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def ListAuthors(request):
    if request.method == 'GET':
        try:
            authors = CustomUser.objects.exclude(id=request.user.id)
            serializer = UserSerializer(authors,many=True)
            if serializer.is_valid():
                return Response({
                "status":True,
                "data": serializer.data
                },status.HTTP_200_OK)
            return Response({
                "status":False,
                "data": serializer.errors
            },status.HTTP_409_CONFLICT)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def AuthorDetails(request,id):
     if request.method == 'GET':
        try:
            author = CustomUser.objects.exclude(id=id)
            serializer = UserSerializer(author)
            if serializer.is_valid():
                return Response({
                "status":True,
                "data": serializer.data
                },status.HTTP_200_OK)
            return Response({
                "status":False,
                "data": serializer.errors
            },status.HTTP_409_CONFLICT)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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