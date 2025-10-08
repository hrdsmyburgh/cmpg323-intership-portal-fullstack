from django.contrib import admin
from django.urls import path, include

from job.views import home_view 
from job.views import job_list_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    
    path('', home_view, name='home'),
    path('listing/', job_list_view, name='job_listing'),
    
    path('', include('job.job_templates_urls')), 
    
    path('api/', include('job.urls')),
]