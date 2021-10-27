from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    description = forms.CharField(label='Mô tả', widget=forms.Textarea(attrs={'id': "description", "class": "control-form"}))
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta():
        model = Product
        exclude = ('deleted',)


class ImageForm(forms.Form):
    image = forms.ImageField(required=False, label="Image")