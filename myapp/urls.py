from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_neumologo, name='login_neumologo'),
    path('registrar/', views.registro_neumologo, name='registro_neumologo'),
    path('home/', views.home, name='home'),
    path('recuperar/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('registrar_paciente/', views.registrar_paciente, name='registrar_paciente'),
    path('buscar_paciente/', views.buscar_paciente, name='buscar_paciente'),
    path('agregar_radiografia/<int:paciente_id>', views.agregar_radiografia, name='agregar_radiografia'),
]