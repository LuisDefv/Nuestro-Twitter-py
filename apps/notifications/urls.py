from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='list'),
    path('notifications/unread-count/', views.UnreadCountView.as_view(), name='unread-count'),
    path('notifications/mark-all-read/', views.MarkAllReadView.as_view(), name='mark-all-read'),
]
