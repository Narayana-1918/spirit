from django.db import models
import uuid

# Create your models here.
class TourPackage(models.Model):
    name = models.CharField(max_length=50)  # Increased to accommodate names like "Coorg and Wayanad"
    pic = models.ImageField(upload_to='tp_img/')
    description = models.TextField(max_length=500, blank=True, null=True)
    package_type_choices = [
        ('Single', 'Single Destination'),
        ('Multiple', 'Multiple Destinations')
    ]
    package_type = models.CharField(max_length=10, choices=package_type_choices, default='Single')
    duration_days = models.PositiveIntegerField()
    duration_nights = models.PositiveIntegerField()
    base_price = models.FloatField()
    discount = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_discounted_price(self):
        return self.base_price - (self.base_price * self.discount / 100)
    
    def get_destinations(self):
        return self.destinations.all() # type: ignore
    
    def __str__(self) -> str:
        return f'{self.name} ({self.package_type})'

class Places(models.Model):
    name = models.CharField(max_length=30)
    place_img = models.ImageField(upload_to='places_images/')
    state = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, default='India')
    description = models.TextField(max_length=300, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Places"
    
    def __str__(self) -> str:
        return f'{self.name}, {self.state}'

class Destination(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='destination')
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    destination_order = models.PositiveIntegerField(default=1)  # Order of visit in multi-destination packages
    days_in_destination = models.PositiveIntegerField()  # How many days spent in this destination
    
    # Destination specific details
    dest_image = models.ImageField(upload_to='dest_images/')
    tour_type_choices = [('Group','Group'), ('Regular','Regular'), ('Luxury','Luxury'), ('Honeymoon','Honeymoon')]
    tour_type = models.CharField(max_length=10, choices=tour_type_choices)
    description = models.TextField(max_length=1000)
    
    # Travel points for this destination
    arrival_point = models.CharField(max_length=50)  # Where tourists arrive for this destination
    departure_point = models.CharField(max_length=50)  # Where they depart from this destination
    
    # Destination specific amenities
    accommodation = models.TextField(max_length=200)
    things_to_do = models.TextField(max_length=500)
    special_attractions = models.TextField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['destination_order']
        unique_together = ['tour_package', 'place']  # Prevent duplicate destinations in same package
    
    def __str__(self) -> str:
        return f'{self.tour_package.name} - {self.place.name} (Day {self.destination_order})'

class PackageItinerary(models.Model):
    """Overall itinerary for the entire package"""
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='package_itinerary')
    day_number = models.PositiveIntegerField()
    current_destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='package_days')
    day_title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    activities = models.TextField(max_length=500, blank=True, null=True)
    meals_included = models.CharField(max_length=50, blank=True, null=True)
    accommodation_details = models.CharField(max_length=100, blank=True, null=True)
    transportation = models.CharField(max_length=100, blank=True, null=True)
    optional_activities = models.TextField(max_length=300, blank=True, null=True)
    is_travel_day = models.BooleanField(default=False)  # True if it's a day for traveling between destinations
    
    class Meta:
        ordering = ['day_number']
        unique_together = ['tour_package', 'day_number']
    
    def __str__(self) -> str:
        return f'{self.tour_package.name} - Day {self.day_number}: {self.day_title}'

class DestinationItinerary(models.Model):
    """Specific itinerary for each destination within a package"""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='destination_itinerary')
    local_day_number = models.PositiveIntegerField()  # Day number within this specific destination
    package_day_number = models.PositiveIntegerField()  # Overall day number in the package
    day_title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    morning_activities = models.TextField(max_length=300, blank=True, null=True)
    afternoon_activities = models.TextField(max_length=300, blank=True, null=True)
    evening_activities = models.TextField(max_length=300, blank=True, null=True)
    meals_included = models.CharField(max_length=50, blank=True, null=True)
    local_transportation = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['package_day_number']
        unique_together = ['destination', 'local_day_number']
    
    def __str__(self) -> str:
        return f'{self.destination.place.name} - Local Day {self.local_day_number} (Package Day {self.package_day_number})'

class Booking(models.Model):
    booking_id = models.CharField(max_length=25, unique=True, editable=False)
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE,related_name='bookings')
    
    # Customer details
    full_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(max_length=200, blank=True, null=True)
    
    # Booking details
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_start_date = models.DateField()
    adults = models.PositiveIntegerField()
    kids_5_12 = models.PositiveIntegerField(default=0)
    kids_b_5 = models.PositiveIntegerField(default=0)
    
    # Pricing
    total_amount = models.FloatField(blank=True, null=True)
    advance_amount = models.FloatField(default=0.0)
    remaining_amount = models.FloatField(blank=True, null=True)
    
    # Status tracking
    booking_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Cancelled', 'Cancelled'),
            ('Completed', 'Completed'),
            ('In Progress', 'In Progress')
        ],
        default='Pending'
    )
    
    # Special requirements
    special_requests = models.TextField(max_length=500, blank=True, null=True)
    dietary_requirements = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate booking ID format: PKG-DEST1DEST2-TYPE-XXXXXX
            package_code = ''.join([word[:2].upper() for word in self.tour_package.name.split()[:2]])
            
            # Get destination codes
            destinations = self.tour_package.destination.all().order_by('destination_order')
            dest_codes = ''.join([dest.place.name[:2].upper() for dest in destinations[:3]])  # Max 3 destinations in code
            
            # Get tour type from first destination
            type_code = destinations.first().tour_type[:1].upper() if destinations.exists() else 'R'
            unique_code = str(uuid.uuid4())[:6].upper()
            
            self.booking_id = f"{package_code}-{dest_codes}-{type_code}-{unique_code}"
        
        # Calculate total amount if not set
        if not self.total_amount:
            base_price = self.tour_package.get_discounted_price()
            total_persons = self.adults + self.kids_5_12 + self.kids_b_5
            
            # Calculate with different pricing for adults and kids
            adult_total = self.adults * base_price
            kid_5_12_total = self.kids_5_12 * (base_price * 0.7)  # 30% discount for kids 5-12
            kid_b_5_total = self.kids_b_5 * (base_price * 0.5)   # 50% discount for kids below 5
            
            self.total_amount = adult_total + kid_5_12_total + kid_b_5_total
            self.remaining_amount = self.total_amount - self.advance_amount
        
        super().save(*args, **kwargs)
    
    def get_total_travelers(self):
        return self.adults + self.kids_5_12 + self.kids_b_5
    
    def __str__(self) -> str:
        return f'{self.booking_id} - {self.full_name} - {self.tour_package.name}'