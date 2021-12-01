from django.http.response import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse
from pos_app.models import Category, Product, OrderProduct, Order
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
    if request.is_ajax():
        category_name = request.GET.get("category")
        if category_name is not None:
            product_list = Product.objects.filter(categories__name=category_name)
        else:
            product_list = Product.objects.all()
        data = render_to_string("ajax/filter-menu.html", {"product_list": product_list})
        return JsonResponse({"data": data})
    current_ip = get_client_ip(request)
    product_list = Product.objects.filter(deleted=False)
    order = None
    ordered_product_list = None
    order_qs = Order.objects.filter(ordered=False, ip_address=current_ip)
    category_list = Category.objects.all()
    if order_qs.exists():
        order = order_qs[0]
        ordered_product_list = order.products.all()
    return render(request, "index.html", context={'product_list':product_list, 'ordered_product_list': ordered_product_list, 'order':order, 'category_list': category_list})

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
        for order_product in order.products.all():
            order_product.ordered = True
            order_product.save()
        order.added_date = timezone.now()
        order.name = (request.POST['fname'] + " " + request.POST['lname'])
        order.save()
        return render(request, "success.html", context={"order": order})
    return render(request, "checkout.html", context={"order": order, "ordered_product_list": ordered_product_list})

def manage_index(request):
    if not request.user.is_staff:
        return HttpResponse("Access denied!")
    return render(request, "manage/base.html")

def product_list(request):
    if not request.user.is_staff:
        return HttpResponse("Access denied!")
    category_list = Category.objects.all()
    if request.method == "POST":
        # Get category of that company
        assigned_category_name = request.POST['assigned_category']
        assigned_category = Category.objects.filter(name=assigned_category_name)[0]
        # objects are products
        object_pk_list = request.POST.getlist('object_list')
        if object_pk_list:
            object_list = Product.objects.filter(pk__in=object_pk_list)
            for object in object_list:
                object.categories.add(assigned_category)
            
        return redirect('pos_app:manage_product_list')
    if request.method == "GET":
        filter_category_name = request.GET.get('category')
        if filter_category_name is None:
            product_list = Product.objects.filter(deleted=False)
        else:
            product_list = Product.objects.filter(categories__name=filter_category_name, deleted=False)

    context_data = {
        'product_list': product_list,
        'category_list': category_list,
        'filter_category_name': filter_category_name,
    }
    return render(request, "manage/product-list.html", context=context_data)

class ProductCreateView(CreateView):
    form_class = ProductForm
    model = Product

    def get_success_url(self):
        return reverse('pos_app:manage_product_list')


def edit_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        edit_form = ProductForm(data=request.POST)
        if edit_form.is_valid():
            name = edit_form.cleaned_data['name']
            categories = edit_form.cleaned_data['categories']
            price = edit_form.cleaned_data['price']
            image = request.FILES.get('image', False)
            if price != product.price:
                order_products = OrderProduct.objects.filter(product=product)
                paid_order_products = OrderProduct.objects.filter(product=product, paid=True)
                if paid_order_products.exists():
                    if image == False:
                        new_product = Product.objects.create(name=name, price=price, image=product.image)
                        
                    else:
                        new_product = Product.objects.create(name=name, price=price, image=image)
                    product.image = None
                    product.deleted = True
                    product.save()
                    for category in categories:
                        new_product.categories.add(category)

                    # unpaid product will be updated to new price
                    unpaid_order_products = order_products.filter(product=product, paid=False)
                    if unpaid_order_products.exists():
                        for order_product in unpaid_order_products:
                            order_product.product = new_product
                            order_product.save()


                else:
                    product.name = name
                    product.categories.clear()
                    for category in categories:
                        product.categories.add(category)
                    product.price = price
                    if image != False:
                        product.image = image
                    product.save()
            else:
                product.name = name
                product.categories.clear()
                for category in categories:
                    product.categories.add(category)
                if image != False:
                    product.image = image
                product.save()
            
            return redirect('pos_app:manage_product_list')


    edit_form = ProductForm(initial={'name':product.name,'categories':product.categories.all(), 'price':product.price})

    return render(request, 'manage/product-edit.html', context={'product':product, 'edit_form': edit_form})


def mark_product_deleted(request, pk):
    if request.is_ajax:
        product = get_object_or_404(Product, pk=pk)
        product.deleted = True
        product.save()

    return JsonResponse({'nothing': ""}, status=200)

def order_list(request):
    if not request.user.is_staff:
        return HttpResponse("Access denied!")
    order_list = Order.objects.filter(ordered=True)
    return render(request, "manage/order-list.html", context={"order_list": order_list})

def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    ordered_product_list = order.products.all()
    return render(request, "manage/order_detail.html", context={'order': order, 'ordered_product_list': ordered_product_list})

class OrderDetailView(DetailView):
    model = Order

def add_category(request):
    if request.method == "POST":
        category_name = request.POST["category"]
        Category.objects.create(name=category_name)
        return redirect('pos_app:manage_product_list')
    return render(request, "manage/add-category.html")


def feedback(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "feedback.html", context={"order": order})


def search_results(request):
    if request.is_ajax():
        available = 0
        product = request.POST.get('product')
        qs = Product.objects.filter(name__icontains=product, deleted=False).order_by('name')
        if len(qs) > 0 and len(product) >0:
            res = render_to_string('ajax/search-product.html', {'qs': qs})
            available = 1
        else:
            res = "Not found..."

        return JsonResponse({'data': res, 'available':available})