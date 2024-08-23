from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

from api.utils import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', include('api.urls'), name='api'),
    path('api/', include('djoser.urls'), name='djoser'),
    path('api/auth/', include('djoser.urls'), name='auth'),
    path('api/auth/', include('djoser.urls.authtoken'), name='auth-token'),
    path('api-token-auth/', views.obtain_auth_token, name='token-auth'),
    path('s/<str:short_url>/', redirect_short_link,
         name='redirect_short_link'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
