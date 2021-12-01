from django.urls import path
from . import views

app_name = "pos_app"
urlpatterns =[
    path('', views.index, name='index'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name="add_to_cart"),
    path('reduce-product/<int:pk>/', views.reduce_product, name="reduce_product"),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name="remove_from_cart"),
    path('payment-choice/', views.select_payment_method, name="payment_choice"),
    path('checkout/', views.check_out, name='checkout'),
    path('manage/index/', views.manage_index, name="manage_index"),
    path('manage/product-list/', views.product_list, name="manage_product_list"),
    path('mange/add-product/', views.ProductCreateView.as_view(template_name="manage/product_create.html"), name="add_product"),
    path('manage/product/edit-detail/<int:pk>',views.edit_product_detail, name='edit_product_detail'),
    path('manage/product/mark-deleted/<int:pk>',views.mark_product_deleted, name='mark_product_deleted'),
    path('manage/order-list/', views.order_list, name="order_list"),
    path('manage/order/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('manage/add-category/', views.add_category, name="add-category"),
    path('feedback/<int:pk>/', views.feedback, name="feedback"),
    path('search-product/', views.search_results, name="search-product"),
]