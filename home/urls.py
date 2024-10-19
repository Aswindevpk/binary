from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'topics',TopicView)


urlpatterns = [
    path('',include(router.urls)),
    path('articles/',ListArticleView.as_view(),name='article_list'),
    path('article/<str:uid>/',ArticleDetailView.as_view(),name='article_detail'),

    #loggedin user profile
    #following and unfollowing

    path('author/<str:id>/',AuthorDetailView.as_view(),name='author_detail'),
    path('authors/',ListAuthorView.as_view(),name='author_list'),
    path('authors/<str:uid>/is_following/',IsFollowingAuthorView.as_view(),name='user_is_following'),

    path('users/<str:uid>/follow/',FollowUserView.as_view(),name='follow_user'),
    path('users/<str:uid>/unfollow/',UnfollowUserView.as_view(),name='unfollow_user'),
    path('users/<str:uid>/follow-stats/',UserFollowStatsView.as_view(),name='user_follow-stats'),

    #actions on article
    path('article/<str:uid>/clap/',ArticleClapView.as_view(),name='clap_article'), 
    path('article/<str:uid>/bookmark/',ArticleBookmarkView.as_view(),name='bookmark_article'), 
    # Article written by a specific user 
    path('authors/<str:author_id>/articles/', AuthorArticlesView.as_view(), name='author-articles'),
    path('article/<str:id>/comments/',ListCommentView.as_view(),name='article_comment'),
    # path('author/<str:id>/',AuthorDetails,name='author_list'),
    path('plans/',PlansView.as_view(),name='home_plans'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]