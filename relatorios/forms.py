from django import forms
from .models import Relatorio
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class RelatorioForm(forms.ModelForm):
    PERIODO_CHOICES = (
        ('dia', 'Dia Atual'),
        ('semana', 'Semana Atual'),
        ('mes', 'Mês Atual'),
        ('personalizado', 'Personalizado'),
    )
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        initial='mes',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_periodo'})
    )
    
    class Meta:
        model = Relatorio
        fields = ['titulo', 'tipo', 'periodo', 'data_inicio', 'data_fim', 'email_destino', 'observacoes']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email_destino': forms.EmailInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir datas padrão (mês atual)
        hoje = timezone.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
        self.fields['data_inicio'].initial = primeiro_dia_mes
        self.fields['data_fim'].initial = hoje
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        
        # Ajustar datas com base no período selecionado
        hoje = timezone.now().date()
        
        if periodo == 'dia':
            cleaned_data['data_inicio'] = hoje
            cleaned_data['data_fim'] = hoje
        elif periodo == 'semana':
            # Início da semana (segunda-feira)
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            cleaned_data['data_inicio'] = inicio_semana
            cleaned_data['data_fim'] = hoje
        elif periodo == 'mes':
            # Início do mês
            inicio_mes = hoje.replace(day=1)
            cleaned_data['data_inicio'] = inicio_mes
            cleaned_data['data_fim'] = hoje
        
        # Validar que data_fim não é anterior a data_inicio
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_fim < data_inicio:
            self.add_error('data_fim', 'A data final não pode ser anterior à data inicial.')
        
        return cleaned_data
