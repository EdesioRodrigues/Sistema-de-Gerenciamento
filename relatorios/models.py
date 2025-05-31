from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Relatorio(models.Model):
    TIPO_CHOICES = (
        ('financeiro', 'Financeiro'),
        ('servicos', 'Serviços'),
        ('clientes', 'Clientes'),
    )
    
    titulo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='financeiro')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    data_geracao = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_descontos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    lucro = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_ordens = models.IntegerField(default=0)
    email_destino = models.EmailField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    arquivo_pdf = models.FileField(upload_to='relatorios/', blank=True, null=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='relatorios')
    
    def __str__(self):
        return f"{self.titulo} ({self.data_inicio} a {self.data_fim})"
    
    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-data_geracao']
