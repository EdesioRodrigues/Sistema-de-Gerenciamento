from django.urls import path
from . import views

urlpatterns = [
    path('', views.cliente_list, name='cliente_list'),
    path('novo/', views.cliente_create, name='cliente_create'),
    path('<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),
]
