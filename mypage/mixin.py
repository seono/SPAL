from django.db import models
from db import settings
import time

class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class TagManager(models.Manager):
    def get_queryset(self):
        return super(TagManager, self).get_queryset()



class Postable(TimeStampedMixin):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='작성자',related_name='%(class)s_create', on_delete=models.CASCADE)
    content = models.TextField(max_length=100,blank=True, verbose_name='내용')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='%(class)s_like', blank=True)
    
    class Meta:
        abstract=True

    def __str__(self):
        return self.author.user_name + " " + self.created.strftime("%Y-%m-%d %H:%M:%S")

    def get_absolute_url(self):
        return reverse('mypage:photo_detail', args=[str(self.id)])