from rest_framework import serializers
from .models import *
from accounts.models import *

class RecentBlogSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    
    class Meta:
        model=Blog
        fields=['title','author','uid']
        
    def get_author(self,obj):
        return obj.author_id.username

class BlogSerializer(serializers.ModelSerializer):
    category_id = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all(), required=False, allow_null=True)
    author_id = serializers.SlugRelatedField(slug_field='username', queryset=CustomUser.objects.all())

    class Meta:
        model = Blog
        fields = ['uid','title','content','category_id','author_id']
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
            'content': {'required': False, 'allow_blank': True},
            'category': {'required': False, 'allow_null': True},
        }

class HomeBlogSerializer(serializers.ModelSerializer):
    clap_count=serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model=Blog
        fields=('uid', 'title', 'content', 'clap_count', 'comment_count','created_at','author')
        
    def get_comment_count(self, obj):
        return obj.comments.count()    # Ensure 'comments' is the related name

    def get_clap_count(self, obj):
        return obj.claps.count()    # Ensure 'claps' is the related name
    
    def get_author(self,obj):
        return obj.author_id.username
    
    
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',queryset=CustomUser.objects.all())
    class Meta:
        model = Comment
        fields = ['user','content']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name','uid']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name','uid']

class UserSerializer(serializers.ModelSerializer):
    about = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id','username','about']
        
        
    def get_about(self, obj):
        max_length = 50  # Maximum number of characters
        if len(obj.about) > max_length:
            return obj.about[:max_length] + '...'
        else:
            return obj.about

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','duration_days','price','desc','benefits']

