from django.urls import path
from core.views import HomeView, JoinUsView, PageView, CountriesListView, PhotoKudoView, robots_txt, JoinUsThankYouView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('join/', JoinUsView.as_view(), name='join'),
    path('join_thank_you/', JoinUsThankYouView.as_view(), name='join_thank_you'),
    path('about-us/', PageView.as_view(), {'page_name': 'about-us'}, name='about-us'),
    path('terms-of-use/', PageView.as_view(), {'page_name': 'our-terms-of-use'}, name='terms-of-use'),
    path('privacy-policy/', PageView.as_view(), {'page_name': 'our-privacy-policy'}, name='privacy-policy'),
    path('photo-guidelines/', PageView.as_view(), {'page_name': 'photo-guidelines'}, name='photo-guidelines'),
    path('careers/', PageView.as_view(), {'page_name': 'careers'}, name='careers'),
    path('add-my-company/', PageView.as_view(), {'page_name': 'adding-your-business'}, name='add-my-company'),
    path('tanzania-based-freelance-writer/', PageView.as_view(), {'page_name': 'tanzania-based-freelance-writer'},name='tanzania-based-freelance-writer'),
    path('advertise-with-us/', PageView.as_view(), {'page_name': 'advertise-with-us'}, name='advertise-with-us'),
    path('api/kudo/photo/<int:photo_pk>/', PhotoKudoView.as_view()),
    path('countries/', CountriesListView.as_view(), name='countries'),
    path("robots.txt", robots_txt),
]
