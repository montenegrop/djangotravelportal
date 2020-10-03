from django.urls import path
from . import views


urlpatterns = [

     path('c/<slug:slug>',views.TourOperatorDetailView.as_view(), name='tour_operator'),
     path('c/<slug:slug>/widget_1',views.TourOperatorWidgetOneDetailView.as_view(), name='tour_operator_widget_1'),
     path('c/<slug:slug>/widget_2',views.TourOperatorWidgetTwoDetailView.as_view(), name='tour_operator_widget_2'),
     # Widget Three does not exists
     path('c/<slug:slug>/widget_4',views.TourOperatorWidgetFourDetailView.as_view(), name='tour_operator_widget_4'),
     #path('c/<int:pk>',views.TourOperatorDetailView.as_view(), name='tour_operator_pk'),
     path('c/<slug:slug>/reviews/<int:review>/',views.TourOperatorDetailView.as_view(), name='tour_operator_review'),
     path('c/<slug:slug>/reviews/',views.TourOperatorDetailView.as_view(), name='tour_operator_reviews'),
     path('c/<slug:slug>/more_information',views.RequestInfoView.as_view(), name='tour_operator_more_information'),
     path('african-safari-tour-operators/', views.TourOperatorView.as_view(), name='all_tour_operator'),
     
     path('quote_itinerary/<int:itinerary_pk>/<slug:slug>/', views.RequestInfoView.as_view(), name='package_quote'),
     path('quote_operator/<int:operator_pk>/<slug:slug>/', views.RequestInfoView.as_view(), name='operator_quote'),
     path('quote/', views.RequestInfoView.as_view(), name='quote'),
     
     path('african-safari-tour-operators/<slug:country>/', views.TourOperatorView.as_view(), name='all_tour_operator_country'),
     path('african-safari-tour-operators/<slug:park>/', views.TourOperatorView.as_view(), name='all_tour_operator_park'),
     path('african-safari-tour-operators/manage-shortlist/(.*)', views.ManageShortlistView.as_view(), name='manage_shortlist'),
     path('african-safari-tour-packages/', views.ItineraryView.as_view(), name='all_tour_packages'),
     path('african-safari-tour-packages/<slug:country>/', views.ItineraryView.as_view(), name='all_tour_packages_country'),
     path('african-safari-tour-packages/<slug:operator>/', views.ItineraryView.as_view(), name='all_tour_packages_operator'),
     path('african-safari-tour-packages/<slug:park>/', views.ItineraryView.as_view(), name='all_tour_packages_park'),
     
     #path('tours/<slug:slug>/', views.TourPackageView.as_view(), name='tour_package'),
     path('tours/<int:pk>/<slug:slug>/', views.TourPackageView.as_view(), name='tour_package'),
     path('tours_thanks/', views.RequestInfoThankYouView.as_view(), name='tour_package_thanks'),


     path('api/tour-review-kudu/<int:pk>/', views.TourOperatorReviewKuduView.as_view(), name='api_tour_review_kudu'),
     path('api/tour-operators/', views.TourOperatorRollupAPIView.as_view(), name='api_tour_operators'),
     path('api/tour-packages/', views.TourPackageRollupAPIView.as_view(), name='api_tour_packages'),
]
