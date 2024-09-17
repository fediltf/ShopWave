from django import forms
from django.forms import ModelForm
from .models import Product, Category


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Product Price'}),
            'digital': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'name': '',
            'price': '',
        }


class ContactForm(forms.Form):
    name = forms.CharField(label="", max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}), )
    email = forms.EmailField(label="",
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    subject = forms.CharField(label="", max_length=500,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject:'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control', 'placeholder': 'Your Message..'}),
        label=''
    )
