# Generated by Django 3.0.6 on 2020-06-11 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0008_comment_p_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dstagram',
            name='p_type',
        ),
    ]
