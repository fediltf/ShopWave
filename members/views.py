from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm

from members.forms import RegisterUserForm
from store.models import Customer

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.success(request, "Error logging in, Try Again..")
            return redirect(request.get_full_path())
    else:
        return render(request, 'authentication/login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, "Logged Out..")
    return redirect('store')


def register_user(request):
    form = RegisterUserForm()
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            user = authenticate(request, username=username, password=password)
            customer = Customer.objects.create(user=user, name=username, email=email)
            login(request, user)
            messages.success(request, "Registred..")
            return redirect('store')
    return render(request, 'authentication/register.html', {
        'form': form,
    })


