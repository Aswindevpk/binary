from rest_framework import serializers
from .models import *
from accounts.models import *

class BlogSerializer(serializers.ModelSerializer):
    #replace the id of tag and category to their names
    tag = serializers.SlugRelatedField(slug_field='tag', queryset=Tag.objects.all())
    category = serializers.SlugRelatedField(slug_field='category', queryset=Category.objects.all())
    creator = serializers.SlugRelatedField(slug_field='username', queryset=Category.objects.all())

    class Meta:
        model = Blog
        fields = ['title','content','tag','category','creator','slug','img']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',queryset=CustomUser.objects.all())
    class Meta:
        model = Comment
        fields = ['user','content']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','username','date_joined']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name','duration_days','price','desc','benefits']

