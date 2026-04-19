from django.urls import path

from . import views

urlpatterns = [
    # Submit a new query (POST)
    path('query/', views.QueryCreateView.as_view(), name='query-create'),
    # List query history (GET, paginated)
    path('queries/', views.QueryListView.as_view(), name='query-list'),
]
