from django.urls import path

from . import views

urlpatterns = [
    # LLM Q&A with prompt templates (POST)
    path('ask-ai/', views.AskAIView.as_view(), name='ask-ai'),
    # RAG-based document query (POST)
    path('rag-query/', views.RAGQueryView.as_view(), name='rag-query'),
    # Paginated query history (GET)
    path('query-history/', views.QueryHistoryView.as_view(), name='query-history'),
]
