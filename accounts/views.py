from django.shortcuts import render
from .forms import RegisterForm
from django.contrib import auth
from django.views.generic.edit import CreateView
from .models import User
from django.urls import reverse_lazy
# Create your views here.

# def login(request):
#     # 해당 쿠키에 값이 없을 경우 None을 return 한다.
#     if request.COOKIES.get('username') is not None:
#         username = request.COOKIES.get('username')
#         password = request.COOKIES.get('password')
#         user = auth.authenticate(request, username=username, password=password)
#         if user is not None:
#             auth.login(request, user)
#             return redirect("home:list")  
#         else:
#             return render(request, "registration/login.html")

#     elif request.method == "POST":
#         username = request.POST["username"]
#         password = request.POST["password"]
#         # 해당 user가 있으면 username, 없으면 None
#         user = auth.authenticate(request, username=username, password=password)

#         if user is not None:
#             auth.login(request, user)
#             if request.POST.get("keep_login") == "TRUE":
#                 response = render(request, 'registration/login.html')
#                 response.set_cookie('username',username)
#                 response.set_cookie('password',password)
#                 return response
#             return redirect("home:list")
#         else:
#             return render(request, 'registration/login.html', {'error':'username or password is incorrect'})
#     else:
#         return render(request, 'registration/login.html')
#     return render(request, 'registration/login.html') 

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
# def register(request):
#     if request.method == 'POST':                                                                #회원 가입 정보가 전달
#         user_form = RegisterForm(request.POST)                                                  #RegisterForm으로 유효성 검사
#         if user_form.is_valid():
#             new_user = user_form.save(commit=False)                                             #commit=False -> 데이터베이스에 넘기지 않음 객체만 만들어짐
#             new_user.set_password(user_form.cleaned_data['password'])                           #비밀번호 지정 + 암호화
#             new_user.save()
#             if request.FILES:
#                 print("here")
#                 f = request.FILES.get('user_image')                                                                     #실제로 데이터베이스에 저장
#             return render(request, 'registration/register_done.html', {'new_user':new_user})

#     else:
#         user_form = RegisterForm()                                                              

#     return render(request, 'registration/register.html',{'form':user_form})