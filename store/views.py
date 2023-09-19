from django.shortcuts import render
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import datetime


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

        context = {'items': items, 'order': order, 'cartItems': cartItems}
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


#
# @csrf_exempt
# def processOrder(request):
#     transaction_id = datetime.datetime.now().timestamp()
#     data = json.loads(request.body)
#     if request.user.is_authenticated:
#         customer = request.user.customer
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)
#         total = float(data['form']['total'])
#         order.transaction_id = transaction_id
#         if total == order.get_cart_total:
#             order.complete = True
#         order.save()
#         if order.shipping == True:
#             ShippingAddress.objects.create(
#                 customer=customer,
#                 order=order,
#                 adress=data['shipping']['adress'],
#                 city=data['shipping']['city'],
#                 state=data['shipping']['state'],
#                 zipcode=data['shipping']['zipcode']
#             )
#     else:
#         print('User is not logged in')
#     return JsonResponse('payment complete!', safe=False)

# class ProcessOrderView(View):
#     @csrf_exempt
#     def post(self, request):
#         transaction_id = datetime.datetime.now().timestamp()
#         data = json.loads(request.body)
#         if request.user.is_authenticated:
#             customer = request.user.customer
#             order, created = Order.objects.get_or_create(customer=customer, complete=False)
#             total = float(data['form']['total'])
#             order.transaction_id = transaction_id
#             if total == order.get_cart_total():  # You should call the method with parentheses
#                 order.complete = True
#             order.save()
#             if order.shipping:
#                 ShippingAddress.objects.create(
#                     customer=customer,
#                     order=order,
#                     address=data['shipping']['address'],  # Correct the key to 'address'
#                     city=data['shipping']['city'],
#                     state=data['shipping']['state'],
#                     zipcode=data['shipping']['zipcode']
#                 )
#         else:
#             print('User is not logged in')
#         return JsonResponse('payment complete!', safe=False)

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


class SearchProductView(View):
    template_name = 'store/search_product.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        searched = request.POST.get('searched')
        searched_products = Product.objects.filter(name__contains=searched)
        return render(request, self.template_name, {'searched': searched, 'searched_products': searched_products})


class ContactView(View):
    template_name = 'store/contact_us.html'

    def get(self, request):
        return render(request, self.template_name, {})