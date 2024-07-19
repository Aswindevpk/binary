from rest_framework import serializers
from .models import *
from accounts.models import *

class ArticleSerializer(serializers.ModelSerializer):
    author_id = serializers.UUIDField()

    class Meta:
        model = Article
        fields = ['uid','title','subtitle','content','author_id','image']
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
            'subtitle': {'required': False, 'allow_null': True},
            'content': {'required': False, 'allow_blank': True},
            'topic': {'required': False, 'allow_null': True},
            'image': {'required': False, 'allow_null': True},
            'author_id': {'required': True},
        }

    def get_author(self,obj):
        return obj.author.id

class ListArticleSerializer(serializers.ModelSerializer):
    clap_count=serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model=Article
        fields=('uid', 'title','subtitle','image', 'content', 'clap_count', 'comment_count','created_at','author')
        
    def get_comment_count(self, obj):
        return obj.comments.count()    # Ensure 'comments' is the related name

    def get_clap_count(self, obj):
        return obj.claps.count()    # Ensure 'claps' is the related name
    
    def get_author(self,obj):     
        return { "id":obj.author.id,"username":obj.author.username }
    
    
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',queryset=CustomUser.objects.all())
    class Meta:
        model = Comment
        fields = ['user','content']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['name','uid']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','about']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','duration_days','price','desc','benefits']

