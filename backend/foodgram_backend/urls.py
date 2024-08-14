from api.views import redirect_short_link
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

urlpatterns = [
    path('<str:short_url>/', redirect_short_link, name='redirect_short_link'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api-token-auth/', views.obtain_auth_token),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)