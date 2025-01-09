from django.db import models
from django.contrib.auth.models import User

STATE_CHOICES = (
    ('Banteay Meanchey', 'Banteay Meanchey'),
    ('Battambang', 'Battambang'),
    ('Kampong Cham', 'Kampong Cham'),
    ('Kampong Chhnang', 'Kampong Chhnang'),
    ('Kampong Speu', 'Kampong Speu'),
    ('Kampong Thom', 'Kampong Thom'),
    ('Kandal', 'Kandal'),
    ('Kep', 'Kep'),
    ('Koh Kong', 'Koh Kong'),
    ('Kratie', 'Kratie'),
    ('Mondulkiri', 'Mondulkiri'),
    ('Phnom Penh', 'Phnom Penh'),
    ('Preah Vihear', 'Preah Vihear'),
    ('Prey Veng', 'Prey Veng'),
    ('Pursat', 'Pursat'),
    ('Ratanakiri', 'Ratanakiri'),
    ('Siem Reap', 'Siem Reap'),
    ('Sihanoukville', 'Sihanoukville'),
    ('Stung Treng', 'Stung Treng'),
    ('Svay Rieng', 'Svay Rieng'),
    ('Takeo', 'Takeo'),
    ('Tboung Khmum', 'Tboung Khmum'),
)

CATEGORY_CHOICES = (
    ('CF', 'Coffee'),
    ('CB', 'Coffee Bean'),
    ('MSC', 'MilkShakeChocolate'),
    ('CFI', 'CoffeeFrapIce'),
    ('CO', 'Coffee'),
    ('IM', 'IceMocha'),
    ('CZ', 'Cheese'),
    ('IC', 'Ice-Coffee'),
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')  
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255)
    product_image = models.ImageField(upload_to='products/')
    
    def __str__(self):
        return self.title

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField(null=True, blank=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for {self.user.username} - {self.amount}"


    
    
class WishList(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Cart.STATUS_CHOICES, default='Pending') 
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="")

    @property
    def total_amount(self):
        return self.quantity * self.product.discounted_price
    
    def __str__(self):
        return f"Order of {self.quantity} x {self.product.title} by {self.user.username}"
    