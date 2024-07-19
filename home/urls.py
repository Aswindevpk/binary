from django.urls import path
from .views import *

urlpatterns = [
    path('articles/',ListArticleView.as_view(),name='article_list'),
    path('article/<str:id>/',ArticleDetailView.as_view(),name='article_detail'),
    path('topics/',TopicView.as_view(),name='topic_list'),
    path('article/<str:id>/comments/',ListCommentView.as_view(),name='article_comment'),
    # path('article/<str:id>/comment/',CommentView.as_view(),name='comment_article'),
    path('article/<str:id>/clap/',ArticleClap,name='clap_article'), # type: ignore
    path('follow/<str:id>/',FollowAuthor,name='follow_author'),
    path('authors/',ListAuthors,name='author_list'),
    path('authors/<str:id>/',AuthorDetails,name='author_list'),
    path('profile/',ProfileView.as_view(),name='user_profile'),
    path('plans/',PlansView.as_view(),name='home_plans'),

    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]