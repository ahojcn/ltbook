# Generated by Django 3.0.1 on 2019-12-29 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=128, unique=True, verbose_name='邮箱')),
                ('name', models.CharField(max_length=128, verbose_name='姓名')),
                ('gender', models.SmallIntegerField(choices=[(0, '保密'), (1, '男'), (2, '女')], default=0, verbose_name='性别')),
                ('pwd', models.CharField(max_length=256, verbose_name='密码')),
                ('tel', models.CharField(max_length=64, verbose_name='手机号')),
                ('reg_time', models.DateTimeField(auto_now_add=True, verbose_name='注册时间')),
                ('avatar', models.TextField(default='/static/img/avatar/default_avatar.jpg', verbose_name='头像')),
                ('is_active', models.BooleanField(default=False, verbose_name='是否激活')),
            ],
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='姓名')),
                ('tel', models.CharField(max_length=64, verbose_name='电话')),
                ('email', models.CharField(max_length=128, verbose_name='邮箱')),
                ('addr', models.CharField(max_length=1024, verbose_name='地址')),
                ('add_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.UserBase', verbose_name='所属用户')),
            ],
        ),
    ]
