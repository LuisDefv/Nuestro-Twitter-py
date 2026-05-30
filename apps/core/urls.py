from django.urls import path

from .views import ConfigView, HealthView, upload_image

app_name = 'core'

urlpatterns = [
    path('config/', ConfigView.as_view(), name='config'),
    path('health/', HealthView.as_view(), name='health'),
    path('upload/', upload_image, name='upload'),
]
