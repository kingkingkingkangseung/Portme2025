from django.urls import path
from .views import (
    PostListCreateAPIView, PostDetailAPIView,
    CommentListAPIView, CommentCreateAPIView, CommentDetailAPIView
)

urlpatterns = [
    # Post
    path('posts/', PostListCreateAPIView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailAPIView.as_view(), name='post-detail'),

    # Comment
    path('posts/<int:post_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('posts/<int:post_id>/comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
]
