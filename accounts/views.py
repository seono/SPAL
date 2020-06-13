from django.shortcuts import render
from .forms import RegisterForm
from django.contrib import auth
from django.views.generic.edit import CreateView
from .models import User
from django.urls import reverse_lazy
# Create your views here.

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:done')
    template_name = 'registration/register.html'
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        if self.request.FILES:
            for f in self.request.FILES.getlist('user_image'):
                user.user_image = f
        user.save()
        return super(RegisterView, self).form_valid(form)

def register_done(request):
    return render(request, 'registration/register_done.html')