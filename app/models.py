from django.db import models
from django.contrib.auth.models import User

STATE_CHOICES=(
    ('Andaman & Nicobar Islands','Andaman & Nicobar Islands'
    ),
    ('Andhra Pradesh','Andhra Pradesh'),
    ('Arunchal Pradesh','Arunachal Pradesh'),
    ('Assam','Assam'),
    ('Bihar','Bihar'),
    ('Chandigarh','Chandigarh'),
    ('Chattisgarh','Chattigarh'),
    ('Dadra & Nagae=r Haveli','Daman and Diu'),
    ('Delhi','Delhi'),
    ('Goa','Goa'),
    ('Guujrat','Gujrat'),
    ('Haryana','Haryana'),
    ('Himachal Pradesh','Himachal Pradesh'),
    ('Jammu & kashmir','jammu & kashmir'),
)
CATEGORY_CHOICES=(
('CR','Curd'),
('ML','Milk'),
('LS','Lassi'),
('MS','MilkShake'),
('PN','Panner'),
('GH',"Ghee"),
('CZ','Cheese'),
('IC','Ice-Creams'),
)
# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price =models.FloatField()
    description = models.FloatField()
    composition =  models.FloatField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255)
    product_image = models.ImageField(upload_to='products/')
    
    
    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    
    def __str__(self):
        return self.name