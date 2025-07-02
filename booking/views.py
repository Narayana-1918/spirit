from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.forms import ModelForm
from django import forms
from .models import TourPackage, Destination, Places, PackageItinerary, DestinationItinerary, Booking
import json

# Form for booking
class BookingForm(ModelForm):
    travel_start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta:
        model = Booking
        fields = [
            'full_name', 'phone', 'email', 'address', 
            'travel_start_date', 'adults', 'kids_5_12', 'kids_b_5',
            'special_requests', 'dietary_requirements'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
            'kids_5_12': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'value': 0}),
            'kids_b_5': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'value': 0}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests'}),
            'dietary_requirements': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dietary requirements'})
        }
def home(request):
    packages = TourPackage.objects.filter(is_active=True)\
    .prefetch_related('destination', 'destination__place')\
    .order_by('?')[:4]
    return render(request,'tours/home.html',{'packages':packages})

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import TourPackage

def tour_packages_list(request):
    """Display all available tour packages with filtering options"""
    packages = TourPackage.objects.filter(is_active=True)\
        .order_by('-created_at')\
        .prefetch_related('destination', 'destination__place')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        packages = packages.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(destination__place__name__icontains=search_query)
        ).distinct()

    # === Filter: Package Type ===
    package_type = request.GET.get('package_type', '')
    if package_type:
        packages = packages.filter(package_type=package_type)

    # === Filter: Duration ===
    duration_filter = request.GET.get('duration', '')
    if duration_filter == 'short':
        packages = packages.filter(duration__lte=3)
    elif duration_filter == 'medium':
        packages = packages.filter(duration__gt=3, duration__lte=7)
    elif duration_filter == 'long':
        packages = packages.filter(duration__gt=7)

    # === Filter: Price Range ===
    price_range = request.GET.get('price_range', '')
    if price_range == 'budget':
        packages = packages.filter(base_price__lte=6000)
    elif price_range == 'mid':
        packages = packages.filter(base_price__lte=10000)
    elif price_range == 'luxury':
        packages = packages.filter(base_price__gt=15000)

    # Pagination
    paginator = Paginator(packages, 9)  # 9 packages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'package_type': package_type,
        'duration_filter': duration_filter,
        'price_range': price_range,
    }

    return render(request, 'tours/packages_list.html', context)


def package_detail(request, package_id):
    """Display detailed view of a specific tour package"""
    package = get_object_or_404(TourPackage, id=package_id, is_active=True)
    # package=TourPackage.objects.filter(id=package_id, is_active=True).exists()
    # print(package.__dict__,package.get_destinations)
    # print(package.get_destinations())
    destinations = package.destination.all().order_by('destination_order') # type: ignore
    package_itinerary = package.package_itinerary.all().order_by('day_number') # type: ignore
    
    # Get places covered in this package
    places = Places.objects.filter(destination__tour_package=package).distinct()
    
    # Calculate pricing for different group sizes
    pricing_examples = {
        'single': package.get_discounted_price(),
        'couple': package.get_discounted_price() * 2,
        'family_4': (package.get_discounted_price() * 2) + (package.get_discounted_price() * 0.7 * 2),  # 2 adults + 2 kids
    }
    # print(package,destinations.tour_package,package_itinerary,places,pricing_examples)
    context = {
        'package': package,
        'destinations': destinations,
        'places': places,
        'package_itinerary': package_itinerary,
        'pricing_examples': pricing_examples,
        'total_travelers_sample': 4,
    }
    
    return render(request, 'tours/package_detail.html', context)

def destination_detail(request, destination_id):
    """Display detailed view of a specific destination within a package"""
    destination = get_object_or_404(Destination, id=destination_id)
    destination_itinerary = destination.destination_itinerary.all().order_by('local_day_number') # type: ignore
    
    context = {
        'destination': destination,
        'destination_itinerary': destination_itinerary,
        'package': destination.tour_package,
    }
    
    return render(request, 'tours/destination_detail.html', context)

def package_booking(request, package_id):
    """Handle package booking form"""
    package = get_object_or_404(TourPackage, id=package_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tour_package = package
            booking.save()
            
            messages.success(
                request, 
                f'Booking successful! Your booking ID is {booking.booking_id}. '
                f'Total amount: ₹{booking.total_amount:.2f}'
            )
            return redirect('tours:booking_confirmation', booking_id=booking.booking_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
    
    # Calculate live pricing
    destinations = package.destination.all() # type: ignore
    
    context = {
        'package': package,
        'destinations': destinations,
        'form': form,
        'base_price': package.get_discounted_price(),
    }
    
    return render(request, 'tours/package_booking.html', context)

def booking_confirmation(request, booking_id):
    """Display booking confirmation details"""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    context = {
        'booking': booking,
        'package': booking.tour_package,
        'destinations': booking.tour_package.destination.all(), # type: ignore
    }
    
    return render(request, 'tours/booking_confirmation.html', context)

# AJAX view for live price calculation
@csrf_exempt
def calculate_price(request):
    """AJAX endpoint to calculate live pricing based on travelers"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            package_id = data.get('package_id')
            adults = int(data.get('adults', 0))
            kids_5_12 = int(data.get('kids_5_12', 0))
            kids_b_5 = int(data.get('kids_b_5', 0))
            
            package = get_object_or_404(TourPackage, id=package_id)
            base_price = package.get_discounted_price()
            
            # Calculate total
            adult_total = adults * base_price
            kid_5_12_total = kids_5_12 * (base_price * 0.7)
            kid_b_5_total = kids_b_5 * (base_price * 0.5)
            
            total_amount = adult_total + kid_5_12_total + kid_b_5_total
            total_travelers = adults + kids_5_12 + kids_b_5
            
            return JsonResponse({
                'success': True,
                'total_amount': round(total_amount, 2),
                'adult_total': round(adult_total, 2),
                'kid_5_12_total': round(kid_5_12_total, 2),
                'kid_b_5_total': round(kid_b_5_total, 2),
                'total_travelers': total_travelers,
                'base_price': base_price,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def places_list(request):
    """Display all available places"""
    places = Places.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        places = places.filter(
            Q(name__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by state
    state_filter = request.GET.get('state', '')
    if state_filter:
        places = places.filter(state__icontains=state_filter)
    
    # Get unique states for filter
    states = Places.objects.values_list('state', flat=True).distinct().exclude(state__isnull=True)
    
    # Pagination
    paginator = Paginator(places, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'state_filter': state_filter,
        'states': states,
    }
    
    return render(request, 'tours/places_list.html', context)

def place_detail(request, place_id):
    """Display detailed view of a specific place"""
    place = get_object_or_404(Places, id=place_id)
    
    # Get all packages that include this place - corrected the lookup
    packages_with_place = TourPackage.objects.filter(
        destination__place=place,  # Changed from destinations__place to destination__place
        is_active=True
    ).distinct()
    
    context = {
        'place': place,
        'packages': packages_with_place,
    }
    
    return render(request, 'tours/place_detail.html', context)

# Class-based views for better organization
class PackageListView(ListView):
    """Class-based view for package listing with advanced filtering"""
    model = TourPackage
    template_name = 'tours/packages_list_cbv.html'
    context_object_name = 'packages'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = TourPackage.objects.filter(is_active=True).order_by('-created_at')
        
        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        package_type = self.request.GET.get('type')
        if package_type:
            queryset = queryset.filter(package_type=package_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['package_types'] = TourPackage.objects.values_list('package_type', flat=True).distinct()
        return context

def my_bookings(request):
    """Display user's booking history (requires user authentication)"""
    # This assumes you have user authentication implemented
    email = request.GET.get('email', '')
    phone = request.GET.get('phone', '')
    
    bookings = Booking.objects.none()
    
    if email:
        bookings = Booking.objects.filter(email=email).order_by('-booking_date')
    elif phone:
        bookings = Booking.objects.filter(phone=phone).order_by('-booking_date')
    
    context = {
        'bookings': bookings,
        'email': email,
        'phone': phone,
    }
    
    return render(request, 'tours/my_bookings.html', context)

def booking_detail(request, booking_id):
    """Display detailed booking information"""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    
    context = {
        'booking': booking,
        'package': booking.tour_package,
        'destinations': booking.tour_package.destination.all(), # type: ignore
        'itinerary': booking.tour_package.package_itinerary.all(), # type: ignore
    }
    
    return render(request, 'tours/booking_detail.html', context)