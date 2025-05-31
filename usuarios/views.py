from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    """
    View personalizada para login de usuários
    """
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomLoginForm
    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha incorretos. Tente novamente.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    """
    View personalizada para logout de usuários
    """
    next_page = reverse_lazy('home')

class RegisterView(CreateView):
    """
    View para registro de novos usuários
    """
    template_name = 'usuarios/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Criar perfil para o usuário
        user = self.object
        from usuarios.models import Perfil
        Perfil.objects.create(usuario=user)
        messages.success(self.request, 'Conta criada com sucesso! Bem-vindo ao sistema.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar conta. Verifique os dados e tente novamente.')
        return super().form_invalid(form)

@login_required
def profile_view(request):
    """
    View para exibir e editar perfil do usuário
    """
    return render(request, 'usuarios/profile.html')

# @login_required
# def dashboard_view(request):
#     """
#     View para o painel principal após login
#     """
#     context = {
#         'title': 'Painel de Controle',
#     }
#     return render(request, 'core/dashboard.html', context)
