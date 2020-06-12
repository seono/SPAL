from django.urls import path
from django.contrib.auth import views as auth_view
from .views import RegisterView, register_done

app_name='accounts'

urlpatterns = [
    path('login/', auth_view.LoginView.as_view(), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register_done/', register_done, name='done')
]