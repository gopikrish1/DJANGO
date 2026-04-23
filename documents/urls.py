from django.urls import path

from . import views

urlpatterns = [
    # List documents (GET) & upload new document (POST)
    path('', views.DocumentListCreateView.as_view(), name='document-list-create'),
    # Retrieve a specific document (GET)
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    # Ingest a document into the vector store (POST)
    path('ingest-doc/', views.IngestDocView.as_view(), name='ingest-doc'),
]
