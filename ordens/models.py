from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from clientes.models import Cliente
from servicos.models import Servico

class Ordem(models.Model):
    STATUS_CHOICES = (
        ('agendado', 'Agendado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )
    
    PAGAMENTO_CHOICES = (
        ('dinheiro', 'Dinheiro'),
        ('cartao_debito', 'Cartão de Débito'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('pix', 'PIX'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordens')
    nome_cliente_avulso = models.CharField(max_length=100, blank=True, null=True)
    data_hora = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado')
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='dinheiro')
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordens_criadas')
    
    @property
    def valor_total(self):
        total = sum(item.subtotal for item in self.itens.all())
        return total
    
    @property
    def valor_final(self):
        return self.valor_total - self.desconto
    
    def __str__(self):
        cliente_nome = self.cliente.nome if self.cliente else self.nome_cliente_avulso
        return f"Ordem #{self.id} - {cliente_nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Atualiza a última visita do cliente
        if self.cliente and self.status == 'concluido':
            self.cliente.ultima_visita = timezone.now()
            self.cliente.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Ordem"
        verbose_name_plural = "Ordens"
        ordering = ['-data_hora']


class ItemOrdem(models.Model):
    ordem = models.ForeignKey(Ordem, on_delete=models.CASCADE, related_name='itens')
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Alterando para método em vez de property para evitar o erro de setter
    def subtotal(self):
        return self.preco * self.quantidade
    
    # Mantendo a property para compatibilidade, mas usando o método
    @property
    def subtotal(self):
        return self.subtotal()
    
    def save(self, *args, **kwargs):
        # Se o preço não foi definido, usa o preço atual do serviço
        if not self.preco:
            self.preco = self.servico.preco
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantidade}x {self.servico.nome}"
    
    class Meta:
        verbose_name = "Item da Ordem"
        verbose_name_plural = "Itens da Ordem"
