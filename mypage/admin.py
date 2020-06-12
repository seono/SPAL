from django.contrib import admin
from .models import Comment, DstagramPhoto, Tag

class CommentAdmin(admin.ModelAdmin):
    model = Comment
    fields=['content','p_comment','id']

class DstagramAdmin(admin.ModelAdmin):
    model = DstagramPhoto
    fields=['dstagram__content','photo','id','created']

class TagAdmin(admin.ModelAdmin):
    model = Tag
    fields=['name','dstagram__id','dstagram__content']

admin.site.register(Comment)
admin.site.register(DstagramPhoto)
admin.site.register(Tag)