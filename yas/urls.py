from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
#from places.urls import *
from yas.views import Custom404, Custom403, custom500

app_name = "yas"

urlpatterns = [
    path('su/', include('django_su.urls')),
    path('yasadmin/', admin.site.urls, name='admin'),
    path('photos/', include('photos.urls', namespace="photos")),
    path('articles/', include('blog.urls', namespace="blog")),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path('backend/', include('backend.urls', namespace="backend")),
    path('reviews/', include('reviews.urls', namespace="reviews")),
    path('search/', include('search.urls', namespace="search")),
    path('', include('users.urls')),
    path('', include('core.urls')),
    path('', include('operators.urls')),
    path('', include('places.urls')),
    path('tags_input/', include('tags_input.urls', namespace='tags_input')),
    path('froala_editor/',include('froala_editor.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

admin.site.site_header = "YAS Admin"
admin.site.site_title = "YAS Admin Portal"
admin.site.index_title = "YAS Administration"

if settings.DEBUG:
    #import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    #urlpatterns = [
    #    path('__debug__/', include(debug_toolbar.urls)),
    #] + urlpatterns
    pass

if settings.DEBUG:
    urlpatterns = [
        path('404/',Custom404.as_view(),name='404'),
        path('500/',custom500,name='500'),
        path('403/',Custom403.as_view(),name='403'),
    ] + urlpatterns

if not settings.DEBUG:
    handler403 = Custom403.as_view()
    handler404 = Custom404.as_view()
    handler500 = custom500
