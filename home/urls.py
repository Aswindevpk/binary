from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'topics',TopicView)


urlpatterns = [
    path('',include(router.urls)),
    path('articles/',ListArticleView.as_view(),name='article_list'),
    path('article/<str:uid>/',ArticleDetailView.as_view(),name='article_detail'),
    path('article-edit/<str:uid>/',ArticleEditView.as_view(),name='article_edit'),
    path('articles-read/',ArticleReadView.as_view(),name='article_read'),
    path('delete-articles-read/',DeleteAllReadArticlesView.as_view(),name='article_read_delete'),
    
    path('author/<str:id>/',AuthorDetailView.as_view(),name='author_detail'),
    path('authors/',ListAuthorView.as_view(),name='author_list'),
    path('authors/<str:uid>/is_following/',IsFollowingAuthorView.as_view(),name='user_is_following'),

    #actions on article
    path('article/<str:uid>/clap/',ArticleClapView.as_view(),name='clap_article'), 

    #bookmarking and related
    path('article/<str:uid>/bookmark/',ArticleBookmarkView.as_view(),name='bookmark_article'), 
    path('bookmarks/',ListArticleBookmarkView.as_view(),name='bookmarked_articles'), 
    path('bookmark/<str:uid>/',EditArticleBookmarkView.as_view(),name='edit_bookmark_article'), 
    # Article written by a specific user 
    path('authors/<str:author_id>/articles/', AuthorArticlesView.as_view(), name='author-articles'),
    path('article/<str:id>/comments/',ListCommentView.as_view(),name='article_comment'),


    path('plans/',PlansView.as_view(),name='home_plans'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]