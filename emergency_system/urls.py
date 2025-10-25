from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('incidents.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('analytics/', include('analytics.urls')),
    path('responders/', include('responders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
