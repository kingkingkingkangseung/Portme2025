# apps/community/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    CommentSerializer
)

# 1) 글 목록 / 생성
class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()

    def get_serializer_class(self):
        # 목록(GET) → 간단한 리스트용, 생성(POST) → 상세용
        return PostListSerializer if self.request.method == "GET" else PostDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        post_type = self.request.query_params.get("type")
        category  = self.request.query_params.get("category")
        tag       = self.request.query_params.get("tag")
        keyword   = self.request.query_params.get("q")

        if post_type:
            qs = qs.filter(type=post_type)
        if category:
            qs = qs.filter(category=category)
        if tag:
            qs = qs.filter(tags__icontains=tag)
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 2) 글 상세 / 수정 / 삭제
class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 조회수 ↑ (동시성 안전하게 F표현식)
        Post.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            self.permission_denied(self.request, message="본인 글만 수정 가능")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="본인 글만 삭제 가능")
        instance.delete()


# 3) 댓글 작성 (POST /posts/{post_id}/comments/)
class CommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        serializer.save(user=self.request.user, post=post)


# 4) 댓글 상세 / 수정 / 삭제 (GET/PATCH/DELETE /comments/{pk}/)
class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.user != self.request.user:
            self.permission_denied(self.request, message="본인 댓글만 수정 가능")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="본인 댓글만 삭제 가능")
        instance.delete()


# 5) 댓글 목록 (GET /posts/{post_id}/comments/)
class CommentListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return Comment.objects.filter(post=post).order_by("created_at")