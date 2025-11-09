from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_views.index, name='index'),
    path('dashboard/', api_views.dashboard, name='dashboard'),
    path('', include('api.urls')),  # Include API URLs at root
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
