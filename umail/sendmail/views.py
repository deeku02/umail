
from django.shortcuts import render,redirect
from .forms import UserRegistrationForm,LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate,login


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Replace LoginForm with AuthenticationForm if using it
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('register')  # Replace 'home' with the name of your home page URL
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request,'login.html',{'form':form})


def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=UserRegistrationForm()
    return render(request, "register.html",{'form':form})
