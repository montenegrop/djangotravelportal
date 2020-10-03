from django.urls import path
from . import views

app_name = "photos"

urlpatterns = [
    path('', views.PhotosView.as_view(), name='index'),
    path('api/photos/', views.PhotosAPIView.as_view(), name='api_photos'),
    path('api/photo-like/<int:pk>/', views.PhotoLikeView.as_view(), name='api_photo_like'),
    path('photo-delete/<int:pk>/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('photo-caption/<int:pk>/', views.PhotoCaptionView.as_view(), name='photo_delete'),
    path('ajax/load-parks/', views.load_parks, name='ajax_load_parks'),
    path('tag/<int:pk>/', views.PhotoTagView.as_view(), name='photo_tag'),

    path('add-photos/', views.PhotoAddView.as_view(), name='add_photos'),
    path('save-photos/', views.PhotoSaveView.as_view(), name='save_photos'),
    path('add-tp-photos/<slug:itinerary_slug>/', views.PhotoAddView.as_view(), name='add_tp_photos'),
    path('add-photos/<int:pk>/ack', views.PhotoAddAckView.as_view(), name='photos_ack'),
    path('add-photos/ack/<str:itinerary_slug>/', views.PhotoAddAckView.as_view(), name='photos_ack_itinerary'),

    path('manage-photos/create', views.UserCreatePhotoView.as_view(), name='user_create_photo'),
    path('manage-tp-photos/create/<slug:itinerary_slug>', views.UserCreatePhotoView.as_view(), name='tp_create_photo'),

    path('load-ajax/<int:pk>/', views.PhotoLoadAjax.as_view(), name='photo_load_ajax'),
    path('animal/<slug:animal_slug>', views.PhotosView.as_view(), name='photos_animal'),
    path('<int:pk>/<str:caption>/', views.PhotoDetailView.as_view(), name='photo'),
    path('<int:pk>/', views.PhotoDetailView.as_view(), name='photo'),
]
