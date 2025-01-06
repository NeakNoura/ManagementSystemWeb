from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
import razorpay
from . models import Cart, Customer, OrderPlaced, Product
from django.db.models import Count
from . forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

def home(request):
    return render (request, "app/home.html")
def about(request):
    return render (request, "app/about.html")
def contact(request):
    return render (request, "app/contact.html")
class CategoryView(View):
    def get(self,request ,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
class ProductDetail(View):
    def get(self,request,pk):
        product= Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())


class CategoryTitle(View):
    def get(self,request,pk,val):
        product= Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0]).values('title')
        return render(request,"app/category.html",locals())

class CustomerRegistrationView(View):
    
    def get(self,request):
        form = CustomerRegistrationForm()
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
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form =CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality =form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcpode = form.cleaned_data['zipcode']
            
            reg =Customer(user= user ,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcpode)
            reg.save()
            messages.success(request,"Pofile Saved")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/profile.html',locals())

def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',locals())
class updateAddress(View):
    def get(self,request,pk):
        add =Customer.objects.get(pk=pk)
        form = CustomerProfileForm(request.POST,instance=add)
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form =CustomerProfileForm(request.POST)
        if form.is_valid():
           
            add =Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality =form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulation! Profile Update Successfully")
        else:
            messages.warning(request,"Invalid Input Data")           
        return redirect("address")

def orders(request):
    orders = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'orders': orders})

def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product =Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")
    
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount+40

    return render(request,'app/addtocart.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &  Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount+40
        print(prod_id)
        data={'quantity':c.quantity,
              'amount':amount,
              'totalamount': totalamount
            
        }
        return JsonResponse(data)
class checkout(View):
    def get(self,request):
        user = request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            amount = famount + value
            totalamount = famount + 40
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
            data={"amount":"razoramount","currency":"IMR","receipt":"order_rcptid_12"}
            payment_response = client.order.create(data=data)
            print (payment_response)
            order_id = payment_response['id']
            order_status = payment_response['status']
            if order_status == 'created':
                payment = razorpay.Payment(
                    user=user,
                    amount = totalamount,
                    razorpay_order_id=order_id,
                    razorpay_payment_status  = order_status
                )
                payment.save()
        return render(request,'app/checkout.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &  Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount+40
        print(prod_id)
        data={'quantity':c.quantity,
              'amount':amount,
              'totalamount': totalamount
            
        }
        return JsonResponse(data)

    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &  Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount+40
        data={'quantity':c.quantity,
              'amount':amount,
              'totalamount': totalamount
            
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &  Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount+40
        data={
              'amount':amount,
              'totalamount': totalamount 
             }
        return JsonResponse(data)


def payment_done(request):
    try:
        razorpay_order_id = request.GET.get('order_id')
        razorpay_payment_id = request.GET.get('payment_id')
        cust_id = request.GET.get('cust_id')

        # Replace with your actual model to handle payments, not the Razorpay model
        payment = razorpay.Payment.objects.get(razorpay_order_id=razorpay_order_id)

        # Verify signature
        razorpay_signature = request.GET.get('signature')
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # Verify payment signature
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params_dict)

            # Update payment status
            payment.razorpay_payment_status = 'paid'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.paid = True
            payment.save()

            # Update the order status
            order = OrderPlaced.objects.get(razorpay_order_id=razorpay_order_id)
            order.payment = payment
            order.status = 'Paid'
            order.save()

            messages.success(request, "Payment successful! Your order is confirmed.")
            return redirect('order_success')  # Redirect to order success page (change URL as needed)

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment failed! Signature mismatch.")
            return redirect('payment_failed')  # Redirect to failure page (change URL as needed)

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('payment_failed')  # Redirect to failure page (change URL as needed)
