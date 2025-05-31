from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from .models import Ordem, ItemOrdem
from .forms import OrdemForm, ItemOrdemFormSet
from servicos.models import Servico
from clientes.models import Cliente
from decimal import Decimal

@login_required
def ordem_list(request):
    ordens = Ordem.objects.all().order_by('-data_hora')
    return render(request, 'ordens/ordem_list.html', {'ordens': ordens})

@login_required
def ordem_detail(request, pk):
    ordem = get_object_or_404(Ordem, pk=pk)
    return render(request, 'ordens/ordem_detail.html', {'ordem': ordem})

@login_required
def ordem_create(request):
    if request.method == 'POST':
        form = OrdemForm(request.POST)
        formset = ItemOrdemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            ordem = form.save(commit=False)
            cliente_nome = request.POST.get("cliente_nome_avulso", "").strip()
            cliente = Cliente.objects.filter(nome__iexact=cliente_nome).first()

            if cliente:
                ordem.cliente = cliente
                ordem.nome_cliente_avulso = ""
            else:
                ordem.cliente = None
                ordem.nome_cliente_avulso = cliente_nome

            ordem.criado_por = request.user
            ordem.save()

            formset.instance = ordem
            formset.save()

            return redirect('ordem_detail', pk=ordem.pk)
    else:
        form = OrdemForm()
        formset = ItemOrdemFormSet()

    servicos = Servico.objects.filter(ativo=True).values('id', 'nome', 'preco')
    clientes = Cliente.objects.all().values_list('nome', flat=True)

    return render(request, 'ordens/ordem_form.html', {
        'form': form,
        'formset': formset,
        'servicos': list(servicos),
        'clientes_nomes': list(clientes),
    })

@login_required
def ordem_update(request, pk):
    ordem = get_object_or_404(Ordem, pk=pk)

    if request.method == 'POST':
        form = OrdemForm(request.POST, instance=ordem)
        formset = ItemOrdemFormSet(request.POST, instance=ordem)

        if form.is_valid() and formset.is_valid():
            ordem = form.save(commit=False)
            cliente_nome = request.POST.get("cliente_nome_avulso", "").strip()
            cliente = Cliente.objects.filter(nome__iexact=cliente_nome).first()

            if cliente:
                ordem.cliente = cliente
                ordem.nome_cliente_avulso = ""
            else:
                ordem.cliente = None
                ordem.nome_cliente_avulso = cliente_nome

            ordem.save()
            formset.save()

            return redirect('ordem_detail', pk=ordem.pk)
    else:
        form = OrdemForm(instance=ordem)
        formset = ItemOrdemFormSet(instance=ordem)

    servicos = Servico.objects.filter(ativo=True).values('id', 'nome', 'preco')
    clientes = Cliente.objects.all().values_list('nome', flat=True)

    return render(request, 'ordens/ordem_form.html', {
        'form': form,
        'formset': formset,
        'servicos': list(servicos),
        'clientes_nomes': list(clientes),
        'ordem': ordem
    })

@login_required
def ordem_delete(request, pk):
    ordem = get_object_or_404(Ordem, pk=pk)

    if request.method == 'POST':
        ordem.delete()
        return redirect('ordem_list')

    return render(request, 'ordens/ordem_confirm_delete.html', {'ordem': ordem})

@login_required
def get_servico_info(request, servico_id):
    try:
        servico = Servico.objects.get(pk=servico_id)
        return JsonResponse({
            'nome': servico.nome,
            'preco': float(servico.preco),
            'duracao': servico.duracao
        })
    except Servico.DoesNotExist:
        return JsonResponse({'error': 'Serviço não encontrado'}, status=404)
