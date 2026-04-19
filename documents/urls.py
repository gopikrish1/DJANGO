from django.urls import path

from . import views

urlpatterns = [
    # List documents (GET) & upload new document (POST)
    path('', views.DocumentListCreateView.as_view(), name='document-list-create'),
    # Retrieve (GET) & delete (DELETE) a specific document
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
]
