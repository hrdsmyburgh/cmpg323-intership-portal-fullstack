from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, StudentForm
from .models import Student

# Registration
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == "student":
                Student.objects.create(user=user, student_id=f"STU{user.id:04d}")
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Registration failed. Please check the form details.")
    else:
        form = UserCreationForm()
    return render(request, "registrationpage.html", {"form": form})

# Login
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            if hasattr(user, 'employer_profile'):
                return redirect("users:employer_dashboard")
            elif hasattr(user, 'student_profile'):
                 return redirect("home") 
            
            return redirect("home")
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

# Logout
def logout_view(request):
    logout(request)
    return render(request, "logged_out.html")

# Student Profile
@login_required
def student_profile(request):
    if not hasattr(request.user, "student_profile"):
        messages.error(request, "No student profile found")
        return redirect("home")
    profile = request.user.student_profile
    return render(request, "studentprofile.html", {"profile": profile})

# CV Upload
@login_required
def upload_cv_view(request):
    if not hasattr(request.user, "student_profile"):
        messages.error(request, "Only students can upload CVs")
        return redirect("home")

    profile = request.user.student_profile

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=profile) 
        if form.is_valid():
            form.save()
            messages.success(request, "CV uploaded successfully")
            return redirect("users:student_profile") 
        else:
            messages.error(request, "Upload failed. Check file type and try again.")
            return redirect("users:student_profile")


# EMPLOYER VIEW
@login_required
def employer_dashboard(request):
    """
    Renders the employer dashboard page, accessible via the URL /users/employer/dashboard/.
    It checks if the user is logged in and has an employer profile.
    """
    if not hasattr(request.user, "employer_profile"):
        messages.error(request, "Access denied. Only registered employers can view this page.")
        return redirect("home") 
    
    profile = request.user.employer_profile
    
    context = {
        'profile': profile,
    }
    
    return render(request, "employeradminpage.html", context)