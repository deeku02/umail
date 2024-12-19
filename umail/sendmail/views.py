import django.contrib.auth.models
from django.shortcuts import render, redirect
from .tasks import send_email_task
from .models import Email_log, EmailStatus
from django.http import HttpResponse
from .forms import UserRegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
import csv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import json
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime,timedelta
import pytz

genai.configure(api_key="AIzaSyD-w3B-jjyesP9f8ExJ5gd-Xd8PqXcUUPc")

@csrf_exempt
def gemini_prompt(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get("prompt")

            if not prompt:
                return JsonResponse({"error": "Prompt cannot be empty"}, status=400)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)

            return JsonResponse({"generated_text": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


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
                    "register"
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
    user = request.user
    sent_emails_count = Email_log.objects.filter(sender=user, status="sent").count()
    scheduled_emails_count = Email_log.objects.filter(
        sender=user, is_scheduled=True, scheduled_time__gt=timezone.now()
    ).count()
    failed_events_count = Email_log.objects.filter(sender=user, status="failed").count()

    context = {
        "sent_emails_count": sent_emails_count,
        "scheduled_emails_count": scheduled_emails_count,
        "failed_events_count": failed_events_count,
    }
    return render(request, "dashboard.html", context)


@csrf_exempt
@login_required
def process_csv(request):
    if request.method == "POST":
        upload_file = request.FILES["file"]
        message_content = request.POST.get("message", "")
        is_scheduled = request.POST.get("is_scheduled", "false").lower() == "true"
        scheduled_time_str = request.POST.get("scheduled_time", None)

        if not message_content:
            return JsonResponse({"error": "Message content is required."}, status=400)

        email_list = []
        failed_emails = []
        user = request.user

        try:
            decoded_file = upload_file.read().decode("utf-8").splitlines()
            csv_reader = csv.DictReader(decoded_file)

            for row in csv_reader:
                email = row.get("email")
                if email:
                    email_list.append(email)

            if is_scheduled and scheduled_time_str:
                scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%dT%H:%M")
                kolkata_tz = pytz.timezone("Asia/Kolkata")
                scheduled_time = kolkata_tz.localize(scheduled_time)
                print(f"Scheduled time (aware): {scheduled_time}")
                now = timezone.now()
                countdown = (scheduled_time - now).total_seconds()
                print(f"Countdown (seconds): {countdown}")
            else:
                scheduled_time = None
                countdown = 0

            for email in email_list:
                print("db")
                status = EmailStatus.PENDING if is_scheduled else EmailStatus.SENT
                email_log = Email_log.objects.create(
                    sender=user,
                    recipient_email=email,
                    status=status,
                    is_scheduled=is_scheduled,
                    scheduled_time=scheduled_time,
                )
                if is_scheduled and countdown > 0:
                    print("This is a scheduled email at time ", scheduled_time)
                    send_email_task.apply_async(
                        args=[email_log.id, message_content],
                        countdown=countdown,
                    )
                else:
                    print("This is not a scheduled email")
                    send_email_task.delay(email_log.id, message_content)

            return JsonResponse(
                {
                    "success": True,
                    "message": "Emails processed successfully.",
                    "email_count": len(email_list),
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse(
                {
                    "success": False,
                    "message": str(e),
                }
            )
    return JsonResponse({"error": "Invalid request."}, status=400)


def analytics(request):
    user=request.user
    email_logs=Email_log.objects.filter(sender=user)
    return render(request, "analytics.html", {"email_logs":email_logs})

from pytz import timezone as pytz_timezone

def settings(request):
    user = request.user
    now = timezone.now()
    kolkata_tz = pytz_timezone("Asia/Kolkata")
    now_kolkata = now.astimezone(kolkata_tz)
    scheduled_emails = Email_log.objects.filter(
        sender=user, is_scheduled=True, scheduled_time__gt=now_kolkata
    )
    schedules = [
        {
            "date": email.scheduled_time.astimezone(kolkata_tz).strftime("%d %b, %Y"),
            "time": email.scheduled_time.astimezone(kolkata_tz).strftime("%I:%M %p"),
            "recipient_email": email.recipient_email,
        }
        for email in scheduled_emails
    ]
    return render(request, "scheduled.html", {"schedules": schedules})
