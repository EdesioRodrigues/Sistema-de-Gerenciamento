from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/data/', views.get_dashboard_data, name='get_dashboard_data'),
]
