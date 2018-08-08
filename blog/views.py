from django.shortcuts import render,get_object_or_404,HttpResponse,redirect,HttpResponsePermanentRedirect,reverse,HttpResponseRedirect
from django.contrib.auth.hashers import make_password,check_password
from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from .models import Post,User,Tag,Photo,Call_ip
import json
from datetime import timedelta
from datetime import timezone as T
import threading
from .email_token import token_confirm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import RegisterForm,LoginForm,CommentForm
from django.conf import settings
from django.template import loader
#from ratelimit.decorators import ratelimit

"""装饰器：获取ip访问次数"""
def call_ip_num(func):
    def zs(request,*args,**kwargs):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = ip.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        ip_count = Call_ip.objects.filter(ip_address=str(ip))
        if ip_count:
            obj = ip_count[0]
            obj.call_num += 1
        else:
            obj = Call_ip()
            obj.ip_address = ip
            obj.call_num = 1
        obj.save()
        return func(request,*args,**kwargs)
    return zs


"""多线程发送邮件"""
class Send_mail_thread(threading.Thread):
    def __init__(self,title,content,from_mail,get_mail,fail_silently=True):
        self.title = title
        self.content = content
        self.from_mail = from_mail
        self.get_mail = get_mail
        self.fail_silently  = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.title,self.content,self.from_mail,self.get_mail)
        email.content_subtype = "html"
        email.send(self.fail_silently)


"""注册激活认证函数"""
def active_user(request,token):
    try:
        global email
        email = token_confirm.confirm_validate_token(token)
    except:
        email = token_confirm.remove_validate_token(token)
        users = User.objects.filter(email=email)
        for user in users:
            user.delete()
        messages.info(request, "邮箱验证失败，请联系博主或者重新注册")
        return HttpResponsePermanentRedirect("/Reuser")
    try:
        user = User.objects.get(email=email)
        user.if_use = True
        user.save()
        response = HttpResponseRedirect("/")
        response.set_signed_cookie("email", email, salt="color", max_age=60 * 60 * 24 * 3)
        return response
    except:
        messages.info(request, "用户不存在，邮箱验证失败，请联系博主或者重新注册")
        return HttpResponsePermanentRedirect("/Reuser")


#获取标签列表放到搜索后的页面
def get_tags(request):
    Tags = Tag.objects.all()
    taglist = []
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email", salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    for i in Tags:
        dic = {}
        dic["tag"] = i.tag
        dic["Id"] = i.id
        taglist.append(dic)
        #response = json.dumps(taglist).encode('utf-8').decode('unicode_escape')
    dic = {}
    dic["taglist"] = taglist
    dic["coke"] = coke
    response = json.dumps(dic).encode('utf-8').decode('unicode_escape')
    return HttpResponse(response)
#@ratelimit(key="ip",rate="5/s",block=True)
#首页
@call_ip_num
def post_list(request):
    list = Post.published.all()
    tag_list = Tag.objects.all()
    paginator = Paginator(list,5)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email", salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    return render(request,"lw-index.html",{"posts":posts,"page":page,"tags":tag_list,"coke":coke})

'''文章详情'''
@call_ip_num
def post_detail(request,year,month,day,post):
    tag_list = Tag.objects.all()
    post = get_object_or_404(Post,slug=post,created__year = year,created__month=month,created__day = day)
    postId = post.id
    posts = Post.published.all().order_by("id")
    up = posts.filter(id__gt=postId).first()
    down = posts.filter(id__lt=postId).all().order_by("-id").first()
    tzutc_8 = T(timedelta(hours=8))
    if up:
        uu = up.title
        ur_cr = up.created
        ur_cr = ur_cr.astimezone(tzutc_8)
        up_year = str(ur_cr.year)
        up_month = ur_cr.strftime("%m")
        up_day = ur_cr.strftime("%d")
        up_slug = up.slug
        up_url = "/{}/{}/{}/{}/".format(up_year,up_month,up_day,up_slug)
    else:
        uu = None
        up_url = None
    if down:
        dd = down.title
        down_cr = down.created
        down_cr = down_cr.astimezone(tzutc_8)
        down_year = str(down_cr.year)
        down_month = down_cr.strftime("%m")
        down_day = down_cr.strftime("%d")
        down_slug = down.slug
        down_url = "/{}/{}/{}/{}/".format(down_year,down_month,down_day,down_slug)
    else:
        dd = None
        down_url = None
    comments = post.comments.filter(active=True).order_by("created")
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email",salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    return render(request,"lw-article-fullwidth.html",{"tags":tag_list,"post":post,"coke":coke,"comments":comments,"up_url":up_url,"down_url":down_url,"uu":uu,"dd":dd})
#存档
@call_ip_num
def artic(request):
    #post = Post.objects.datetimes("created","month",order="DESC")
    tag_list = Tag.objects.all()
    post = Post.article.all()
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email", salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    return render(request,"lw-timeline.html",{"tags":tag_list,"posts":post,"coke":coke})
#用户登录页面
@call_ip_num
def login(request):
    return render(request,"lw-log.html")
#用户注册页面
@call_ip_num
def register_page(request):
    return render(request,"lw-re.html")
#用户注册
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data.get("email")
            re = User.objects.filter(email=email)
            if len(re):
                for u in re:
                    if u.if_use:
                        messages.info(request,"该邮箱已被注册")
                    else:
                        u.delete()
                        passwd = data.get("passwd")
                        hash_pw = make_password(passwd)
                        user = User.objects.create(email=email, passwd=hash_pw)
                        user.save()
                        token = token_confirm.generate_validate_token(email)
                        link = '/'.join([settings.DOMAIN, 'activate', token])
                        data = {"email": email, "link": link}
                        email_message = loader.render_to_string("re_email.html", data)
                        title = "注册用户验证信息"
                        from_mail = settings.EMAIL_HOST_USER
                        get_mail = [email]
                        send_mail = Send_mail_thread(title, email_message, from_mail, get_mail)
                        send_mail.start()
                        messages.info(request, "欢迎注册，请登录自己的邮箱进行验证")
                return HttpResponsePermanentRedirect("/Reuser")#用户已存在
            else:
                passwd = data.get("passwd")
                hash_pw = make_password(passwd)
                user = User.objects.create(email=email,passwd = hash_pw)
                user.save()
                token = token_confirm.generate_validate_token(email)
                link = '/'.join([settings.DOMAIN,'activate',token])
                title = "注册用户验证信息"
                from_mail = settings.EMAIL_HOST_USER
                get_mail = [email]
                data = {"email":email,"link": link}
                email_message = loader.render_to_string("re_email.html", data)
                send_mail = Send_mail_thread(title, email_message, from_mail, get_mail)
                send_mail.start()
                messages.info(request, "欢迎注册，请登录自己的邮箱进行验证")
                return HttpResponsePermanentRedirect("/Reuser")
        else:
            messages.info(request,"邮箱或者密码格式不正确")
            return HttpResponsePermanentRedirect("/Reuser")#邮箱或者密码格式不正确
    else:
        return render(request,"404.html")

#用户登录
def sign(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data.get("email")
            passwd = data.get("passwd")
            try:
                user = User.objects.get(email=email)
            except:
                # 用户名不存在
                # return HttpResponse(json.dumps(0))
                messages.info(request, "用户名不存在")
                return HttpResponsePermanentRedirect("/login")
            if user:
                state = check_password(passwd,user.passwd)
                if state:
                    if user.if_use:
                        #登录
                        response = HttpResponseRedirect("/")
                        response.set_signed_cookie("email",email,salt="color",max_age=60*60*24*3)
                        return response
                    else:
                        messages.info(request, "您还没有进行邮箱验证，请通过邮箱验证后再登陆")
                        return HttpResponseRedirect("/login")
                else:
                    #密码错误
                    messages.info(request,"密码错误")
                    return HttpResponseRedirect("/login")
            else:
                #用户名不存在
                #return HttpResponse(json.dumps(0))
                messages.info(request,"用户名不存在")
                return HttpResponsePermanentRedirect("/login")
        else:
            #邮箱或者密码格式错误
            return HttpResponseRedirect(request,"邮箱或者密码格式错误")
    else:
        return render(request,"404.html")
'''发表评论'''
def pubcomment(request):
    if request.method == "POST":
        comment = CommentForm(data=request.POST)
        if comment.is_valid():
            new_comment = comment.save(commit=False)
            urr = request.META.get("HTTP_REFERER")#http://127.0.0.1:8000/blog/2016/06/06/ZY/
            #ur = urr.split("live/")[1]#2016/06/06/ZY/
            ur = urr.split(":8000/")[1]#2016/06/06/ZY/
            data = ur.split("/")
            year = data[0]
            month = data[1]
            day = data[2]
            slug = data[3]
            post = get_object_or_404(Post, slug=slug, created__year=year, created__month=month, created__day=day)
            new_comment.post = post
            c = request.COOKIES.get("email")
            if c:
                email = request.get_signed_cookie("email",salt="color")
                if email:
                    new_comment.email = email
                    new_comment.save()
                    return HttpResponsePermanentRedirect("/" + ur + "#wgw")
                else:
                    return HttpResponsePermanentRedirect("/login")
            else:
                return HttpResponsePermanentRedirect("/login")
        else:
            return render(request,"404.html")
    else:
        return render(request,"404.html")
#某分类
@call_ip_num
def tag(request,id):
    tag_list = Tag.objects.all()
    tag_obj = Tag.objects.get(id=id)
    postslist = tag_obj.post.filter(status="published")
    paginator = Paginator(postslist,5)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email", salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    return render(request,"lw-category-sidebar.html",{"tags":tag_list,"tag":tag_obj,"posts":posts,"page":page,"coke":coke})
#图片库
@call_ip_num
def photo(request):
    tag_list = Tag.objects.all()
    photos = Photo.objects.all().order_by("-created")
    c = request.COOKIES.get("email")
    if c:
        useremail = request.get_signed_cookie("email", salt="color")
        if useremail:
            coke = 1
        else:
            coke = 0
    else:
        coke = 0
    print(coke)
    return render(request,"lw-img.html",{"tags":tag_list,"photos":photos,"coke":coke})