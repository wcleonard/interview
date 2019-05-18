from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    ''' 修改一些默认参数 '''
    page_size = 3  # 每页显示多少条
    page_size_query_param = 'size'  # 每页显示多少条的参数key
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制
