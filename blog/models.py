from django.db import models
from django.urls import reverse
# Create your models here.
import os
from django.utils import timezone
from datetime import timedelta
from datetime import timezone as T
from django.contrib.auth.models import User
#from ..mysite.settings import MEDIA_ROOT
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile
from PIL import Image
#管理器 返回已发布文章
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')
#管理器 按归档日期返回
class Article(models.Manager):
    def get_queryset(self):
        list = []
        post_list = Post.published.order_by("-created")
        for i in post_list:
            dic = {}
            cr = i.created
            tzutc_8 = T(timedelta(hours=8))
            cr = cr.astimezone(tzutc_8)
            dic['created'] = str(cr.year) + "/" + cr.strftime("%m") + "/" + cr.strftime("%d")
            dic['year'] = cr.year
            dic['month'] = cr.month
            dic['title'] = i.title
            dic['author'] = i.author
            dic['slug'] = i.slug
            dic['tag'] = i.tag
            list.append(dic)
        return list
#访问IP表
class Call_ip(models.Model):
    ip_address = models.CharField(verbose_name="IP地址",max_length=30)
    call_num = models.IntegerField(verbose_name="访问次数",default=0)
    def __str__(self):
        return self.ip_address

#文章分类表
class Tag(models.Model):
    tag = models.CharField(max_length=30,unique=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta():
        ordering = ("-created",)
    def __str__(self):
        return self.tag
#文章表
class Post(models.Model):
    STATUS_CHOICES = (
        ("draft","Draft"),
        ("published","Published"),
    )
    title = models.CharField(max_length=250)
    img = models.ImageField(upload_to='image',null=True)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               related_name='blog_posts',on_delete=models.CASCADE)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    tag = models.ForeignKey(Tag,related_name="post",on_delete=models.CASCADE,default=1)
    class Meta():
        ordering = ("-publish",)
    def __str__(self):
        return self.title

    objects = models.Manager()
    published = PublishedManager()
    article = Article()
    def get_absolute_url(self):
        cr_time = self.created
        tzutc_8 = T(timedelta(hours=8))
        china_time = cr_time.astimezone(tzutc_8)
        return reverse("blog:post_detail",
                       args=[china_time.year,
                             china_time.strftime("%m"),
                             china_time.strftime("%d"),
                             self.slug])
#用户表
class User(models.Model):
    email = models.EmailField(unique=True)
    passwd = models.CharField(max_length=128)
    if_use = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    class Meta():
        ordering = ("-created",)
    def __str__(self):
        return self.email
#用户评论表
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments',on_delete=models.CASCADE)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    class Meta():
        ordering = ("-created",)
    def __str__(self):
        return '{}的评论-{}'.format(self.email,self.post)
#相册标签表
class Photo_tag(models.Model):
    tag = models.CharField(max_length=30,unique=True)
    remarks = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    class Meta():
        ordering = ("created",)
    def __str__(self):
        return "相册：{}".format(self.tag)
#上传图片后转缩略图
def make_thumb(path,size=1.6*1024*1024):
    filesize = os.path.getsize(path)
    f = Image.open(path)
    if filesize >= size:
        if len(f.split()) == 4:
        	r, g, b, a = f.split()
        	f = Image.merge("RGB", (r, g, b))
        width,height = f.size
        new_width = 1024
        new_height = int(new_width * height * 1.0 / width)
        f.thumbnail((new_width,new_height),Image.ANTIALIAS)
    return f

#相册表
class Photo(models.Model):
    photo = models.ImageField(upload_to="photo")
    remarks = models.CharField(max_length=36)
    created = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(Photo_tag,
                            on_delete=models.CASCADE,related_name="photos")
    photo_thumb = models.ImageField(upload_to="photo_thumb",null=True,blank=True)
    class Meta():
        ordering = ("created",)
    def __str__(self):
        return "照片：{}".format(self.remarks)

    def save(self):
        super(Photo,self).save()
        #base,ext = os.path.splitext(os.path.basename(self.photo.path))
        img_name = self.photo.name.split("/")[1]
        thumb_photo = make_thumb(os.path.join(settings.MEDIA_ROOT,"photo/" + img_name))
        thumb_path = os.path.join(settings.MEDIA_ROOT,"photo_thumb/" + img_name)
        thumb_photo.save(thumb_path)
        self.photo_thumb = ImageFieldFile(self,self.photo_thumb,"photo_thumb/" + img_name)
        super(Photo,self).save()