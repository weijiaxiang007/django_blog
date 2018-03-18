from django.urls import path, re_path
from .views import IndexView,ArticleDetailView,CategoryView,DateView
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('index',IndexView.as_view(),name='index'),
    path('article/<int:article_id>',ArticleDetailView.as_view(),name='article'),
    path('category/<int:cate_id>',CategoryView.as_view(),name='category'),
    path('date/<int:year>/<int:month>',DateView.as_view(),name='date'),
    path('search/',views.article_search,name='search'),
    path('article/<int:article_id>/comment',views.comment_view,name='comment'),
    path('article/<int:article_id>/like',views.deal_like,name='like')
]
