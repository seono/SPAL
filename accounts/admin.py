from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    fields=['user_name','user_id','user_image','is_staff','is_active']

admin.site.register(User)