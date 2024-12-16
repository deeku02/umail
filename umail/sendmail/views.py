from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
import csv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(
            request.POST
        )  # Replace LoginForm with AuthenticationForm if using it
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(
                    "dashboard"
                )  # Replace 'home' with the name of your home page URL
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})


def dashboard_view(request):
    return render(request, "dashboard.html", {})

@csrf_exempt
def process_csv_file(request):
    if request.method=='POST' and request.FILES.get('file'):
        upload_file=request.FILES['file']
        email_list=[]

        try:
            decoded_file=upload_file.read().decode("utf-8").splitlines()
            csv_reader=csv.DictReader(decoded_file)

            for row in csv_reader:
                email=row.get("email")
                if email:
                    email_list.append(email)

            return JsonResponse({
            "message": "CSV file processed successfully!",
                "emails": email_list,
                "email_count": len(email_list),
                })
        except Exception as e:
            return JsonResponse({"error":str(e)},status=400)
    return JsonResponse({"error":"InvalidRequest"},status=400)

def analytics(request):
    return render(request,"analytics.html",{})

def settings(request):
    return render(request,'settings.html',{})