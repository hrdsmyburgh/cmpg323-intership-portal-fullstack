from django.urls import path
from . import views 

urlpatterns = [
    path('listing/', views.job_list_view, name='job_listing'),
    
    path(
        'job_detail/<int:pk>/', 
        views.job_detail_view, 
        name='job_details'
    ),
    
    path(
        'apply/<int:job_id>/', 
        views.application_form_view, 
        name='application_form'
    ),
]