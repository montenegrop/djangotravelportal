from django.urls import path
from . import views

app_name = 'articles'
urlpatterns = [
    path('', views.ArticlesView.as_view(), name='index'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='view'),
    path('api/article-kudu/<int:pk>/', views.ArticlKuduView.as_view(), name='api_article_kudu'),
    path('search/<str:query>/', views.ArticleSearchView.as_view(), name='search'),
    path('category/<slug:slug>/', views.ArticleCategory.as_view(), name='category'),
]
