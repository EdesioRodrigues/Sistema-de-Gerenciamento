from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorio_list, name='relatorio_list'),
    path('novo/', views.relatorio_create, name='relatorio_create'),
    path('<int:pk>/', views.relatorio_detail, name='relatorio_detail'),
    path('<int:pk>/editar/', views.relatorio_update, name='relatorio_update'),
    path('<int:pk>/excluir/', views.relatorio_delete, name='relatorio_delete'),
    path('<int:pk>/download/', views.relatorio_download, name='relatorio_download'),
    path('<int:pk>/email/', views.relatorio_email, name='relatorio_email'),
    path('graficos/', views.relatorio_graficos, name='relatorio_graficos'),
]
