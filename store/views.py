from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import render, redirect
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import datetime
from .forms import ProductForm, ContactForm
from django.contrib import messages


class StoreView(View):
    template_name = 'store/store.html'

    def get(self, request):
        data = cartData(request)
        order = data['order']
        items = data['items']
        cartItems = data['cartItems']
        category = request.GET.get('category')
        sort_by = request.GET.get("sort")
        products = Product.objects.all()
        if category:
            products = products.filter(category__name=category)

        if sort_by == "l2h":
            products = products.order_by("price")
        elif sort_by == "h2l":
            products = products.order_by("-price")
        else:
            products = products.order_by("name")

        categories = Category.objects.all()
        context = {'products': products, 'cartItems': cartItems, 'categories': categories, 'category': category}
        return render(request, self.template_name, context)


class CartView(View):
    template_name = 'store/cart.html'

    def get(self, request):
        data = cartData(request)
        items = data['items']
        order = data['order']
        cartItems = data['cartItems']
        categories = Category.objects.all()
        context = {'items': items, 'order': order, 'cartItems': cartItems, 'categories': categories}
        return render(request, self.template_name, context)


class CheckoutView(View):
    template_name = 'store/checkout.html'

    def get(self, request):
        data = cartData(request)
        items = data['items']
        order = data['order']
        cartItems = data['cartItems']
        context = {'items': items, 'order': order, 'cartItems': cartItems}
        return render(request, self.template_name, context)


class UpdateitemView(View):
    def post(self, request):
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        print('Action:', action)
        print('ProductId:', productId)

        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = orderItem.quantity + 1
        elif action == 'remove':
            orderItem.quantity = orderItem.quantity - 1
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

# ------ SEARCH-PRODUCTS ------
class SearchProductView(View):
    template_name = 'store/search_product.html'
    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        searched = request.POST.get('searched')
        searched_products = Product.objects.filter(name__contains=searched)
        return render(request, self.template_name, {'searched': searched, 'searched_products': searched_products})


# ------ CRUD Products ------
class AddProductView(View):
    def get(self, request):
        form = ProductForm()
        submitted = False
        if 'submitted' in request.GET:
            submitted = True
        categories = Category.objects.all()
        return render(request, 'store/add_product.html',
                      {'categories': categories, 'form': form, 'submitted': submitted})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect('/add_product?submitted=True')
            messages.success(request, "Product added successfully!")
            return redirect('store')
        categories = Category.objects.all()
        return render(request, 'store/add_product.html', {'categories': categories, 'form': form})


def update_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully!")
        return redirect('store')
    return render(request, 'store/update_product.html', {'product': product, 'form': form})


def delete_product(request, product_id):
    try:
        item = OrderItem.objects.get(product__id=product_id)
        item.delete()
    except:
        pass
    product = Product.objects.get(pk=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('store')

# ------ CONTACT US ------
def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = request.POST.get("subject", "")
            message = request.POST.get("message", "")
            from_email = request.POST.get("email", "")
            if subject and message and from_email:
                try:
                    send_mail(subject, message, from_email, ["contact@shopwave.com"])
                except BadHeaderError:
                    messages.success(request, "Invalid header found.")
                    return redirect(request.get_full_path())
                messages.success(request,
                                 "Thanks! Our team will come back to you within a matter of hours to help you.")
                return redirect('store')

            else:
                messages.success(request, "Make sure all fields are entered and valid.")
                return redirect(request.get_full_path())
            return redirect('store')
    else:
        form = ContactForm()

    return render(request, 'store/contact_us.html', {'form': form})
