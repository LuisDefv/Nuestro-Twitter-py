"""Endpoints de configuración pública (lo que Angular necesita en runtime)."""

from constance import config
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ConfigView(APIView):
    """Devuelve config editable desde admin (constance) que el frontend consume."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'site_name': config.SITE_NAME,
            'post_max_chars': config.POST_MAX_CHARS,
            'posts_per_page': config.POSTS_PER_PAGE,
            'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        })


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})


class ApiRootView(APIView):
    """Índice de endpoints disponibles. Sirve como root del backend para debug."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'name': 'Nandetuiter API',
            'frontend': 'http://localhost:4200',
            'admin': request.build_absolute_uri('/admin/'),
            'endpoints': {
                'config': request.build_absolute_uri(reverse('core:config')),
                'health': request.build_absolute_uri(reverse('core:health')),
                'login': request.build_absolute_uri('/api/auth/login/'),
                'refresh': request.build_absolute_uri('/api/auth/refresh/'),
            },
        })
