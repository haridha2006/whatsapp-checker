from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('api/initialize/', views.session_status, name='initialize'),
    path('api/check-single/', views.check_single, name='check_single'),
    path('api/check-batch/', views.check_batch, name='check_batch'),
    path('api/status/', views.get_status, name='status'),
    path('api/session-status/', views.session_status, name='session_status'),
    path('api/upload-file/', views.upload_file, name='upload_file'),
    path('api/download/<str:filename>/', views.download_results, name='download_results'),
    path('test/', views.test_page, name='test'),
    path('api/test/', views.test_api, name='test_api'),
]
