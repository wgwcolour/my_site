from django.contrib import admin

# Register your models here.
from .models import Post,User,Comment,Tag,Photo_tag,Photo,Call_ip
class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'author', 'publish','status')
	list_filter = ('status', 'created', 'publish', 'author')
	search_fields = ('title', 'body')
	prepopulated_fields = {'slug': ('title',)}
	raw_id_fields = ('author',)
	date_hierarchy = 'publish'
	ordering = ['status', 'publish']
class Call_ips(admin.ModelAdmin):
	list_display = ('ip_address','call_num')
admin.site.register(Post,PostAdmin)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Photo_tag)
admin.site.register(Photo)
admin.site.register(Call_ip,Call_ips)