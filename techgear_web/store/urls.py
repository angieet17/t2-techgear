from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('dashboard/editar/<str:producto_id>/', views.editar_producto, name='editar_producto'),
    path('dashboard/eliminar/<str:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
]