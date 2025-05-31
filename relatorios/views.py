from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta, datetime
from decimal import Decimal
import json
import os
import tempfile
from weasyprint import HTML, CSS
from .models import Relatorio
from .forms import RelatorioForm
from ordens.models import Ordem, ItemOrdem
from servicos.models import Servico
from django.core.mail import EmailMessage

@login_required
def relatorio_list(request):
    """Lista todos os relatórios"""
    relatorios = Relatorio.objects.all().order_by('-data_geracao')
    return render(request, 'relatorios/relatorio_list.html', {'relatorios': relatorios})

@login_required
def relatorio_detail(request, pk):
    """Exibe os detalhes de um relatório"""
    relatorio = get_object_or_404(Relatorio, pk=pk)
    
    # Obter ordens do período
    ordens = Ordem.objects.filter(
        data_hora__date__gte=relatorio.data_inicio,
        data_hora__date__lte=relatorio.data_fim,
        status='concluido'
    ).order_by('-data_hora')
    
    # Dados para gráficos
    dados_graficos = gerar_dados_graficos(relatorio.data_inicio, relatorio.data_fim)
    
    return render(request, 'relatorios/relatorio_detail.html', {
        'relatorio': relatorio,
        'ordens': ordens,
        'dados_graficos': json.dumps(dados_graficos)
    })

@login_required
def relatorio_create(request):
    """Cria um novo relatório"""
    if request.method == 'POST':
        form = RelatorioForm(request.POST)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.criado_por = request.user
            
            # Calcular dados financeiros
            ordens = Ordem.objects.filter(
                data_hora__date__gte=relatorio.data_inicio,
                data_hora__date__lte=relatorio.data_fim,
                status='concluido'
            )
            
            # Usar Decimal para evitar erros de tipo
            relatorio.valor_total = Decimal(sum(ordem.valor_total for ordem in ordens))
            relatorio.valor_descontos = Decimal(sum(ordem.desconto for ordem in ordens))
            relatorio.lucro = relatorio.valor_total - relatorio.valor_descontos
            relatorio.total_ordens = ordens.count()
            
            # Gerar PDF
            if relatorio.total_ordens > 0:
                relatorio.arquivo_pdf = gerar_pdf_relatorio(relatorio, ordens)
            
            relatorio.save()
            
            # Enviar por email se solicitado
            if relatorio.email_destino:
                enviar_relatorio_email(relatorio)
            
            return redirect('relatorio_detail', pk=relatorio.pk)
    else:
        form = RelatorioForm()
    
    return render(request, 'relatorios/relatorio_form.html', {'form': form})

@login_required
def relatorio_update(request, pk):
    """Atualiza um relatório existente"""
    relatorio = get_object_or_404(Relatorio, pk=pk)
    
    if request.method == 'POST':
        form = RelatorioForm(request.POST, instance=relatorio)
        if form.is_valid():
            relatorio = form.save(commit=False)
            
            # Recalcular dados financeiros
            ordens = Ordem.objects.filter(
                data_hora__date__gte=relatorio.data_inicio,
                data_hora__date__lte=relatorio.data_fim,
                status='concluido'
            )
            
            # Usar Decimal para evitar erros de tipo
            relatorio.valor_total = Decimal(sum(ordem.valor_total for ordem in ordens))
            relatorio.valor_descontos = Decimal(sum(ordem.desconto for ordem in ordens))
            relatorio.lucro = relatorio.valor_total - relatorio.valor_descontos
            relatorio.total_ordens = ordens.count()
            
            # Gerar novo PDF
            if relatorio.total_ordens > 0:
                relatorio.arquivo_pdf = gerar_pdf_relatorio(relatorio, ordens)
            
            relatorio.save()
            
            # Enviar por email se solicitado
            if relatorio.email_destino:
                enviar_relatorio_email(relatorio)
            
            return redirect('relatorio_detail', pk=relatorio.pk)
    else:
        form = RelatorioForm(instance=relatorio)
    
    return render(request, 'relatorios/relatorio_form.html', {'form': form, 'relatorio': relatorio})

@login_required
def relatorio_delete(request, pk):
    """Exclui um relatório"""
    relatorio = get_object_or_404(Relatorio, pk=pk)
    
    if request.method == 'POST':
        # Excluir arquivo PDF se existir
        if relatorio.arquivo_pdf:
            if os.path.isfile(relatorio.arquivo_pdf.path):
                os.remove(relatorio.arquivo_pdf.path)
        
        relatorio.delete()
        return redirect('relatorio_list')
    
    return render(request, 'relatorios/relatorio_confirm_delete.html', {'relatorio': relatorio})

@login_required
def relatorio_download(request, pk):
    """Download do PDF do relatório"""
    relatorio = get_object_or_404(Relatorio, pk=pk)
    
    if relatorio.arquivo_pdf:
        response = HttpResponse(relatorio.arquivo_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{relatorio.titulo}.pdf"'
        return response
    else:
        # Se não houver PDF, gerar um novo
        ordens = Ordem.objects.filter(
            data_hora__date__gte=relatorio.data_inicio,
            data_hora__date__lte=relatorio.data_fim,
            status='concluido'
        )
        
        if ordens.count() > 0:
            # Gerar PDF temporário
            html_string = render_to_string('relatorios/pdf_template.html', {
                'relatorio': relatorio,
                'ordens': ordens,
                'data_geracao': timezone.now()
            })
            
            html = HTML(string=html_string)
            css = CSS(string='''
                @page {
                    size: letter;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                }
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .info {
                    margin-bottom: 20px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
                .total {
                    font-weight: bold;
                    text-align: right;
                    margin-top: 20px;
                }
            ''')
            
            # Criar PDF na memória
            pdf_file = html.write_pdf(stylesheets=[css])
            
            # Retornar como resposta HTTP
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{relatorio.titulo}.pdf"'
            return response
        
        # Se não houver ordens, redirecionar para a página de detalhes
        return redirect('relatorio_detail', pk=relatorio.pk)

@login_required
def relatorio_email(request, pk):
    """Envia o relatório por email"""
    relatorio = get_object_or_404(Relatorio, pk=pk)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            relatorio.email_destino = email
            relatorio.save()
            
            # Enviar email
            sucesso = enviar_relatorio_email(relatorio)
            
            if sucesso:
                return JsonResponse({'status': 'success', 'message': 'Relatório enviado com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Erro ao enviar o relatório.'})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'})

@login_required
def relatorio_graficos(request):
    """Exibe visualização gráfica dos dados"""
    # Obter parâmetros de filtro
    periodo = request.GET.get('periodo', 'mes')
    
    # Definir datas com base no período
    hoje = timezone.now().date()
    
    if periodo == 'dia':
        data_inicio = hoje
        data_fim = hoje
        label_periodo = 'do Dia'
    elif periodo == 'semana':
        # Início da semana (segunda-feira)
        data_inicio = hoje - timedelta(days=hoje.weekday())
        data_fim = hoje
        label_periodo = 'da Semana'
    elif periodo == 'mes':
        # Início do mês
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
        label_periodo = 'do Mês'
    elif periodo == 'ano':
        # Início do ano
        data_inicio = hoje.replace(month=1, day=1)
        data_fim = hoje
        label_periodo = 'do Ano'
    elif periodo == 'personalizado':
        # Datas personalizadas
        try:
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d').date()
            data_fim = datetime.strptime(request.GET.get('data_fim'), '%Y-%m-%d').date()
            label_periodo = f'de {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}'
        except (ValueError, TypeError):
            # Em caso de erro, usar mês atual
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
            label_periodo = 'do Mês'
    else:
        # Padrão: mês atual
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
        label_periodo = 'do Mês'
    
    # Gerar dados para gráficos
    dados_graficos = gerar_dados_graficos(data_inicio, data_fim)
    dados_graficos['label_periodo'] = label_periodo
    
    # Se for uma requisição AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(dados_graficos)
    
    # Renderizar template com dados
    return render(request, 'relatorios/relatorio_graficos.html', {
        'dados_graficos': json.dumps(dados_graficos),
        'periodo': periodo,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

def gerar_dados_graficos(data_inicio, data_fim):
    """Gera dados para gráficos com base no período"""
    # Obter ordens do período
    ordens = Ordem.objects.filter(
        data_hora__date__gte=data_inicio,
        data_hora__date__lte=data_fim,
        status='concluido'
    )
    
    # Calcular resumo
    total_ordens = ordens.count()
    valor_total = float(sum(ordem.valor_total for ordem in ordens))
    valor_descontos = float(sum(ordem.desconto for ordem in ordens))
    lucro = valor_total - valor_descontos
    
    # Dados por período (dia, semana, mês)
    delta = (data_fim - data_inicio).days
    
    if delta <= 31:  # Até 31 dias: agrupar por dia
        dados_por_periodo = []
        for i in range(delta + 1):
            data = data_inicio + timedelta(days=i)
            ordens_dia = ordens.filter(data_hora__date=data)
            
            valor_total_dia = float(sum(ordem.valor_total for ordem in ordens_dia))
            valor_descontos_dia = float(sum(ordem.desconto for ordem in ordens_dia))
            lucro_dia = valor_total_dia - valor_descontos_dia
            
            dados_por_periodo.append({
                'data': data.strftime('%d/%m'),
                'valor_total': valor_total_dia,
                'valor_descontos': valor_descontos_dia,
                'lucro': lucro_dia
            })
    else:  # Mais de 31 dias: agrupar por semana ou mês
        dados_por_periodo = []
        # Implementação simplificada: agrupar por mês
        meses = {}
        
        for ordem in ordens:
            data = ordem.data_hora.date()
            mes_key = data.strftime('%m/%Y')
            
            if mes_key not in meses:
                meses[mes_key] = {
                    'valor_total': 0,
                    'valor_descontos': 0,
                    'lucro': 0
                }
            
            meses[mes_key]['valor_total'] += float(ordem.valor_total)
            meses[mes_key]['valor_descontos'] += float(ordem.desconto)
            meses[mes_key]['lucro'] += float(ordem.valor_total - ordem.desconto)
        
        for mes, dados in meses.items():
            dados_por_periodo.append({
                'data': mes,
                'valor_total': dados['valor_total'],
                'valor_descontos': dados['valor_descontos'],
                'lucro': dados['lucro']
            })
    
    # Dados por forma de pagamento
    dados_pagamento = {
        'dinheiro': float(sum(ordem.valor_final for ordem in ordens.filter(forma_pagamento='dinheiro'))),
        'cartao_debito': float(sum(ordem.valor_final for ordem in ordens.filter(forma_pagamento='cartao_debito'))),
        'cartao_credito': float(sum(ordem.valor_final for ordem in ordens.filter(forma_pagamento='cartao_credito'))),
        'pix': float(sum(ordem.valor_final for ordem in ordens.filter(forma_pagamento='pix')))
    }
    
    # Dados por serviço
    servicos_count = {}
    for ordem in ordens:
        for item in ordem.itens.all():
            servico_id = item.servico.id
            servico_nome = item.servico.nome
            
            if servico_id not in servicos_count:
                servicos_count[servico_id] = {
                    'nome': servico_nome,
                    'quantidade': 0
                }
            
            servicos_count[servico_id]['quantidade'] += item.quantidade
    
    dados_servicos = [
        {'nome': dados['nome'], 'quantidade': dados['quantidade']}
        for servico_id, dados in servicos_count.items()
    ]
    
    # Ordenar por quantidade (decrescente)
    dados_servicos.sort(key=lambda x: x['quantidade'], reverse=True)
    
    # Limitar a 10 serviços mais realizados
    dados_servicos = dados_servicos[:10]
    
    return {
        'resumo': {
            'total_ordens': total_ordens,
            'valor_total': round(valor_total, 2),
            'valor_descontos': round(valor_descontos, 2),
            'lucro': round(lucro, 2)
        },
        'dados_por_periodo': dados_por_periodo,
        'dados_pagamento': dados_pagamento,
        'dados_servicos': dados_servicos
    }

def gerar_pdf_relatorio(relatorio, ordens):
    """Gera um arquivo PDF para o relatório"""
    # Renderizar template HTML
    html_string = render_to_string('relatorios/pdf_template.html', {
        'relatorio': relatorio,
        'ordens': ordens,
        'data_geracao': timezone.now()
    })
    
    # Configurar CSS
    css = CSS(string='''
        @page {
            size: letter;
            margin: 1cm;
        }
        body {
            font-family: Arial, sans-serif;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .info {
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        .total {
            font-weight: bold;
            text-align: right;
            margin-top: 20px;
        }
    ''')
    
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        # Gerar PDF
        HTML(string=html_string).write_pdf(tmp.name, stylesheets=[css])
    
    # Nome do arquivo
    filename = f"relatorio_{relatorio.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
    
    # Caminho para salvar
    filepath = os.path.join('relatorios', filename)
    
    # Retornar caminho relativo para salvar no modelo
    return filepath

def enviar_relatorio_email(relatorio):
    """Envia o relatório por email"""
    try:
        # Verificar se há email de destino
        if not relatorio.email_destino:
            return False
        
        # Verificar se há arquivo PDF
        if not relatorio.arquivo_pdf:
            # Gerar PDF se não existir
            ordens = Ordem.objects.filter(
                data_hora__date__gte=relatorio.data_inicio,
                data_hora__date__lte=relatorio.data_fim,
                status='concluido'
            )
            
            if ordens.count() > 0:
                relatorio.arquivo_pdf = gerar_pdf_relatorio(relatorio, ordens)
                relatorio.save()
        
        # Preparar email
        subject = f"Relatório: {relatorio.titulo}"
        message = f"""
        Olá,
        
        Segue em anexo o relatório "{relatorio.titulo}" referente ao período de {relatorio.data_inicio.strftime('%d/%m/%Y')} a {relatorio.data_fim.strftime('%d/%m/%Y')}.
        
        Resumo:
        - Total de ordens: {relatorio.total_ordens}
        - Valor total: R$ {relatorio.valor_total}
        - Descontos: R$ {relatorio.valor_descontos}
        - Lucro: R$ {relatorio.lucro}
        
        Atenciosamente,
        Equipe Guto Barber
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [relatorio.email_destino]
        
        # Criar email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list
        )
        
        # Anexar PDF
        if relatorio.arquivo_pdf:
            email.attach_file(os.path.join(settings.MEDIA_ROOT, relatorio.arquivo_pdf.name))
        
        # Enviar email
        email.send()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False
