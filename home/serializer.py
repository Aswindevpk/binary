from rest_framework import serializers
from .models import *
from accounts.models import *



class CreateArticleTitleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid','title','content','author']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': False},
            'author': {'read_only':True},
        }

class DetailArticleSerializer(serializers.ModelSerializer):
    clap_count=serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model=Article
        fields=('uid', 'title','image', 'content' , 'clap_count', 'comment_count','created_at','author','is_premium')

        
    def get_comment_count(self, obj):
        return obj.comments.count()    # Ensure 'comments' is the related name

    def get_clap_count(self, obj):
        return obj.claps.count()    # Ensure 'claps' is the related name
    
    def get_author(self,obj):     
        request = self.context.get('request')  # Get the request object from serializer context
        img_url = obj.author.img.url if obj.author.img else None  # Get the relative image URL
        # Use request.build_absolute_uri() to get the full URL if the image exists
        full_img_url = request.build_absolute_uri(img_url) if img_url else None

        return {
        "id": obj.author.id,
        "username": obj.author.username,
        "img": full_img_url,  # Return the full URL of the image
        }

class ArticleEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['uid','title','content','subtitle','image','topics','is_published','is_premium']
        extra_kwargs = {
            'image': {'required': False,'allow_null':True},
            'topics': {'required': False,'allow_null':True},
        }

class ArticleReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRead
        fields = ['article']

class ListArticleSerializer(serializers.ModelSerializer):
    clap_count=serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    bookmark_id = serializers.SerializerMethodField()

    class Meta:
        model=Article
        fields=('uid', 'title','image', 'summary' , 'clap_count', 'comment_count','created_at','author','is_premium','bookmark_id')

    def get_summary(self,obj):
        return " ".join(obj.content.split()[:25])
        
    def get_comment_count(self, obj):
        return obj.comments.count()    # Ensure 'comments' is the related name

    def get_clap_count(self, obj):
        return obj.claps.count()    # Ensure 'claps' is the related name
    
    def get_author(self,obj):     
        request = self.context.get('request')  # Get the request object from serializer context
        img_url = obj.author.img.url if obj.author.img else None  # Get the relative image URL
        # Use request.build_absolute_uri() to get the full URL if the image exists
        full_img_url = request.build_absolute_uri(img_url) if img_url else None

        return {
        "id": obj.author.id,
        "username": obj.author.username,
        "img": full_img_url,  # Return the full URL of the image
        }
    
    def get_bookmark_id(self, obj):
        #Only return note if "include_note" flag is set in the context
        if self.context.get('include_bookmark',False):
            request = self.context.get('request')
            user = request.user if request else None

            if user:
                try:
                    bookmark = Bookmark.objects.get(user=user,article=obj)
                    return bookmark.uid
                except Bookmark.DoesNotExist:
                    return None
        return None

    

    

    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['author','content','uid','created_at']

    def get_author(self,obj):     
        return { "id":obj.author.id,"username":obj.author.username }
    
class DetailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['name','uid']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username','name','about','email','img','pronouns')

class AuthorSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id','username','about','is_following','img')

    def get_is_following(self,obj):
        user = self.context.get('user')
        if user:
            return Follow.objects.filter(follower=user,followed=obj.id).exists()
        return False

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','duration_days','price','desc','benefits']


"""
    Reaction on the article
"""
class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clap
        fields = ['article','user']
        extra_kwargs = {
            'user':{'read_only':True}
        }

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['article','user','note']
        extra_kwargs = {
            'user':{'read_only':True},
            'note':{'required':False,'allow_null':True}
        }

    
