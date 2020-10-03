from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = "search"

urlpatterns = [
    path('<str:query>/', views.SearchView.as_view(), name='index'),
    path('<str:query>/operators', views.SearchTourOperatorsView.as_view(), name='operators'),
    path('<str:query>/packages', views.SearchTourPackagesView.as_view(), name='packages'),
    path('<str:query>/reviews', views.SearchReviewsView.as_view(), name='reviews'),
    path('<str:query>/photos', views.SearchPhotosView.as_view(), name='photos'),
    path('<str:query>/blog', views.SearchBlogView.as_view(), name='blog'),
]
