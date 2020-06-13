from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, DeleteView, CreateView
from django.views.generic.list import ListView
# Create your views here.
from mypage.models import DstagramPhoto, Comment, Dstagram, Tag
from mypage.forms import CommentForm
from django.http import HttpResponseForbidden,HttpResponseRedirect
from db import settings
from django.contrib.auth.mixins import LoginRequiredMixin       #권한 제한하는 건데 @login_required라는 decorator는 함수형 (def)뷰에서 사용 지금은 클래스 형 뷰->Mixin사용
from django.db.models import Q, Count
from django.utils import timezone
from accounts.models import User

from django.db import connection,transaction
cursor = connection.cursor()

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
        where = '%(year)s>=YEAR(O.created) AND %(month)s<=MONTH(O.created)'%\
            {'year':year, 'month':month}
        print(where)
        if l == 1:
            dstagram = Dstagram.objects.raw(
                "SELECT * from mypage_dstagram O,\
                (SELECT dstagram_id, count(*) as like_count from mypage_dstagram_likes group by dstagram_id)\
                     S where  O.id = S.dstagram_id order by like_count desc"
            )
            queryset = dstagram\
            .prefetch_related('photos')\
            .prefetch_related('comments__author')
        elif l == 3:
            dstagram = Dstagram.objects.raw(
                "SELECT * from mypage_dstagram O, \
                    (SELECT dstagram_id, count(*) as like_count from mypage_dstagram_likes group by dstagram_id) S\
                        where '%s' and O.id = S.dstagram_id order by like_count desc" % where
            )
            queryset = dstagram\
            .prefetch_related('photos')\
            .prefetch_related('comments__author')
        else:
            dstagram = Dstagram.objects.raw(
                "SELECT * from mypage_dstagram order by created desc, updated desc"
            )
            queryset = dstagram\
                .prefetch_related('photos')\
                .prefetch_related('comments__author')
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
        now = timezone.now()
        query = "insert into mypage_comment(content, author_id, created, updated, dstagram_id)\
             values('%s', '%s', '%s', '%s','%s')" %(comment.content, self.request.user.user_id,now,now,self.kwargs.get('comment_id'))
        cursor.execute(query)
        return HttpResponseRedirect(self.request.POST.get('next', '/'))

class CCCommentCreateView(CreateView):
     model = Comment
     fields = ['content']
     template_name = 'home/list.html'
     def form_valid(self, form):
        comment = form.save(commit=False)
        now = timezone.now()
        query = "insert into mypage_comment(content, author_id, created, updated, p_comment_id)\
            values('%s', '%s', '%s', '%s','%s')" %(comment.content, self.request.user.user_id,now,now,self.kwargs.get('comment_id'))
        cursor.execute(query)
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
    
class SearchView(FormMixin,LoginRequiredMixin,ListView):
    template_name="home/list.html"
    form_class = CommentForm
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        context['comment_form'] = self.get_form()
        return context

    def get_queryset(self):
        queryset = None
        if 'q' in self.request.GET:
            word = self.request.GET.get('q')
            post = Dstagram.objects.all()
            if word[0] == '#':
                t = word[1:len(word)]
                post = Dstagram.objects.raw(
                    "SELECT * from mypage_dstagram P\
                         where P.id IN (select dstagram_id from mypage_tag t where t.name like '%s') \
                             order by created desc, updated desc" % t
                )
                queryset = post.prefetch_related('photos')\
                    .prefetch_related('comments__author')
            else:
                post = Dstagram.objects.raw(
                    "SELECT * from mypage_dstagram P \
                        where P.author_id IN (select user_id from accounts_user t where t.user_name like '%s')\
                             order by created desc, updated desc" % word
                )
                queryset = post.prefetch_related('photos')\
                    .prefetch_related('comments__author')
                return queryset
        else:        
            post = Dstagram.objects.raw(
                "SELECT * from mypage_dstgram order by created desc, updated desc"
            )
            queryset = post.prefetch_related('photos')\
                .prefetch_related('comments__author')
        return queryset