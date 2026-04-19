from django.urls import path

from . import views

urlpatterns = [
    # JWT login endpoint
    path('login/', views.LoginView.as_view(), name='auth-login'),
]
