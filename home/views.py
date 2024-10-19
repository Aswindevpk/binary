from django.forms import ValidationError
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from accounts.models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import generics
from rest_framework import viewsets


class AuthorArticlesView(generics.ListAPIView):
    serializer_class = ListArticleSerializer

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return Article.objects.filter(author__id=author_id)
   

class ListArticleView(generics.ListCreateAPIView):
    serializer_class = ListArticleSerializer

    def get_queryset(self):
        #filtering according to need
        limit = self.request.GET.get("limit")
        topic = self.request.GET.get("topic")
        bookmarked = self.request.GET.get("bookmarked")

        if topic:
            return Article.objects.filter(topics__name=topic,is_published=True).distinct()
        if limit:
            return Article.objects.filter(is_published=True)[:int(limit)]
        if bookmarked:
            return Article.objects.filter(bookmarks__user=self.request.user)
        if topic and limit:
            return Article.objects.filter(is_published=True,topics__name=topic)[:int(limit)]
        return  Article.objects.filter(is_published=True)[:10]   #here limit the article by 10


    def perform_create(self, serializer):
        author= self.request.user 
        serializer.save(author=author)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = DetailArticleSerializer
    lookup_field = 'uid'


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

class IsFollowingAuthorView(APIView):

    def get(self,request, uid):
        try:
            author = CustomUser.objects.get(id=uid)
        except CustomUser.DoesNotExist:
            return Response({"error":"user not found."},status=status.HTTP_404_NOT_FOUND)
        
        is_following = Follow.objects.filter(follower=request.user,followed=author).exists()

        return Response(
            {'is_following':is_following},status=status.HTTP_200_OK
        )

class ListAuthorView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AuthorSerializer


#all topic view create,delete,update etc
class TopicView(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()

#follow a user
class FollowUserView(generics.CreateAPIView):
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        followed_user_id = self.kwargs['uid']
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"user not found."},status=status.HTTP_404_NOT_FOUND)
        
        follow_relation ,created = Follow.objects.get_or_create(
            follower=request.user,
            followed=followed_user
        )

        if created:
            return Response({"message":"You are now following this user."},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"You are already following this user."},status=status.HTTP_200_OK)
        
#unfollow a user
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = FollowSerializer

    def delete(self, request, *args, **kwargs):
        followed_user_id = self.kwargs['uid']
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"user not found."},status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow_relation = Follow.objects.get(
                follower=request.user,
                followed=followed_user
            )
            follow_relation.delete()
            return Response({"message":"You have Unfollowed this user."},status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"message":"You are not following this user."},status=status.HTTP_400_BAD_REQUEST)
        
class ArticleClapView(generics.CreateAPIView):
    serializer_class = ClapSerializer

    def create(self, request, *args, **kwargs):
        article_id = self.kwargs['uid']
        try:
            article = Article.objects.get(uid=article_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"article not found."},status=status.HTTP_404_NOT_FOUND)
        
        clap_article ,created = Clap.objects.get_or_create(
            user=request.user,
            article=article
        )

        if created:
            return Response({"message":"You have claped for this article."},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"You are already claped this article."},status=status.HTTP_200_OK)

class ArticleBookmarkView(generics.CreateAPIView):
    serializer_class = ClapSerializer

    def create(self, request, *args, **kwargs):
        article_id = self.kwargs['uid']
        try:
            article = Article.objects.get(uid=article_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"article not found."},status=status.HTTP_404_NOT_FOUND)
        
        bookmark_article ,created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )

        if created:
            return Response({"message":"You have bookmarked this article."},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"You have already bookmarked this article."},status=status.HTTP_200_OK)




class ListCommentView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DetailCommentSerializer
        return CommentSerializer

    def get_queryset(self):
        id = self.kwargs['id']
        return Comment.objects.filter(article__uid = id)
 
    def perform_create(self, serializer):
        #get the article using passed id
        article_id = self.kwargs['id']
        commenter= self.request.user #user commenting on the article

        try:
            article = Article.objects.get(uid=article_id)
        except Article.DoesNotExist:
            raise serializer.ValidationError({"error":"Article not found"})

        # Save the comment with the article linked to it 
        serializer.save(article=article,author=commenter)

class UserFollowStatsView(APIView):

    def get(self,request,*args,**kwargs):
        user_id = kwargs.get('uid')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        #count the number of followers
        followers_count = Follow.objects.filter(followed=user).count()

        #count the number of following
        following_count = Follow.objects.filter(follower=user).count()

        return Response({
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count
        })



class PlansView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class ImageUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        image_file = request.data.get('image')

        if image_file:
            uploaded_image = BlogImage.objects.create(image=image_file)
            image_url = request.build_absolute_uri(uploaded_image.image.url)
            return Response({'imageUrl': image_url}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)