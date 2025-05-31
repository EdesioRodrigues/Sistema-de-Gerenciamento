from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Servico
from .forms import ServicoForm

@login_required
def servico_list(request):
    """
    View para listar todos os serviços
    """
    servicos = Servico.objects.all()
    context = {
        'servicos': servicos,
        'title': 'Serviços'
    }
    return render(request, 'servicos/servico_list.html', context)

@login_required
def servico_create(request):
    """
    View para criar um novo serviço
    """
    if request.method == 'POST':
        form = ServicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço criado com sucesso!')
            return redirect('servico_list')
    else:
        form = ServicoForm()
    
    context = {
        'form': form,
        'title': 'Novo Serviço'
    }
    return render(request, 'servicos/servico_form.html', context)

@login_required
def servico_update(request, pk):
    """
    View para atualizar um serviço existente
    """
    servico = get_object_or_404(Servico, pk=pk)
    
    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço atualizado com sucesso!')
            return redirect('servico_list')
    else:
        form = ServicoForm(instance=servico)
    
    context = {
        'form': form,
        'servico': servico,
        'title': 'Editar Serviço'
    }
    return render(request, 'servicos/servico_form.html', context)

@login_required
def servico_delete(request, pk):
    """
    View para excluir um serviço
    """
    servico = get_object_or_404(Servico, pk=pk)
    
    if request.method == 'POST':
        servico.delete()
        messages.success(request, 'Serviço excluído com sucesso!')
        return redirect('servico_list')
    
    context = {
        'servico': servico,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'servicos/servico_confirm_delete.html', context)
