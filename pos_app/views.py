from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, HttpResponse
from pos_app.models import Product, OrderProduct, Order
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import ProductForm, ImageForm
from django.views.generic import CreateView, DetailView
from django.utils import timezone
# Create your views here.


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    current_ip = get_client_ip(request)
    product_list = Product.objects.filter(deleted=False)
    order = None
    ordered_product_list = None
    order_qs = Order.objects.filter(ordered=False, ip_address=current_ip)
    if order_qs.exists():
        order = order_qs[0]
        ordered_product_list = order.products.all()
    return render(request, "index.html", context={'product_list':product_list, 'ordered_product_list': ordered_product_list, 'order':order})

def add_to_cart(request, pk):
    current_ip = get_client_ip(request)
    if request.is_ajax and request.method == "GET":
        product = get_object_or_404(Product, pk=pk)
        order_product_qs = OrderProduct.objects.filter(product=product, ip_address=current_ip, ordered=False)
        if order_product_qs.exists():
            order_product = order_product_qs[0]
        else:
            order_product = OrderProduct.objects.create(
                product=product, ip_address=current_ip)
        order_qs = Order.objects.filter(ip_address=current_ip, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__pk=product.pk).exists():
                order_product.quantity += 1
                order_product.save()
            else:
                order.products.add(order_product)
                t = render_to_string('ajax/add-product.html', {'ordered_product': order_product, 'product':product})
                return JsonResponse({'data':t})
        else:
            order = Order.objects.create(ip_address=current_ip)
            order.products.add(order_product)
            t = render_to_string('ajax/add-product.html', {'ordered_product': order_product, 'product':product})
            return JsonResponse({'data':t})
        # For sales statistic only
    return HttpResponse("nothing")
       

def reduce_product(request, pk):
    ordered_product = get_object_or_404(OrderProduct, pk=pk)
    ordered_product.quantity -= 1
    ordered_product.save()
    return HttpResponse("nothing")

def remove_from_cart(request, pk):
    ordered_product = get_object_or_404(OrderProduct, pk=pk)
    ordered_product.delete()
    return HttpResponse("nothing")

def select_payment_method(request):
    current_ip = get_client_ip(request)
    order = None
    ordered_product_list = None
    order_qs = Order.objects.filter(ip_address=current_ip, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        ordered_product_list = order.products.all()
    return render(request, "payment-choice.html", context={'order':order, 'ordered_product_list':ordered_product_list})

def check_out(request):
    current_ip = get_client_ip(request)
    order = None
    ordered_product_list = None
    order_qs = Order.objects.filter(ip_address=current_ip, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        ordered_product_list = order.products.all()
    if request.method == "POST":
        order.ordered=True
        order.added_date = timezone.now()
        order.name = (request.POST['fname'] + " " + request.POST['lname'])
        order.save()
        return render(request, "success.html")
    return render(request, "checkout.html", context={"order": order, "ordered_product_list": ordered_product_list})

def manage_index(request):
    return render(request, "manage/base.html")

def product_list(request):
    product_list = Product.objects.filter(deleted=False)
    return render(request, "manage/product-list.html", context={'product_list': product_list})

class ProductCreateView(CreateView):
    form_class = ProductForm
    model = Product

    def get_success_url(self):
        return reverse('pos_app:manage_product_list')


def edit_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.save()
        form = ImageForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            if form.cleaned_data['image']:
                product.image = request.FILES['image']
                product.replace_image()
                product.save()
    else:
        form = ImageForm()

    return render(request, 'manage/product-edit.html', context={'product': product, 'form': form})

def mark_product_deleted(request, pk):
    if request.is_ajax:
        product = get_object_or_404(Product, pk=pk)
        product.deleted = True
        product.save()

    return JsonResponse({'nothing': ""}, status=200)

def order_list(request):
    order_list = Order.objects.filter(ordered=True)
    return render(request, "manage/order-list.html", context={"order_list": order_list})

def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    ordered_product_list = order.products.all()
    return render(request, "manage/order_detail.html", context={'order': order, 'ordered_product_list': ordered_product_list})

class OrderDetailView(DetailView):
    model = Order
