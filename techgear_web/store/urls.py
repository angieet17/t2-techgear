from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('agregar/<str:producto_id>/', views.agregar_producto, name='agregar_producto'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('dashboard/editar/<str:producto_id>/', views.editar_producto, name='editar_producto'),
    path('dashboard/eliminar/<str:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
]