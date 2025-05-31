from django.urls import path
from . import views

urlpatterns = [
    path('', views.ordem_list, name='ordem_list'),
    path('nova/', views.ordem_create, name='ordem_create'),
    path('<int:pk>/', views.ordem_detail, name='ordem_detail'),
    path('<int:pk>/editar/', views.ordem_update, name='ordem_update'),
    path('<int:pk>/excluir/', views.ordem_delete, name='ordem_delete'),
    path('servico/<int:servico_id>/info/', views.get_servico_info, name='get_servico_info'),
]
