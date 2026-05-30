"""Endpoints de configuración pública (lo que Angular necesita en runtime)."""

import cloudinary.uploader
from constance import config
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
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
                'upload': request.build_absolute_uri(reverse('core:upload')),
                'login': request.build_absolute_uri('/api/auth/login/'),
                'refresh': request.build_absolute_uri('/api/auth/refresh/'),
            },
        })


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """Sube una imagen a Cloudinary y devuelve la URL pública."""
    file = request.FILES.get('file')
    if not file:
        return Response(
            {'error': 'No se envió ningún archivo.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response(
            {'error': 'Tipo de archivo no soportado. Usá JPEG, PNG, GIF o WebP.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'La imagen supera los 10 MB.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = cloudinary.uploader.upload(
            file,
            folder='nandetuiter',
            resource_type='image',
        )
        return Response({'url': result['secure_url']})
    except Exception as e:
        return Response(
            {'error': f'Error al subir la imagen: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
