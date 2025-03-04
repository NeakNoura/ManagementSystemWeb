from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
import razorpay
from . models import Cart, Customer, OrderPlaced, Payment, Product, WishList
from django.db.models import Count
from . forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Cart, Product
from django.conf import settings
from django.shortcuts import get_object_or_404


def home(request):
    totalitem= 0
    if request.user.is_authenticated:
        totalitem = (Cart.objects.filter(user=request.user).count())
    return render (request, "app/home.html")
        
def about(request):
    totalitem= 0
    if request.user.is_authenticated:
        totalitem = (Cart.objects.filter(user=request.user).count())
    return render (request, "app/about.html",locals())

def contact(request):
    totalitem= 0
    if request.user.is_authenticated:
        totalitem = (Cart.objects.filter(user=request.user).count())
    return render (request, "app/contact.html",locals())

class CategoryView(View):
    
    def get(self,request ,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
class ProductDetail(View):
    def get(self,request,pk):
        product= Product.objects.get(pk=pk)
        wishlist = WishList.objects.filter(Q(product=product) & Q(user=request.user))
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,"app/productdetail.html",locals())

class CategoryTitle(View):
    def get(self,request,pk,val):
        product= Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0]).values('title')
        return render(request,"app/category.html",locals())

class CustomerRegistrationView(View):
    
    def get(self,request):
        form = CustomerRegistrationForm()
        totalitem = 0 
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/customerregistration.html',locals())
    
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Login Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/customerregistration.html',locals())


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            customer, created = Customer.objects.get_or_create(user=user)
            customer.name = name
            customer.locality = locality
            customer.city = city
            customer.mobile = mobile
            customer.state = state
            customer.zipcode = zipcode
            customer.save()

            if created:
                messages.success(request, "Profile created successfully!")
            else:
                messages.success(request, "Profile updated successfully!")

            return redirect('profile')

        else:
            messages.warning(request, "Invalid Input Data")
        
        return render(request, 'app/profile.html', {'form': form})

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add})

class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)  
        return render(request, 'app/updateAddress.html', {'form': form, 'add': add})

    def post(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(request.POST, instance=add) 
        if form.is_valid():
            form.save() 
            messages.success(request, "Congratulations! Profile Updated Successfully")
            return redirect("address") 
        else:
            messages.warning(request, "Invalid Input Data")
            return render(request, 'app/updateAddress.html', {'form': form, 'add': add})
        
        
        
def orders(request):
    orders_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'orders_placed': orders_placed})



def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    next_url = request.GET.get('next', '/')

    if product_id:
        product = get_object_or_404(Product, id=product_id)


        cart_items = Cart.objects.filter(user=user, product=product)

        if cart_items.exists():
            cart_item = cart_items.first()  
            cart_item.quantity += 1
            cart_item.save()


            if cart_items.count() > 1:
                total_quantity = sum(item.quantity for item in cart_items)
                cart_item.quantity = total_quantity
                cart_item.save()

              
                cart_items.exclude(id=cart_item.id).delete()
        else:
            Cart.objects.create(user=user, product=product, quantity=1)

    return redirect(next_url)


def show_cart(request):
    totalitem = 0  
    if request.user.is_authenticated:  
        cart = Cart.objects.filter(user=request.user)
        totalitem = cart.count()  

        if cart.exists():  
            amount = sum(item.product.discounted_price * item.quantity for item in cart)
            totalamount = amount  
        else:
            amount = 0
            totalamount = 0

        context = {
            'cart': cart,  # Pass cart items to the template
            'amount': amount,
            'totalamount': totalamount,
            'totalitem': totalitem
        }
        return render(request, 'app/addtocart.html', context)
    
    return render(request, 'app/addtocart.html', {'cart': None, 'totalitem': totalitem})  # If user is not logged in


class Checkout(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to proceed to checkout.")
            return redirect('login')  
        
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount += value
        totalamount = famount + 40
        
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        razoramount = int(totalamount * 100)  
        data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        
        return render(request, 'app/checkout.html', locals())



def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        if cart_items.exists():
            c = cart_items.first()  
            c.quantity += 1
            c.save()
        else:
            c = Cart.objects.create(product_id=prod_id, user=request.user, quantity=1)
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        totalamount = amount + 40  
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        if cart_items.exists():
            c = cart_items.first()
            if c.quantity > 1:
                c.quantity -= 1 
                c.save()
            else:
                c.delete() 
        else:
            return JsonResponse({'error': 'Item not found in cart'}, status=404)
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        totalamount = amount + 40  
        data = {
            'quantity': c.quantity if cart_items.exists() else 0, 
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  
        print("Received request to remove product with ID:", prod_id)

        if not prod_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        user = request.user
        cart_item = Cart.objects.filter(Q(product__id=prod_id) & Q(user=user)).first()

        if not cart_item:
            print("Cart item not found!")
            return JsonResponse({'error': 'Product not found in cart'}, status=404)

        print(f"Before update: {cart_item.quantity}")

        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
            cart_item.save()
            print(f"After update: {cart_item.quantity}")
        else:
            print("Deleting product from cart")
            cart_item.delete()

        # Recalculate total
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        totalamount = amount + 40  

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount,
            'quantity': cart_item.quantity if cart_item.quantity > 0 else 0
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def payment_done(request):
    try:
        razorpay_order_id = request.GET.get('order_id')
        razorpay_payment_id = request.GET.get('payment_id')
        cust_id = request.GET.get('cust_id')
        payment = razorpay.Payment.objects.get(razorpay_order_id=razorpay_order_id)

        razorpay_signature = request.GET.get('signature')
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params_dict)

            payment.razorpay_payment_status = 'paid'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.paid = True
            payment.save()
            order = OrderPlaced.objects.get(razorpay_order_id=razorpay_order_id)
            order.payment = payment
            order.status = 'Paid'
            order.save()

            messages.success(request, "Payment successful! Your order is confirmed.")
            return redirect('order_success') 

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment failed! Signature mismatch.")
            return redirect('payment_failed')  

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('payment_failed')  

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.get(prod_id)
        product = Product.objects.get(id=prod_id)
        wishlist = request.user
        data={
            'message':"wishlist Adde Successfully",
        }
        return JsonResponse(data)
    
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.get(prod_id)
        product = Product.objects.get(id=prod_id)
        user = request.user
        WishList.objects.filter(user=user,product=product).delete()
        data={
            'message':"wishlist Remove Successfully",
        }
        return JsonResponse(data)
    
    
def search(request):
    query =  request.GET['search']
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist = len(WishList.objects.filter(user=request.user))
        
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())