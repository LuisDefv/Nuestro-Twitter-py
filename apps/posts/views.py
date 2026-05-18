"""Endpoints de posts."""

from constance import config
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Post
from .serializers import PostSerializer


class PostsPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        return config.POSTS_PER_PAGE


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    pagination_class = PostsPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
