from django.contrib import admin
from .models import Article,Category
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id','title','author','category',
                    'created_time','last_modified_time','status','likes')
    ordering = ('id',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','category','create_time','last_modified_time')
    ordering = ('id',)

admin.site.register(Article,ArticleAdmin)
admin.site.register(Category,CategoryAdmin)

