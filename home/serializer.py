from rest_framework import serializers
from .models import *
from accounts.models import *

class ArticleSerializer(serializers.ModelSerializer):
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), required=False, allow_null=True, many=True)

    class Meta:
        model = Article
        fields = ['uid','title','subtitle','content','author','image','topics']
        extra_kwargs = {
            'title': {'required': True},
            'subtitle': {'required': False, 'allow_null': True},
            'content': {'required': True},
            'topics': {'required': False, 'allow_null': True},
            'image': {'required': False, 'allow_null': True},
            'author': {'required': True},
        }

    
    def update(self, instance, validated_data):
        topics_data = validated_data.pop('topics',None)  # Extract topics data if present
        print(topics_data)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)

        if topics_data is not None:
            instance.topics.clear()  # Remove all existing topics
            for topic_data in topics_data:
                print(topic_data)
                topic = Topic.objects.get(uid=topic_data['uid'])
                instance.topics.add(topic)

        instance.save()
        return instance


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
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['author','content','uid']

    def get_author(self,obj):     
        return { "id":obj.author.id,"username":obj.author.username }
    
class DetailCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['author','content','article']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['name','uid']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username','about')


class AuthorSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id','username','about','is_following')

    def get_is_following(self,obj):
        user = self.context.get('user')
        if user:
            return Follow.objects.filter(follower=user,followed=obj.id).exists()
        return False

    




class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','duration_days','price','desc','benefits']

