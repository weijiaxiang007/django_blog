# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.db.models import Count
from django.conf import settings

import re,json
from .models import Article, Category, ArticleComment
from .forms import ArticleCommentForm
# Create your views here.

class PageFunc():
    # filter_list 是过滤后的列表

    def __init__(self,filter_list):
        self.paginator = Paginator(filter_list, settings.EACHE_PAGE)  # 每5篇博客为一页

    # page_num 是当前页码
    def get_pagintor_info(self,page_num):
        last_page = self.paginator.num_pages
        page_num = page_num
        current_page_num = self.paginator.get_page(page_num).number  # 获取当前页码
        # 获取当前页码前后各2页
        page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                     list(range(current_page_num, min(current_page_num + 2, last_page) + 1))

        # 加上省略号
        if page_range[0] - 1 >= 2:
            page_range.insert(0, '...')
        if last_page - page_range[-1] >= 2:
            page_range.append('...')
        # 加上首页和尾页
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != last_page:
            page_range.append(last_page)

        res = {
            'page_range' : page_range,
            'last_page'  : last_page,
        }

        return res

    def get_category_list(self):
        # 获取每个分类中有几篇博客
        categorys = Category.objects.all().order_by('category')
        categorys_list = []
        for category in categorys:
            category.count = Article.objects.filter(category=category).count()
            categorys_list.append(category)
        return categorys_list

    def get_date_list(self):
        # 按日期分类内容
        dates = Article.objects.dates('created_time', 'month', order='DESC')
        return dates

class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        page_num = self.request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
        article_list = PageFunc(Article.objects.filter(status='p')).paginator.get_page(page_num)
        return article_list

    def get_context_data(self, *, object_list=None, **kwargs):
        page_info = PageFunc(Article.objects.filter(status='p'))
        res = page_info.get_pagintor_info(self.request.GET.get("page", 1))

        kwargs["category_list"] = page_info.get_category_list()
        kwargs['page_range'] = res['page_range']
        kwargs['last_page'] = res['last_page']
        kwargs['date_list'] = page_info.get_date_list()
        return super(IndexView, self).get_context_data(**kwargs)

class ArticleDetailView(DetailView):
    """
    显示文章
    """
    model = Article
    template_name = 'article.html'
    context_object_name = 'article'

    # pk_url_kwarg用于接受来自url中的参数作为主键
    pk_url_kwarg = 'article_id'

    # 从数据库中获取id为pk_url_kwargs的对象
    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object()
        # 点击一次阅读量增加一次
        obj.views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        # 得到上一篇和下一篇博客
        current_blog = get_object_or_404(Article,pk=self.kwargs['article_id'])
        previous_blog = Article.objects.filter(created_time__gt=current_blog.created_time).last()
        next_blog = Article.objects.filter(created_time__lt=current_blog.created_time).first()
        comment_list = ArticleComment.objects.filter(article=current_blog)

        views = current_blog.views
        likes = current_blog.likes

        kwargs['comment_list'] = comment_list
        kwargs['previous_blog'] = previous_blog
        kwargs['next_blog'] = next_blog
        kwargs['views'] = views
        kwargs['likes'] = likes
        return super(ArticleDetailView,self).get_context_data(**kwargs)

class CategoryView(ListView):
    template_name = 'category.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        page_num = self.request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
        article_list = PageFunc(Article.objects.filter(category=self.kwargs['cate_id'], status='p')).paginator.get_page(page_num)
        return article_list

    def get_context_data(self, *, object_list=None, **kwargs):
        page_info = PageFunc(Article.objects.filter(category=self.kwargs['cate_id'], status='p'))
        res = page_info.get_pagintor_info(self.request.GET.get("page", 1))

        kwargs["category_list"] = page_info.get_category_list()
        kwargs['category'] = get_object_or_404(Category, pk=self.kwargs['cate_id'])
        kwargs['last_page'] = res['last_page']
        kwargs['page_range'] = res['page_range']
        kwargs['date_list'] = page_info.get_date_list()
        return super(CategoryView, self).get_context_data(**kwargs)

# class CategoryView(ListView):
#     template_name = 'category.html'
#     context_object_name = "article_list"
#
#     def paginator(self):
#         article_list = Article.objects.filter(category=self.kwargs['cate_id'],status='p')
#         paginator = Paginator(article_list, settings.EACHE_PAGE)  # 每5篇博客为一页
#         return paginator
#
#     def get_queryset(self):
#         page_num = self.request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
#         page_of_article = self.paginator().get_page(page_num)
#         article_list = page_of_article
#         return article_list
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         last_page = self.paginator().num_pages
#         page_num = self.request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
#         current_page_num = self.paginator().get_page(page_num).number  # 获取当前页码
#         # 获取当前页码前后各2页
#         page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
#                      list(range(current_page_num, min(current_page_num + 2, last_page) + 1))
#
#         # 加上省略号
#         if page_range[0] - 1 >= 2:
#             page_range.insert(0, '...')
#         if last_page - page_range[-1] >= 2:
#             page_range.append('...')
#         # 加上首页和尾页
#         if page_range[0] != 1:
#             page_range.insert(0, 1)
#         if page_range[-1] != last_page:
#             page_range.append(last_page)
#
#         # 按日期分类内容
#         date_list = Article.objects.dates('created_time', 'month', order='DESC')
#
#         # 获取每个分类中有几篇博客
#         categorys = Category.objects.all().order_by('category')
#         categorys_list = []
#         for category in categorys:
#             category.count = Article.objects.filter(category=category).count()
#             print(category.count)
#             categorys_list.append(category)
#
#         kwargs["category_list"] = categorys_list
#         kwargs['category'] = get_object_or_404(Category, pk=self.kwargs['cate_id'])
#         kwargs['last_page'] = last_page
#         kwargs['page_range'] = page_range
#         kwargs['date_list'] = date_list
#         return super(CategoryView, self).get_context_data(**kwargs)

class DateView(ListView):
    template_name = 'date_list.html'
    context_object_name = 'article_list'

    # 不知道是不是django的bug 用created_time__month 过滤不出month。所以只能这样用
    def filter_time(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        if month < 10:
            month = '0' + str(month)
        # 例 2018-03
        return '%s-%s' %(year,month)

    def get_queryset(self):
        page_num = self.request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
        article_list = PageFunc(Article.objects.filter(created_time__startswith=self.filter_time(),status='p')).paginator.get_page(page_num)
        return article_list

    def get_context_data(self, *, object_list=None, **kwargs):
        page_info = PageFunc(Article.objects.filter(created_time__startswith=self.filter_time(),status='p'))
        res = page_info.get_pagintor_info(self.request.GET.get("page", 1))

        # 获取每个分类中有几篇博客
        # categorys_list = Category.objects.annotate(count=Count('article'))

        kwargs["category_list"] = page_info.get_category_list()
        kwargs['date_list'] = page_info.get_date_list()
        year = self.kwargs['year']
        month = self.kwargs['month']
        kwargs['date'] = '%s年%s月' %(year,month)
        kwargs['last_page'] = res['last_page']
        kwargs['page_range'] = res['page_range']
        return super(DateView, self).get_context_data(**kwargs)

def home(request):
    return render(request,'home.html')

def article_search(request,):
    search_for = request.GET.get('search_for')
    print(search_for)

    if search_for:
        res = []
        article_list = Article.objects.filter(status='p')
        for article in article_list:
            if re.findall(search_for,article.title):
                res.append(article)
        page_info = PageFunc(res)
        page_num = request.GET.get("page", 1)  # 拿url中的page参数。默认展示第一页
        article_list = page_info.paginator.get_page(page_num)
        page_res = page_info.get_pagintor_info(page_num)

        context = {
            'search_for'    : search_for,
            'search'        : 'yes',
            'last_page'     : page_res['last_page'],
            'page_range'    : page_res['page_range'],
            'article_list'  : article_list,
            'category_list' : page_info.get_category_list(),
            'date_list'     : page_info.get_date_list(),
        }
        return render(request,'search.html',context)
    else:
        return redirect('index')

def comment_view(request,article_id):
    comment = ArticleCommentForm(request.POST)
    if comment.is_valid():
        message = comment.cleaned_data['body']
        user_name = comment.cleaned_data['user_name']
        article = get_object_or_404(Article, pk=article_id)
        new_record = ArticleComment(user_name=user_name, body=message, article=article)
        new_record.save()

        return HttpResponse("")
    else:
        context = {
            'body_error': comment.errors.get('body'),
            'username_error': comment.errors.get('user_name'),
        }
        return HttpResponse(json.dumps(context,ensure_ascii=False),content_type='application/json')

def deal_like(request,article_id):
    if request.method == "GET":
        op = request.GET.get('op')
        obj = Article.objects.get(pk=article_id)
        if op == "add":
            obj.likes += 1
        elif op=="sub":
            obj.likes -= 1
        obj.save()
        return HttpResponse("成功")
    else:
        return HttpResponse("失败")
