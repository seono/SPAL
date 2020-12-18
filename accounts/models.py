from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
# Create your models here.

def get_path(instance, filename):
    return 'media/user_img/{:%Y/%m/%d}/{}'.format(timezone.localtime(), filename)

class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, user_id, user_name, password=None):
        if not user_id :
            raise ValueError('must have user id')
        user = self.model(
            user_id = user_id,
            user_name = user_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, user_name, password):

        user = self.create_user(
            user_id = user_id,
            user_name = user_name,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Man'),
        ('W', 'Woman'),
    )
    objects = UserManager()

    user_id = models.CharField(max_length=30, unique=True, primary_key=True)
    user_name = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    user_image = models.ImageField(upload_to=get_path, verbose_name='사진')
    user_profile = models.TextField(max_length=100, blank=True, null=True)
    follow = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='Relation',
        related_name='+'
    )
    
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['user_name']

    def getImage(self):
        if not self.user_image:
            return '/media/user_img/default.jpg'
        else:
            return self.user_image.url

class Relation(models.Model):
    RELATION_TYPE_FOLLOWING = 'f'
    RELATION_TYPE_BLOCK = 'b'
    CHOICE_TYPE = (
        (RELATION_TYPE_FOLLOWING, '팔로잉'),
        (RELATION_TYPE_BLOCK, '차단'),
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='from_user',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_user'
    )
    type = models.CharField(max_length=1,choices=CHOICE_TYPE)
    