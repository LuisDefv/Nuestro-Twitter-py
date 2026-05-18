"""URLs de posts."""
from django.urls import path

from .views import PostListCreateView

app_name = 'posts'

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='list-create'),
]
