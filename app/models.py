from django.db import models


class UserBase(models.Model):
    """
    用户基本信息
    """
    USER_GENDER = (
        (0, '保密'),
        (1, '男'),
        (2, '女'),
    )
    email = models.CharField(max_length=128, unique=True, null=False, blank=False, verbose_name='邮箱')
    name = models.CharField(max_length=128, verbose_name='姓名')
    gender = models.SmallIntegerField(default=0, choices=USER_GENDER, verbose_name='性别')
    pwd = models.CharField(max_length=256, null=False, blank=False, verbose_name='密码')
    tel = models.CharField(max_length=64, verbose_name='手机号')
    reg_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    avatar = models.TextField(default='/static/img/avatar/default_avatar.jpg', verbose_name='头像')
    is_active = models.BooleanField(default=False, verbose_name='是否激活')


class AddressBook(models.Model):
    """
    通讯录表
    """
    user = models.ForeignKey(to=UserBase, on_delete=models.CASCADE, verbose_name='所属用户')

    name = models.CharField(max_length=128, null=False, blank=False, verbose_name='姓名')
    tel = models.CharField(max_length=64, verbose_name='电话')
    email = models.CharField(max_length=128, verbose_name='邮箱')
    addr = models.CharField(max_length=1024, verbose_name='地址')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')


class AreaInfo(models.Model):
    """
    地址模型类
    """
    # 地区名称
    atitle = models.CharField(verbose_name='标题', max_length=20)
    # 自关联属性
    aParent = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.atitle

    def title(self):
        return self.atitle

    title.admin_order_field = 'atitle'
    title.short_description = '地区名称'

    def parent(self):
        if self.aParent is None:
            return ''
        return self.aParent.atitle

    parent.short_description = '父级地区名称'
