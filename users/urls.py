from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/upload-cv/', views.upload_cv_view, name='upload_cv'),
    
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'), 
]