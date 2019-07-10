from django.contrib import admin
from django.urls import path
from apps.blog import views
from django.conf.urls import include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('articles/<int:id>/', views.detail, name='detail'),
    path('category/<int:id>/', views.search_category, name='category_menu'),
    path('tag/<str:tag>/', views.search_tag, name='search_tag'),
    path('archives/<str:year>/<str:month>', views.archives, name='archives'),
    path('summernote/', include('django_summernote.urls')),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT, 'show_indexes': settings.DEBUG})
    ]