from django import forms
from .models import Product, Category
from django.contrib.auth.forms import AuthenticationForm

# class ProductForm(forms.ModelForm):
#     description = forms.CharField(label='Mô tả', widget=forms.Textarea(attrs={'id': "description", "class": "control-form"}))
#     def __init__(self, *args, **kwargs):
#         super(ProductForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'
#     class Meta():
#         model = Product
#         exclude = ('deleted',)

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': '','name': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '',
            'id': 'hi',
            'name': 'password',
        }
))

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['categories'].widget = forms.CheckboxSelectMultiple()
        self.fields['categories'].queryset = Category.objects.all()


    class Meta():
        model = Product
        exclude = ('deleted', 'description')


class ImageForm(forms.Form):
    image = forms.ImageField(required=False, label="Image")