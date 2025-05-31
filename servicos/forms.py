from django import forms
from .models import Servico

class ServicoForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de serviços
    """
    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'preco', 'duracao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracao': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
