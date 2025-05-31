from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    """
    Modelo para armazenar informações adicionais do usuário
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cargo = models.CharField(max_length=50, blank=True, null=True)
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.cargo or 'Sem cargo'}"
