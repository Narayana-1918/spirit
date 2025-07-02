from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    # Package URLs
    path('',views.home,name='home'),
    path('tours/', views.tour_packages_list, name='packages_list'),
    path('packages/', views.tour_packages_list, name='packages_list'),
    path('packages/cbv/', views.PackageListView.as_view(), name='packages_list_cbv'),
    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('package/<int:package_id>/book/', views.package_booking, name='package_booking'),
    
    # Destination URLs
    path('destination/<int:destination_id>/', views.destination_detail, name='destination_detail'),
    
    # Places URLs
    path('places/', views.places_list, name='places_list'),
    path('place/<int:place_id>/', views.place_detail, name='place_detail'),
    
    # Booking URLs
    path('booking/confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/detail/<str:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    
    # AJAX URLs
    path('ajax/calculate-price/', views.calculate_price, name='calculate_price'),
]