from django.contrib import admin
from django.urls import path, include
from checker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/check-single/', views.check_single, name='check_single'),
    path('api/check-batch/', views.check_batch, name='check_batch'),
    path('api/upload-file/', views.upload_file, name='upload_file'),
    path('api/status/', views.get_status, name='get_status'),
    path('api/download/<str:filename>/', views.download_results, name='download_results'),
    path('session-status/', views.session_status, name='session_status'),
    path('test/', views.test_page, name='test'),
    path('test-api/', views.test_api, name='test_api'),
]
