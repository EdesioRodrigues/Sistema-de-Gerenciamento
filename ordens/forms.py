from django import forms
from .models import Ordem, ItemOrdem
from clientes.models import Cliente
from servicos.models import Servico
from django.forms import inlineformset_factory

class OrdemForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    nome_cliente_avulso = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Ordem
        fields = ['cliente', 'nome_cliente_avulso', 'data_hora', 'status', 'forma_pagamento', 'desconto', 'observacoes']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        nome_cliente_avulso = cleaned_data.get('nome_cliente_avulso')
        
        if not cliente and not nome_cliente_avulso:
            self.add_error('nome_cliente_avulso', 'Informe o cliente ou o nome do cliente avulso.')
        
        return cleaned_data

class ItemOrdemForm(forms.ModelForm):
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select servico-select'})
    )
    
    class Meta:
        model = ItemOrdem
        fields = ['servico', 'quantidade', 'preco']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'min': 1}),
            'preco': forms.NumberInput(attrs={'class': 'form-control preco-input', 'step': '0.01', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se já existe um serviço selecionado, preenche o preço
        if self.instance and self.instance.servico_id:
            self.fields['preco'].initial = self.instance.servico.preco

# Cria um formset para os itens da ordem
ItemOrdemFormSet = inlineformset_factory(
    Ordem, 
    ItemOrdem, 
    form=ItemOrdemForm,
    extra=1, 
    can_delete=True
)
