from django.db import models
from django.urls import reverse
# Create your models here.
from django.utils import timezone
from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=('Product name'))
    description = models.TextField(blank=True, verbose_name=('Description'))
    price = models.FloatField(verbose_name=('Price'))
    image = models.ImageField(upload_to='images/%Y/', verbose_name="Image")
    deleted = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
    def get_add_to_cart_url(self):
        return reverse('pos_app:add_to_cart', kwargs={'pk':self.pk})

    def get_edit_product_detail_url(self):
        return reverse('pos_app:edit_product_detail', kwargs={'pk': self.pk})
    
    def replace_image(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = Product.objects.get(pk=self.pk)
            if this.image != self.image:
                this.image.delete(save=False)
        except: pass
        super(Product, self).save(*args, **kwargs)

    def get_mark_deleted_url(self):
        return reverse('pos_app:mark_product_deleted', kwargs={'pk': self.pk})

class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=50)

    def __str__(self):
        return str(self.quantity) + " - " + self.product.name

    def get_name(self):
        return self.product.name

    def get_single_price(self):
        return round(self.product.price, 2)

    def get_total_price(self):
        return round(self.product.price * self.quantity, 2)

    def get_reduce_product_url(self):
        return reverse('pos_app:reduce_product', kwargs={'pk': self.pk})
    
    def get_remove_from_cart_url(self):
        return reverse("pos_app:remove_from_cart", kwargs={'pk': self.pk})

    

class Order(models.Model):
    products = models.ManyToManyField(OrderProduct)
    ip_address = models.CharField(max_length=50)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    added_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=80)

    
    def __str__(self):
        return "Order - " + str(self.pk )

    def get_total_price(self):
        sum = 0
        for ordered_product in self.products.all():
            sum += ordered_product.get_total_price();
        return round(sum, 2)

    def get_total_quantity(self):
        sum = 0
        if self.products.all().exists():
            for ordered_product in self.products.all():
                sum += ordered_product.quantity
        return sum
    
    def get_detail_view_url(self):
        return reverse('pos_app:order_detail', kwargs={'pk': self.pk})