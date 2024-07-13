from django.urls import path
from .views import *

urlpatterns = [
    #for creation and updation
    path('blog/',BlogView.as_view(),name='blog'),
    path('blog/<str:id>/', BlogView.as_view(), name='update-blog'),
    #for fetching
    path('blogs/category/<str:category_id>/', CategoryBlogListView.as_view(), name='category-blogs'),
    path('recent-blogs/', RecentBlogListView.as_view(), name='recent-blogs'),
    path('users/',UserView.as_view(),name='users'),
    path('tags/',TagView.as_view(),name='home_tags'),
    path('categories/',CategoryView.as_view(),name='home_categories'),
    path('profile/',ProfileView.as_view(),name='home_profile'),
    path('plans/',PlansView.as_view(),name='home_plans'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    # path('search/', SearchView.as_view(), name='search_results'),
]