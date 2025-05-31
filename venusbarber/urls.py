from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('servicos/', include('servicos.urls')),
    path('clientes/', include('clientes.urls')),
    path('ordens/', include('ordens.urls')),
    path('relatorios/', include('relatorios.urls')),
]

# Adicionar URLs para arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
