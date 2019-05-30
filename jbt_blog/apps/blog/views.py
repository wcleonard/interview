from django.shortcuts import render
from apps.blog.models import Article, Category, Tag
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.conf import settings

# 获取全部的分类对象
categories = Category.objects.all()
# 获取全部的标签对象
tags = Tag.objects.all()
months = Article.objects.datetimes('pub_time', 'month', order='DESC')


# 主页视图
def home(request):
    # 获取全部(状态为已发布，发布时间不为空)Article对象
    posts = Article.objects.filter(status='p', pub_time__isnull=False)
    # 每页显示数量
    paginator = Paginator(posts, settings.PAGE_NUM)
    # 获取URL中page参数的值
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'home.html', {'post_list': post_list, 'category_list': categories, 'months': months})


def detail(request, id):
    try:
        post = Article.objects.get(id=str(id))
        # 更新浏览次数
        post.viewed()
        tags = post.tags.all()
        # 上一篇文章对象和下一篇文章对象
        next_post = post.next_article()
        prev_post = post.prev_article()
    except Article.DoesNotExist:
        raise Http404
    return render(
        request, 'post.html',
        {
            'post': post,
            'tags': tags,
            'category_list': categories,
            'next_post': next_post,
            'prev_post': prev_post,
            'months': months
        }
    )


def search_category(request, id):
    posts = Article.objects.filter(category_id=str(id))
    category = categories.get(id=str(id))
    # 每页显示数量
    paginator = Paginator(posts, settings.PAGE_NUM)
    try:
        # 获取URL中page参数的值
        page = request.GET.get('page')
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'category.html',
                  {'post_list': post_list,
                   'category_list': categories,
                   'category': category,
                   'months': months
                   }
                  )


def search_tag(request, tag):
    posts = Article.objects.filter(tags__name__contains=tag)
    # 每页显示数量
    paginator = Paginator(posts, settings.PAGE_NUM)
    try:
        # 获取URL中page参数的值
        page = request.GET.get('page')
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'tag.html', {
        'post_list': post_list,
        'category_list': categories,
        'tag': tag,
        'months': months
    }
                  )


def archives(request, year, month):
    posts = Article.objects.filter(pub_time__year=year, pub_time__month=month).order_by('-pub_time')
    # 每页显示数量
    paginator = Paginator(posts, settings.PAGE_NUM)
    try:
        # 获取URL中page参数的值
        page = request.GET.get('page')
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'archive.html', {
        'post_list': post_list,
        'category_list': categories,
        'months': months,
        'year_month': year + '年' + month + '月'
    }
                  )
