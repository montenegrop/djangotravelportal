from django.urls import path
from backend.views import *

app_name = "backend"

urlpatterns = [
    #admin
    path('admin/', AdminDashboardView.as_view(), name='admin'),
    path('admin_tour_operator/', AdminTourOperatorView.as_view(), name='admin_tour_operator'),
    path('admin_members/', AdminMembersView.as_view(), name='admin_members'),
    path('admin_open_park_review/<int:park_review_pk>/', AdminOpenReviewView.as_view(), name='admin_open_park_review'),
    path('admin_open_tour_operator_review/<int:tour_operator_review_pk>/', AdminOpenReviewView.as_view(), name='admin_open_tour_operator_review'),
    path('admin_open_tour_operator/<int:pk>/', AdminOpenTourOperatorView.as_view(), name='admin_open_tour_operator'),
    path('admin_quote_requests/', AdminQuoteRequestView.as_view(), name='admin_quote_requests'),
    path('admin_yas_score/<int:pk>/', AdminTourOperatorYasScoreView.as_view(), name='admin_yas_score'),
    path('admin_articles/', AdminArticlesView.as_view(), name='admin_articles'),
    path('admin_article_change/<slug:slug>/', AdminArticleChangeView.as_view(), name='admin_article_change'),
    path('admin_article_delete/<slug:slug>/', AdminArticlesView.as_view(), name='admin_article_delete'),
    path('admin_test_email/', AdminTestEmailView.as_view(), name='admin_test_email'), 
    path('admin_email_templates/', AdminEmailTemplatesView.as_view(), name='admin_email_templates'), 
    path('admin_email_templates_edit/<int:pk>/', AdminEmailTemplatesEditView.as_view(), name='admin_email_templates_edit'), 
    path('admin_email_templates_open/<int:pk>/', AdminEmailTemplatesOpenView.as_view(), name='admin_email_templates_open'), 
    
    #member
    path('member_photos/', MemberPhotosView.as_view(), name='member_photos'),
    path('member_reviews/', MemberReviewsView.as_view(), name='member_reviews'),
    path('member_profile/', MemberProfileView.as_view(), name='member_profile'),
    
    #tour operator
    path('dashboard/', TourOperatorDashboardView.as_view(), name='tour_operator_dashboard'),
    path('advertise/', TourOperatorAdvertiseView.as_view(), name='tour_operator_advertise'),
    path('analytics/', TourOperatorAnalyticsView.as_view(), name='tour_operator_analytics'),
    path('client-review/', TourOperatorClientReviewView.as_view(), name='tour_operator_client_review'),
    path('profile/', TourOperatorEditProfileView.as_view(), name='tour_operator_profile'),
    path('photos/', TourOperatorPhotosView.as_view(), name='tour_operator_photos'),
    path('packages/', TourOperatorPackagesView.as_view(), name='tour_operator_packages'),
    path('package_photos/<slug:slug>/', TourOperatorPackagePhotosView.as_view(), name='tour_operator_package_photos'),
    path('add-packages/', TourOperatorAddPackagesView.as_view(), name='tour_operator_add_packages'),
    path('edit-packages/<int:pk>/<slug:slug>/', TourOperatorAddPackagesView.as_view(), name='tour_operator_edit_package'),
    path('remove-packages/<int:pk>/<slug:slug>/', TourOperatorRemovePackagesView.as_view(), name='tour_operator_remove_package'),
    path('quotes/', TourOperatorQuoteRequestsView.as_view(), name='tour_operator_quotes'),
    path('widgets/', TourOperatorWidgetsView.as_view(), name='tour_operator_widgets'),
    path('tour_operator/quoterequest_update/<int:pk>/', SaveQuoteUpdate.as_view(), name='quote_update'),
]








