from django.conf.urls import url
from . import views
app_name = "blog"
urlpatterns = [
    url(r"^$",views.post_list,name="post_list"),
    #url(r'^$',views.PostListView.as_view(),name="post_list"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$',
        views.post_detail,
        name='post_detail'),
    url(r'^artic',views.artic,name="artic"),
    url(r'^login',views.login,name="login"),
    url(r"^register$",views.register,name="register"),
    url(r"^sign",views.sign,name = "sign"),
    url(r'^pubcomment',views.pubcomment,name="pubcomment"),
    url(r"^tag/(?P<id>\d{1})/",views.tag,name="tag"),
    url(r"^photo",views.photo,name="photo"),
    url(r"^Reuser$",views.register_page,name="register_page"),
    url(r"tag$",views.get_tags,name="get_tags"),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$',views.active_user,name='active_user'),
]