from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_neumologo, name='login_neumologo'),
    path('registrar/', views.registro_neumologo, name='registro_neumologo'),
    path('home/', views.home, name='home'),
    path('recuperar/', views.cambiar_contrasena, name='cambiar_contrasena'),
]