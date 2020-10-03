from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('wildlife/', views.WildlifeView.as_view(), name='wildlife'),
    path('guides/', views.GuidesView.as_view(), name='guides'),
    path('Swahili-safari-animals/', views.SwahiliView.as_view(), name='swahili'),
    path('wildlife/<slug:slug>/', views.AnimalDetailView.as_view(), name='animal'),
    path('parks/<slug:slug>/', views.ParkDetailView.as_view(), name='park'),
    path('parks/', views.ParksRollupView.as_view(), name='parks_rollup'),
    path('parks/<slug:slug>/reviews', views.ParkReviewsDetailView.as_view(), name='park_reviews'),
    path('parks/<slug:slug>/reviews/<int:review_pk>', views.ParkReviewsDetailView.as_view(), name='park_review'),
    path('parks/<slug:slug>/tours', views.ParkToursDetailView.as_view(), name='park_tours'),
    path('parks/<slug:slug>/tour-operators', views.ParkTourOperatorsDetailView.as_view(), name='park_tour_operators'),
    path('parks/<slug:slug>/getting-there', views.ParkGettingThereDetailView.as_view(), name='park_getting_there'),
    path('<slug:slug>/park/wildlife/', views.ParkWildlifeDetailView.as_view(), name='park_wildlife'),
    path('<slug:slug>/park/activities/', views.ParkActivitiesDetailView.as_view(), name='park_activities'),
    path('parks/<slug:slug>/photos', views.ParkPhotosDetailView.as_view(), name='park_photos'),
    path('activities/', views.ActivitiesView.as_view(), name='activities'),
    path('activities/<slug:slug>', views.ActivityDetailView.as_view(), name='activity'),
    path('<slug:slug>/', views.CountryIndexDetailView.as_view(), name='country_index'),
    path('<slug:slug>/parks/', views.CountryIndexParksDetailView.as_view(), name='country_index_parks'),
    path('<slug:slug>/getting-there/', views.CountryIndexGettingThereDetailView.as_view(),
         name='country_index_getting_there'),
    path('<slug:slug>/activities/', views.CountryIndexActivitiesDetailView.as_view(), name='country_index_activities'),
    path('<slug:slug>/wildlife/', views.CountryIndexWildlifeDetailView.as_view(), name='country_index_wildlife'),
    path('<slug:slug>/photos/', views.CountryIndexPhotosDetailView.as_view(), name='country_index_photos'),
    path('api/park-review-kudu/<int:pk>/', views.ParkReviewKuduView.as_view(), name='api_park_review_kudu'),

]
