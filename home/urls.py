from django.urls import path
from .views import *

urlpatterns = [
    path('blogs/',BlogView.as_view(),name='home_blogs'),
    path('tags/',TagView.as_view(),name='home_tags'),
    path('categories/',CategoryView.as_view(),name='home_categories'),
]