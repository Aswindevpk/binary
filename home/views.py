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
from django.shortcuts import get_object_or_404

"""
Article of a specific user
"""
class AuthorArticlesView(generics.ListAPIView):
    serializer_class = ListArticleSerializer

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return Article.objects.filter(author__id=author_id)
   
"""
List and create article
"""
class ListArticleView(generics.ListCreateAPIView):
    serializer_class = ListArticleSerializer
    create_serializer_class = CreateArticleTitleContentSerializer

    def get_queryset(self):
        #filtering according to need
        limit = self.request.GET.get("limit")
        topic = self.request.GET.get("topic")
        bookmarked = self.request.GET.get("bookmarked")
        draft = self.request.GET.get("draft")

        if draft == 'true':
            return Article.objects.filter(is_published=False,author=self.request.user)
        if draft == 'false':
            return Article.objects.filter(is_published=True,author=self.request.user)
        if topic:
            return Article.objects.filter(topics__name=topic,is_published=True).distinct()
        if limit:
            return Article.objects.filter(is_published=True)[:int(limit)]
        if bookmarked:
            return Article.objects.filter(bookmarks__user=self.request.user)
        if topic and limit:
            return Article.objects.filter(is_published=True,topics__name=topic)[:int(limit)]
        return  Article.objects.filter(is_published=True)[:10]   #here limit the article by 10

    def get_serializer_class(self):
        # Use different serializer for creation
        if self.request.method == 'POST':
            return self.create_serializer_class
        return self.serializer_class


    def perform_create(self, serializer):
        author= self.request.user 
        serializer.save(author=author)

"""
Article full data view
"""
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = DetailArticleSerializer
    lookup_field = 'uid'

    def get(self, request,*args,**kwargs):
        #Fetch the article object using the uid
        article = get_object_or_404(Article,uid=self.kwargs['uid'])

        #Track the read status if already read or not
        if request.user.is_authenticated:
            #Ensure the user and article combination is only save once
            ArticleRead.objects.get_or_create(user=request.user,article=article)

        #call the original "get" method to return the serialized response
        return super().get(request,*args,**kwargs)






"""
List all article read by the user recently
"""
class ArticleReadView(generics.ListAPIView):
    serializer_class = ListArticleSerializer

    def get_queryset(self):
        read_articles = ArticleRead.objects.filter(user=self.request.user)
        #return the article object from the read_article query set
        return [read.article for read in read_articles]

"""
Deletes the read article history of the user
"""
class DeleteAllReadArticlesView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        #all articleread entries of logged in user
        read_articles = ArticleRead.objects.filter(user=request.user)

        #check if any history exist
        if read_articles.exists():
            read_articles.delete()
            return Response({"message": "All read articles have been deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "No read articles found for this user."}, status=status.HTTP_404_NOT_FOUND)





"""
Edit,and Delete Articles
"""
class ArticleEditView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleEditSerializer
    lookup_field = 'uid'
"""
uploades and track the images in the article content
"""
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






"""
    Author full data view
"""
class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


"""
checks if user follow the give user
"""
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

"""
List all authors
"""
class ListAuthorView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AuthorSerializer





"""
    clap on a article
"""
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




"""
Edit the bookmarked article notes
"""
class EditArticleBookmarkView(generics.RetrieveUpdateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    lookup_field = 'uid'


"""
    Bookmarks an article and list it
"""
class ArticleBookmarkView(generics.CreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        article_id = self.kwargs['uid']

        try:
            article = Article.objects.get(uid=article_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"article not found."},status=status.HTTP_404_NOT_FOUND)
        
        #Toggle bookmark: create if absent, delete if exists
        bookmark_article ,created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )

        if created:
            return Response({"message":"You have bookmarked this article."},status=status.HTTP_201_CREATED)
        if bookmark_article:
            #if already exists delete the bookmark
            bookmark_article.delete()
            return Response({"message":"Removed from bookmarks"},status=status.HTTP_200_OK)



class ListArticleBookmarkView(generics.ListAPIView):
    serializer_class = ListArticleSerializer

    def get_queryset(self):
        user = self.request.user
        # filtering article bookmarked by the user 
        return Article.objects.filter(bookmarks__user=user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['include_bookmark'] = True  # Include the 'note' field in the serializer
        return context






"""
    list article specific comments
"""
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








"""
List plans available
"""
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
    
"""
    all topic view create,delete,update etc
"""
class TopicView(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
