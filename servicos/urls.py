from django.urls import path
from . import views

urlpatterns = [
    path('', views.servico_list, name='servico_list'),
    path('novo/', views.servico_create, name='servico_create'),
    path('<int:pk>/editar/', views.servico_update, name='servico_update'),
    path('<int:pk>/excluir/', views.servico_delete, name='servico_delete'),
]
