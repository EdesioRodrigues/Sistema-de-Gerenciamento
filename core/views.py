from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from ordens.models import Ordem
from clientes.models import Cliente
from servicos.models import Servico

@login_required
def home_view(request):
    """Página inicial após login com dashboard e ações rápidas"""
    # Dados para indicadores
    total_clientes = Cliente.objects.count()
    total_servicos = Servico.objects.count()
    total_ordens = Ordem.objects.count()
    total_relatorios = 0  # Placeholder, substituir pelo modelo real quando disponível
    
    # Ordens recentes (últimas 10)
    ordens_recentes = Ordem.objects.all().order_by('-data_hora')[:10]
    
    context = {
        'total_clientes': total_clientes,
        'total_servicos': total_servicos,
        'total_ordens': total_ordens,
        'total_relatorios': total_relatorios,
        'ordens_recentes': ordens_recentes,
    }
    
    # Se for uma requisição AJAX, retorna apenas os dados
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'total_clientes': total_clientes,
            'total_servicos': total_servicos,
            'total_ordens': total_ordens,
            'total_relatorios': total_relatorios,
            'ordens_recentes_html': render(request, 'core/includes/ordens_recentes.html', 
                                          {'ordens_recentes': ordens_recentes}).content.decode('utf-8')
        })
    
    return render(request, 'core/home.html', context)

@login_required
def dashboard_view(request):
    """Dashboard administrativo com estatísticas e gráficos"""
    # Dados para gráfico de faturamento dos últimos 7 dias
    hoje = timezone.now().date()
    data_inicio = hoje - timedelta(days=6)
    
    faturamento_diario = []
    for i in range(7):
        data = data_inicio + timedelta(days=i)
        ordens_dia = Ordem.objects.filter(
            data_hora__date=data,
            status='concluido'
        )
        valor_total = sum(ordem.valor_final for ordem in ordens_dia)
        faturamento_diario.append({
            'data': data.strftime('%d/%m'),
            'valor': float(valor_total)
        })
    
    context = {
        'faturamento_diario': faturamento_diario,
    }
    
    return render(request, 'core/dashboard.html', context)

def get_dashboard_data(request):
    """Endpoint AJAX para atualizar dados do dashboard"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    # Dados para indicadores
    total_clientes = Cliente.objects.count()
    total_servicos = Servico.objects.count()
    total_ordens = Ordem.objects.count()
    total_relatorios = 0  # Placeholder, substituir pelo modelo real quando disponível
    
    # Ordens recentes (últimas 10)
    ordens_recentes = Ordem.objects.all().order_by('-data_hora')[:10]
    
    # Renderiza o HTML das ordens recentes
    ordens_html = render(request, 'core/includes/ordens_recentes.html', 
                        {'ordens_recentes': ordens_recentes}).content.decode('utf-8')
    
    return JsonResponse({
        'total_clientes': total_clientes,
        'total_servicos': total_servicos,
        'total_ordens': total_ordens,
        'total_relatorios': total_relatorios,
        'ordens_recentes_html': ordens_html
    })
