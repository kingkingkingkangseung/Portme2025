from django.urls import path
from .views import (
    PostListCreateAPIView, PostDetailAPIView,
    CommentListAPIView, CommentCreateAPIView, CommentDetailAPIView,
    ToggleLikeAPIView, ToggleScrapAPIView,
)

urlpatterns = [
    # Post
    path("posts/",               PostListCreateAPIView.as_view(), name="post-list-create"),
    path("posts/<int:pk>/",      PostDetailAPIView.as_view(),     name="post-detail"),
    path("posts/<int:pk>/like/", ToggleLikeAPIView.as_view(),     name="post-like"),
    path("posts/<int:pk>/scrap/",ToggleScrapAPIView.as_view(),    name="post-scrap"),

    # Comment
    path("posts/<int:post_id>/comments/",          CommentListAPIView.as_view(),   name="comment-list"),
    path("posts/<int:post_id>/comments/create/",   CommentCreateAPIView.as_view(), name="comment-create"),
    path("comments/<int:pk>/",                     CommentDetailAPIView.as_view(), name="comment-detail"),
]