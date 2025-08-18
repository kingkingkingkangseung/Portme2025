from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer

# 🔒 공용: 현재 요청자가 접근 가능한 글만 반환하는 헬퍼
def visible_posts_for(request):
    qs = Post.objects.all()
    if not request.user.is_authenticated:
        # 비로그인: 회고록은 공개만, 다른 타입은 모두 허용
        return qs.filter(Q(type="retro", visibility="public") | ~Q(type="retro"))
    # 로그인: 본인 글은 모두 + 타인 글은 공개 회고록 + 다른 타입
    return qs.filter(
        Q(user=request.user) |
        Q(type="retro", visibility="public") |
        ~Q(type="retro")
    )


# 1) 글 목록 / 생성
class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()

    def get_serializer_class(self):
        return PostListSerializer if self.request.method == "GET" else PostDetailSerializer

    def get_queryset(self):
        qs = visible_posts_for(self.request)

        # 필터
        post_type = self.request.query_params.get("type")
        category  = self.request.query_params.get("category")
        tag       = self.request.query_params.get("tag")  # 태그 이름 포함 검색
        keyword   = self.request.query_params.get("q")

        if post_type:
            qs = qs.filter(type=post_type)
        if category:
            qs = qs.filter(category=category)
        if tag:
            qs = qs.filter(tags__name__icontains=tag)
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 2) 글 상세 / 수정 / 삭제
class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostDetailSerializer

    # 🔒 상세도 접근 가능한 글만
    def get_queryset(self):
        return visible_posts_for(self.request)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 조회수 증가
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


# 3) 좋아요 토글
class ToggleLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        post = get_object_or_404(visible_posts_for(request), pk=pk)  # 🔒
        if request.user in post.likes.all():
            post.likes.remove(request.user); liked = False
        else:
            post.likes.add(request.user); liked = True
        return Response({"liked": liked, "likes_count": post.likes.count()})


# 4) 스크랩 토글
class ToggleScrapAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        post = get_object_or_404(visible_posts_for(request), pk=pk)  # 🔒
        if request.user in post.scraps.all():
            post.scraps.remove(request.user); scrapped = False
        else:
            post.scraps.add(request.user); scrapped = True
        return Response({"scrapped": scrapped, "scraps_count": post.scraps.count()})


# 5) 댓글 작성
class CommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    def perform_create(self, serializer):
        post = get_object_or_404(visible_posts_for(self.request), pk=self.kwargs["post_id"])  # 🔒
        serializer.save(user=self.request.user, post=post)


# 6) 댓글 상세 / 수정 / 삭제
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


# 7) 댓글 목록
class CommentListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    def get_queryset(self):
        post = get_object_or_404(visible_posts_for(self.request), pk=self.kwargs["post_id"])  # 🔒
        return Comment.objects.filter(post=post).order_by("created_at")
