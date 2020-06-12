from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, DeleteView, CreateView
from django.views.generic.list import ListView
# Create your views here.
from mypage.models import DstagramPhoto, Comment, Dstagram
from mypage.forms import CommentForm
from django.http import HttpResponseForbidden,HttpResponseRedirect

from django.contrib.auth.mixins import LoginRequiredMixin       #권한 제한하는 건데 @login_required라는 decorator는 함수형 (def)뷰에서 사용 지금은 클래스 형 뷰->Mixin사용
from django.db.models import Q, Count
from django.utils import timezone

class PhotoListView(FormMixin,LoginRequiredMixin,ListView):
    template_name="home/list.html"
    form_class = CommentForm
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)

        context['comment_form'] = self.get_form()
        return context

    def get_queryset(self):
        l = self.kwargs.get('list_num')
        now = timezone.now()
        year = now.year
        month = now.month
        where = '%(year)s>=YEAR(created) AND %(month)s<=MONTH(created)'%\
            {'year':year, 'month':month}
        if l == 1:
            dstagram = Dstagram.objects.all()\
            .annotate(
                like_count=Count('likes')
            ).order_by("-like_count")
            print(dstagram)
            queryset = dstagram\
            .prefetch_related('photos')\
            .prefetch_related('comments__author')\
            .select_related('author')
            print(queryset)
        elif l == 3:
            dstagram = Dstagram.objects.extra(where=[where])
            queryset = Dstagram.objects\
            .prefetch_related('photos')\
            .prefetch_related('comments__author')\
            .select_related('author')\
            .annotate(
                like_count=Count('likes')
            ).order_by("-like_count")
        else:
            queryset = Dstagram.objects\
                .prefetch_related('photos')\
                .prefetch_related('comments__author')\
                .select_related('author')\
                .order_by('-created','-updated')
        return queryset

class PhotoDetailView(LoginRequiredMixin,DetailView):
    model = DstagramPhoto
    template_name='home/detail.html'


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        to = self.request.POST.get('next','/')
        return to

class CommentCreateView(CreateView):
     model = Comment
     fields = ['content']
     template_name = 'home/list.html'

     def form_valid(self, form):
          comment = form.save(commit=False)
          comment.author = self.request.user
          comment.dstagram = Dstagram.objects.get(pk=self.kwargs.get('comment_id'))
          comment.save()
          return HttpResponseRedirect(self.request.POST.get('next', '/'))

class CCCommentCreateView(CreateView):
     model = Comment
     fields = ['content']
     template_name = 'home/list.html'

     def form_valid(self, form):
          comment = form.save(commit=False)
          comment.author = self.request.user
          print("Here")
          comment.p_comment = Comment.objects.get(pk=self.kwargs.get('comment_id'))
          comment.save()
          return HttpResponseRedirect(self.request.POST.get('next', '/'))


class PhotoLike(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:    #로그인확인
            return HttpResponseForbidden()
        else:
            if 'post_id' in kwargs:
                post_id = kwargs['post_id']
                post = Dstagram.objects.get(pk=self.kwargs.get('post_id'))
                user = request.user
                if user in post.likes.all():
                    post.likes.remove(user)
                else:
                    post.likes.add(user)
            referer_url = request.META.get('HTTP_REFERER')
            path = urlparse(referer_url).path
            return HttpResponseRedirect(path)