"""
core URL Configuration

Routes:
    /api/documents/       → Document CRUD
    /api/query/           → Submit a query
    /api/queries/         → List query history
    /api/auth/login/      → JWT login
    /admin/               → Django admin panel
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # DRF UI Login/Logout
    path('api-auth/', include('rest_framework.urls')),

    # Documents API
    path('api/documents/', include('documents.urls')),

    # Queries API (both /api/query/ and /api/queries/ are defined in queries.urls)
    path('api/', include('queries.urls')),

    # Authentication API
    path('api/auth/', include('users.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
