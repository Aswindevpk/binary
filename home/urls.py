from django.urls import path
from .views import *

urlpatterns = [
    path('blogs/',BlogView.as_view(),name='home_blogs'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('tags/',TagView.as_view(),name='home_tags'),
    path('categories/',CategoryView.as_view(),name='home_categories'),
    path('profile/',ProfileView.as_view(),name='home_profile'),
    path('plans/',PlansView.as_view(),name='home_plans'),
    # path('search/', SearchView.as_view(), name='search_results'),
]