from django.db import models
from django.urls import reverse
from .mixin import *
from db import settings
from django.utils import timezone

def get_path(instance, filename):
    return 'media/feed/{:%Y/%m/%d}/{}'.format(timezone.localtime(), filename)

class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset()



class Dstagram(Postable):
    pass
class Search(models.Model):
    search = models.CharField(max_length=100)

class DstagramPhoto(TimeStampedMixin):
    photo = models.ImageField(upload_to=get_path, verbose_name='사진')
    dstagram = models.ForeignKey('mypage.Dstagram',
                            on_delete=models.CASCADE,
                            related_name='photos',
                            verbose_name='디스타그램')


class Tag(models.Model):
    name = models.CharField(max_length=10, default=None, null=True, blank=True)
    dstagram = models.ForeignKey('mypage.Dstagram',
                            related_name='tags',
                            default=None, null=True, blank=True,
                            on_delete=models.CASCADE,
                            verbose_name='디스타그램')
    objects = TagManager()

class Comment(Postable):
    dstagram = models.ForeignKey('mypage.Dstagram',
                            related_name='comments',
                            default=None, null=True, blank=True,
                            on_delete=models.CASCADE,
                            verbose_name='디스타그램')
    p_comment = models.ForeignKey('self',
                            blank=True, null=True,
                            on_delete=models.CASCADE)
    objects = CommentManager()
    
    def __str__(self):
        return self.content
        