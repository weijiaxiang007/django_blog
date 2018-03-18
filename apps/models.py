#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

class Article(models.Model):
    STATUS_CHOICES = (
        ('d', 'part'),
        ('p', 'Published'),
    )  # 文章的状态

    title = models.CharField('标题', max_length=100)
    content = RichTextUploadingField()
    author = models.ForeignKey(User,verbose_name='作者',max_length=20,on_delete=models.DO_NOTHING)
    # 目录分类
    category = models.ForeignKey('Category', verbose_name='分类',
                                 null=True, on_delete=models.DO_NOTHING,related_name='article')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    # auto_now_add : 创建时间戳，不会被覆盖

    last_modified_time = models.DateTimeField('修改时间', auto_now=True)
    # auto_now: 自动将当前时间覆盖之前时间

    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES)

    # 阅读量
    views = models.PositiveIntegerField('浏览量', default=0)
    # 点赞数
    likes = models.PositiveIntegerField('点赞数', default=0)
    # 是否置顶
    topped = models.BooleanField('置顶', default=False)
    # 标签云
    tags = models.ManyToManyField('Tag',verbose_name='标签集合',blank=True)

    def __str__(self):
        return self.title

    #分页时用到 -表示逆序
    class Meta:
        ordering = ['-created_time']

class Category(models.Model):
    """
    另外一个表,储存文章的分类信息
    文章表的外键指向
    """
    category = models.CharField('类名',max_length=20)
    create_time = models.DateTimeField('创建时间',auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.category

class ArticleComment(models.Model):
    """
    评论信息
    """
    user_name = models.CharField('评论者名字',max_length=100,default='Anouymous')
    body = models.TextField('评论内容',max_length=300)
    created_time = models.DateTimeField('评论发表时间',auto_now_add=True)
    article = models.ForeignKey('Article',verbose_name='评论所属文章',on_delete=True)

    def __str__(self):
        return self.body[:20]

class Tag(models.Model):
    """
    tag(标签云)
    """
    name = models.CharField('标签云',max_length=20)
    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    last_modified_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.name
