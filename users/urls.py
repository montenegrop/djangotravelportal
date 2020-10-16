from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

urlpatterns = [

    path('accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            html_email_template_name='registration/password_reset_email.html'
        ),
        name='password_reset'
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # new
    path('profile/', views.ChangeProfileView.as_view()),
    path('shortlist/', views.ShortListView.as_view(), name='shortlist'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signup_email/', views.SignUpEmail.as_view(), name='signup_email'),
    path('registration/', views.signup, name='account_registration'),
    path('logout/', views.logout_view, name='logout_view'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('activate_complete/', views.ActivateCompleteView.as_view(), name='activate_complete'),
    
    path('member/<int:pk>/<str:slug>/', views.MemberView.as_view(), name='member'),
    path('member/<int:pk>/', views.MemberView.as_view(), name='member'),

    # add security:
    path('member/password', views.change_password, name='change_password'),
    path('member/avatar', views.ChangeAvatar.as_view(), name='change_avatar'),
    path('delete_itinerary_fav/<int:itinerary_pk>/', views.DeleteItineraryFavAPIView.as_view(), name='delete_itinerary_fav'),
    path('add_itinerary_fav/<int:itinerary_pk>/', views.AddItineraryFavAPIView.as_view(), name='add_itinerary_fav'),
    path('delete_itinerary_fav_multiple/', views.DeleteItineraryFavAPIView.as_view(), name='delete_itinerary_fav_multiple'),

    path('add_operator_fav/<int:operator_pk>/', views.AddOperatorFavAPIView.as_view(), name='add_operator_fav'),
    path('delete_operator_fav/<int:operator_pk>/', views.DeleteOperatorFavAPIView.as_view(), name='delete_operator_fav'),
    path('delete_operator_fav_multiple/', views.DeleteOperatorFavAPIView.as_view(), name='delete_operator_fav_multiple'),
]

