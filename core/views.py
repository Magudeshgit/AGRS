from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from core.email_handler.fetch_emails import fetch_and_process_emails
from django.http import HttpResponse

from .forms import (
    CustomSignupForm,
    ComplaintForm,
    ComplaintResponseForm,
    DepartmentResponseForm
)
from .models import *
from core.utils.email_config import DEPARTMENT_EMAILS
from core.utils.whatsapp import send_whatsapp_message
from core.utils.phone import format_phone_number
from twilio.rest import Client
from core.utils.department_contacts import DEPARTMENT_PHONE_NUMBERS
from core.utils.priority_score import calculate_priority_score
from core.utils.department_contacts import classify_rule_based

THRESHOLD = 50
client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)


#  Classifier Logic  #

# def classify_department(title, description):
#     # train_classifier_llm()
#     complaint_count = Complaint.objects.count()
#     return predict_department_llm(title, description) if complaint_count >= THRESHOLD else classify_rule_based(title, description)
    # return classify_rule_based(title, description)


#  Auth Views  #
def signup_view(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('submit_complaint')
    else:
        form = CustomSignupForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on user type
            if user.user_type == 'staff':
                return redirect('department_dashboard')
            else:
                return redirect('submit_complaint')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


#  Complaint Submission  #
@login_required
def submit_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES, initial={"user": request.user})
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user

            

            #Calculate Priority Score
            complaint.priority_score = calculate_priority_score(
                complaint.title,
                complaint.description,
                complaint.user,
                complaint.title
            )
            complaint.save()

            send_whatsapp_message(
                to_number=complaint.user.,
                message_text=f"Hi {complaint.user.username}, your complaint titled \"{complaint.title}\" "
                            f"has been submitted successfully to the {complaint.department} department. "
                            f"Tracking ID: #{complaint.id}. You'll be notified once there's a response.",
                related_complaint=complaint,
                recipient_role='user'
            )

            # Notify department
            # department_phone = DEPARTMENT_PHONE_NUMBERS.get(complaint.department)
            if department_phone:
                send_whatsapp_message(
                    to_number=department_phone,
                    message_text=f"A new complaint (ID: {complaint.id}) titled \"{complaint.title}\" has been assigned "
                                f"to your department. Please respond via the portal.",
                    related_complaint=complaint,
                    recipient_role='department'
                )

            dept_email = DEPARTMENT_EMAILS.get(complaint.department, "grievance@college.edu")

            send_mail(
                subject=f"[New Complaint] - {complaint.title}",
                message=f"""A new complaint has been submitted.
                            Title: {complaint.title}
                            Department: {complaint.department}
                            Description:
                            {complaint.description}

                            Please respond via the portal with resolution or expected deadline.""",
                                            from_email=None,
                                            recipient_list=[dept_email],
                                            fail_silently=False,
                                        )

            messages.success(request, "Complaint submitted and email sent to concerned department.")

            LLMTrainingSample.objects.create(
                complaint_text=complaint.title + " " + complaint.description,
                department=complaint.department
            )

            return redirect("mine_complaints")
        else:
            print(form.errors)
    else:
        form = ComplaintForm()
    acad_depts = department.objects.filter(is_academic=True)
    return render(request, "submit.html", {"form": form, "acaddepts": acad_depts})


#  Complaint Views  #
@login_required
def mine_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "mine.html", {"complaints": complaints})


#  Department Dashboard  #
@login_required
def department_dashboard(request):
    user = request.user
    complaints = Complaint.objects.none()
    
    if user.user_type == "staff" and hasattr(user, 'department_name') and user.department_name:
        complaints = Complaint.objects.filter(department__iexact=user.department_name).order_by('-created_at')

    pending = complaints.filter(status='pending')
    in_progress = complaints.filter(status='in_progress')
    resolved = complaints.filter(status='resolved')

    return render(request, "department_dashboard.html", {
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved
    })


#  Department Response
@login_required
def respond_to_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.status = 'in_progress'
            complaint.responded_at = timezone.now()
            complaint.save()

            send_whatsapp_message(
                to_number=complaint.contact_phone,
                message_text=f"Hi {complaint.user.username}, your complaint \"{complaint.title}\" has received a response:\n\n"
                            f"{complaint.department_response}\n\n"
                            f"Status: {complaint.status}\nExpected resolution: {complaint.resolution_deadline or 'N/A'}\n"
                            f"Please review and acknowledge in the portal.",
                related_complaint=complaint,
                recipient_role='user'
            )

            subject = f"Response to Your Complaint: {complaint.title}"
            message = f"""
Dear {complaint.user.username},

Your complaint has been addressed.

Response: {complaint.department_response}
Deadline (if any): {complaint.resolution_deadline}

Please login to acknowledge or escalate the complaint.

Regards,
Grievance Team
"""
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [complaint.contact_email])
            messages.success(request, "Response submitted and user notified.")
            return redirect("department_dashboard")
    else:
        form = ComplaintResponseForm(instance=complaint)
    

    # Update/Create department score
    dept_score, created = DepartmentScore.objects.get_or_create(department_name=complaint.department)
    time_diff = timezone.now() - complaint.created_at

    if time_diff.days <= 2:
        dept_score.score += 5  # quick response
    else:
        dept_score.score += 2  # slow but responded

    dept_score.save()

    return render(request, "respond.html", {"form": form, "complaint": complaint})


@login_required
def mark_resolved(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    if complaint.status == "in_progress":
        complaint.status = "resolved"
        complaint.save()
        messages.success(request, "Complaint marked as resolved.")
    return redirect("mine_complaints")


@login_required
def escalate_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    if complaint.status == "in_progress":
        complaint.status = "pending"
        complaint.save()
        messages.success(request, "Complaint escalated. Department will be notified again.")
    return redirect("mine_complaints")


from django.views.decorators.http import require_POST

@require_POST
@login_required
def acknowledge_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    action = request.POST.get("action")
    if action == "close":
        request.user.user_score += 5  # reward
        request.user.save()
        complaint.status = "resolved"
        complaint.save()
        dept_phone = DEPARTMENT_PHONE_NUMBERS.get(complaint.department)
        if dept_phone:
            send_whatsapp_message(
                to_number=dept_phone,
                message_text=f"Complaint #{complaint.id} titled \"{complaint.title}\" has been marked as resolved by the user.",
                related_complaint=complaint,
                recipient_role='department'
            )
        messages.success(request, "Complaint marked as resolved.")
    elif action == "escalate":
        request.user.user_score -= 3  # penalize
        request.user.save()
        # dept_score, _ = DepartmentScore.objects.get_or_create(department_name=complaint.department)
        dept_score.score -= 4
        dept_score.save()
        messages.info(request, "Complaint escalated.")
    return redirect("mine_complaints")
from django.http import HttpResponse
from core.email_handler.fetch_emails import fetch_and_process_emails

def fetch_emails_view(request):
    fetch_and_process_emails()
    return HttpResponse("Fetched and processed new emails.")
