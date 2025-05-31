from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm

@login_required
def cliente_list(request):
    """
    View para listar todos os clientes
    """
    clientes = Cliente.objects.all()
    context = {
        'clientes': clientes,
        'title': 'Clientes'
    }
    return render(request, 'clientes/cliente_list.html', context)

@login_required
def cliente_create(request):
    """
    View para criar um novo cliente
    """
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'title': 'Novo Cliente'
    }
    return render(request, 'clientes/cliente_form.html', context)

@login_required
def cliente_update(request, pk):
    """
    View para atualizar um cliente existente
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': 'Editar Cliente'
    }
    return render(request, 'clientes/cliente_form.html', context)

@login_required
def cliente_detail(request, pk):
    """
    View para visualizar detalhes de um cliente
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    ordens = cliente.ordens.all()
    
    context = {
        'cliente': cliente,
        'ordens': ordens,
        'title': f'Cliente: {cliente.nome}'
    }
    return render(request, 'clientes/cliente_detail.html', context)

@login_required
def cliente_delete(request, pk):
    """
    View para excluir um cliente
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('cliente_list')
    
    context = {
        'cliente': cliente,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'clientes/cliente_confirm_delete.html', context)
