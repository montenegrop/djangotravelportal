from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = "reviews"

urlpatterns = [
    #path('/', include('django.contrib.auth.urls')),
    path('create/', views.ReviewCreateView.as_view(), name='create'),
    path('photo-guidelines', views.PhotoGuidelinesView.as_view(), name='photo_guidelines'),
    path('<slug:slug>', views.ReviewIndexView.as_view(), name='index'),
    path('create/park/<int:pk>/', views.ReviewCreateParkReviewView.as_view(), name='park'),
    path('create/park/<int:pk>/ack', views.ReviewCreateParkReviewAckView.as_view(), name='park_ack'),
    path('park/manage-photos/<int:pk>', views.ParkReviewManagePhotosView.as_view(), name='park_review_manage_photos'),
    path('park/manage-photos/<int:pk>/create', views.ParkReviewCreatePhotoView.as_view(), name='park_review_create_photo'),
    path('photo-guidelines', views.PhotoGuidelinesView.as_view(), name='photo_guidelines'),
    path('tour-operator/manage-photos/<int:pk>', views.TourOperatorReviewManagePhotosView.as_view(), name='tour_operator_manage_photos'),
    path('tour-operator/manage-photos/<int:pk>/create', views.TourOperatorReviewCreatePhotoView.as_view(), name='tour_operator_review_create_photo'),
    path('create/park/store/<int:pk>/', views.save_review_park, name='park_save'),
    path('create/park-kilimanjaro/<int:pk>/', views.ReviewCreateParkKilimanjaroView.as_view(), name='park_kilimanjaro'),
    path('create/park-kilimanjaro/store/<int:pk>/', views.save_review_park_kilimanjaro, name='park_kilimanjaro_save'),
    path('create/tour-operator/<int:pk>', views.ReviewCreateTourOperatorView.as_view(), name='tour_operator'),
    path('create/tour-operator/<int:pk>/ack', views.ReviewCreateTourOperatorReviewAckView.as_view(), name='tour_operator_ack'),
    path('create/tour-operator/store/<int:pk>', views.save_review_tour_operator, name='tour_operator_save'),
    path('parks/<slug:slug>', views.ParkReviewDetailView.as_view(), name="park_review"),
    path('c/<slug:slug>', views.TourOperatorReviewDetailView.as_view(), name="tour_operator_review")
]
