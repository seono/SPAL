from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from .models import DstagramPhoto, Comment, Dstagram, Tag
from django.http import HttpResponseForbidden,HttpResponseRedirect, HttpResponse
from urllib.parse import urlparse
from .forms import DstagramForm,CommentForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin       #권한 제한하는 건데 @login_required라는 decorator는 함수형 (def)뷰에서 사용 지금은 클래스 형 뷰->Mixin사용
from django.db.models import Q
from accounts.models import User, Relation
import re
from django.core.exceptions import ObjectDoesNotExist
from .colortag import *
from django.db import connection,transaction
from django.utils import timezone
cursor = connection.cursor()

class UserPostListView(FormMixin,LoginRequiredMixin,ListView):
    template_name="photo/user_page.html"
    form_class = CommentForm
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)

        context['comment_form'] = self.get_form()
        user = User.objects.get(pk=self.kwargs.get('user_id'))
        me = self.request.user
        
        try:
            f_list = Relation.objects.filter(from_user=me, to_user=user, type='f')
            if f_list:
                context['is_follow'] = True
            else:
                context['is_follow'] = False
        except AttributeError:
            context['is_follow'] = False
        context['follows'] = me.to_user.filter(type='f').count()
        context['followers'] = user.to_user.filter(type='f').count()
        context['diff_user'] = user
        return context

    def get_queryset(self):
        queryset = None
        user = User.objects.get(pk=self.kwargs.get('user_id'))
        post = Dstagram.objects.raw(
            "SELECT * from mypage_dstagram where author_id like '%s' order by created desc, updated desc"%user.user_id
        )
        queryset = post.prefetch_related('photos').prefetch_related('comments__author')
        return queryset

class PhotoListView(FormMixin,LoginRequiredMixin,ListView):
    template_name="photo/my_page.html"
    form_class = CommentForm
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)

        context['comment_form'] = self.get_form()
        return context

    def get_queryset(self):
        queryset = None       
        post = Dstagram.objects.raw(
            "SELECT * from mypage_dstagram where author_id like '%s' order by created desc, updated desc"%self.request.user.user_id
        )
        queryset = post.prefetch_related('photos').prefetch_related('comments__author')
        return queryset

class PhotoUploadView(LoginRequiredMixin,CreateView):
    model = Dstagram
    form_class = DstagramForm
    success_url = reverse_lazy('mypage:mypage')
    template_name = 'photo/upload.html'                         #사용할 템플릿

    def form_valid(self, form):
        dstagram = form.save(commit=False)
        dstagram.author = self.request.user
        content = self.request.POST.get('content')
        #tag 인식
        p = re.compile('#[^\s\t\n\f\v#]{1,10}')
        tags = p.findall(content)
        # dstagram.content = content
        # dstagram.save()
        now = timezone.now()
        query = "insert into mypage_dstagram(content, author_id, created, updated) values('%s', '%s', '%s', '%s')" %(content, self.request.user.user_id, now,now)
        cursor.execute(query)
        cursor.execute("SELECT * from mypage_dstagram where created = '%s'"%now)
        row = cursor.fetchone()
        id = int(row[0])
        for i, tag in enumerate(tags):
            tags[i] = tag[1:len(tag)]
        for tag in tags:
            query = "insert into mypage_tag(name, dstagram_id) values('%s','%d')"%(tag,id)
            cursor.execut(query)
        if self.request.FILES:
            for i,f in enumerate(self.request.FILES.getlist('images')):
                # rgb color 추출
                if i == 0:
                    c_tags = color(f)
                    if len(c_tags)>0:
                        for cs in c_tags:
                            query = "insert into mypage_tag(name, dstagram_id) values('%s','%d')"%(cs,id)  
                dstagram = Dstagram.objects.get(id=id)
                feed_photo = DstagramPhoto(dstagram=dstagram, photo=f)
                feed_photo.save()
        return super(PhotoUploadView, self).form_valid(form)


class PhotoDeleteView(LoginRequiredMixin,DeleteView):
    model = DstagramPhoto
    success_url = '/'
    template_name = 'photo/delete.html'

class PhotoUpdateView(LoginRequiredMixin,UpdateView):
    model = DstagramPhoto
    fields = ['photo','text']
    template_name = 'photo/update.html'

class PhotoDetailView(LoginRequiredMixin,DetailView):
    model = DstagramPhoto
    template_name = 'photo/detail.html'

class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        to = self.request.POST.get('next','/')
        return to

class CommentCreateView(CreateView):
    model = Comment
    fields = ['content']
    template_name = 'photo/user_page.html'


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
     template_name = 'photo/user_page.html'

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


class CommentLike(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:    #로그인확인
            return HttpResponseForbidden()
        else:
            if 'comment_id' in kwargs:
                comment_id = kwargs['comment_id']
                comment = Comment.objects.get(pk=self.kwargs.get('comment_id'))
                user = request.user
                if user in comment.likes.all():
                    query = "DELETE from mypage_comment_likes where user_id = '%s'"%user.user_id
                    cursor.execute(query)
                else:
                    query = "INSERT INTO mypage_comment_likes(comment_id, user_id) values(%d, '%s')"%(comment_id, user.user_id)
                    cursor.execute(query)
            referer_url = request.META.get('HTTP_REFERER')
            path = urlparse(referer_url).path
            return HttpResponseRedirect(path)

class UserFollow(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:    #로그인확인
            return HttpResponseForbidden()
        else:
            if 'user_id' in kwargs:
                user_id = kwargs['user_id']
                user = User.objects.get(pk=self.kwargs.get('user_id'))
                me = request.user
                query_del = "DELETE FROM accounts_relation where type like 'f' and from_user_id like '%s' and to_user_id like'%s'"%(me.user_id, user.user_id)
                query_in = "INSERT INTO accounts_relation(type, from_user_id, to_user_id) values('f', '%s', '%s')"%(me.user_id, user.user_id)
                query_self = "SELECT * from accounts_relation where type like 'f' and from_user_id like '%s' and to_user_id like '%s'"%(me.user_id, user.user_id)
                cursor.execute(query_self)
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(query_in)
                else:
                    cursor.execute(query_del)
            referer_url = request.META.get('HTTP_REFERER')
            path = urlparse(referer_url).path
            return HttpResponseRedirect(path)
