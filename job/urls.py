from django.urls import path
from .views import (
    JobListAPIView, JobCreateAPIView, JobDetailAPIView,
    MyJobPostingsAPIView, JobStatsAPIView,
    ApplicationCreateAPIView, MyApplicationsAPIView,
    EmployerApplicationsAPIView, ApplicationStatusUpdateAPIView,
    ApplicationDetailAPIView,
)

urlpatterns = [
    path('jobs/', JobListAPIView.as_view(), name='job-list'),
    path('jobs/create/', JobCreateAPIView.as_view(), name='job-create'),
    path('jobs/<int:pk>/', JobDetailAPIView.as_view(), name='job-detail'),
    path('jobs/my/', MyJobPostingsAPIView.as_view(), name='my-jobs'),
    path('jobs/stats/', JobStatsAPIView.as_view(), name='job-stats'),

    path('applications/create/', ApplicationCreateAPIView.as_view(), name='application-create'),
    path('applications/my/', MyApplicationsAPIView.as_view(), name='my-applications'),
    path('applications/job/<int:job_id>/', EmployerApplicationsAPIView.as_view(), name='employer-applications'),
    path('applications/<int:application_id>/update-status/', ApplicationStatusUpdateAPIView.as_view(), name='application-update-status'),
    path('applications/<int:application_id>/', ApplicationDetailAPIView.as_view(), name='application-detail'),
]