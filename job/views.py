from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render 
from django.db.models import Q

from .models import Job, Application
from .serializers import (
    JobSerializer, JobCreateSerializer,
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer
)

def home_view(request):
    """Renders the homepage with featured jobs and categories."""
    
    featured_jobs = Job.objects.filter(is_active=True).order_by('-posted_on')[:6]
    
    context = {
        'featured_jobs': featured_jobs,
        'categories': [
            {'name': 'Design & Creative', 'job_count': 653},
            {'name': 'Development', 'job_count': 658},
            {'name': 'Marketing', 'job_count': 400},
            {'name': 'Finance', 'job_count': 210},
        ]
    }
    
    return render(request, "index.html", context) 


def job_list_view(request):
    """
    Renders the job listing page (job_listing.html) with a list of all active jobs.
    """
    jobs = Job.objects.filter(is_active=True).order_by('-posted_on')
    
    context = {
        'jobs': jobs, 
    }
    return render(request, "job_listing.html", context)


def job_detail_view(request, pk):
    """
    Renders the single job detail page (job_details.html) for a specific job ID (pk).
    """
    job = get_object_or_404(Job, pk=pk)
    
    context = {
        'job': job, 
    }
    return render(request, "job_details.html", context) 

def application_form_view(request, job_id):
    """Renders the job application form, passing the job object to the template."""
    
    job = get_object_or_404(Job, id=job_id)
    
    context = {
        'job': job, 
    }
    
    return render(request, 'application_form.html', context)


class JobListAPIView(generics.ListAPIView):
    """List all active jobs with optional filtering"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('type')
        experience = self.request.query_params.get('experience')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(detailed_experience__icontains=search)
            )
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(type__icontains=job_type)
        if experience:
            queryset = queryset.filter(experience__icontains=experience)

        return queryset.order_by('-posted_on')


class JobCreateAPIView(generics.CreateAPIView):
    """Allow employers to create a new job"""
    serializer_class = JobCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can create jobs.")
        serializer.save() 


class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a job (employer only for updates/deletes)"""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if not hasattr(request.user, 'employer_profile') or job.employer != request.user.employer_profile:
            raise PermissionDenied("You can only edit your own job postings.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        if not hasattr(request.user, 'employer_profile') or job.employer != request.user.employer_profile:
            raise PermissionDenied("You can only delete your own job postings.")
        return super().destroy(request, *args, **kwargs)


class MyJobPostingsAPIView(generics.ListAPIView):
    """List all jobs posted by the logged-in employer"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view their job postings.")
        return Job.objects.filter(employer=user.employer_profile).order_by('-posted_on')


class ApplicationCreateAPIView(generics.CreateAPIView):
    """Students apply to a job"""
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Only students can apply for jobs.")
        
        serializer.save()


class MyApplicationsAPIView(generics.ListAPIView):
    """List all applications submitted by the logged-in student"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Only students can view their applications.")
        return Application.objects.filter(applicant=user.student_profile).order_by('-applied_date')


class EmployerApplicationsAPIView(generics.ListAPIView):
    """List all applications for a specific job (employer only)"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view job applications.")
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id, employer=user.employer_profile)
        return Application.objects.filter(job=job).order_by('-applied_date')


class ApplicationStatusUpdateAPIView(generics.UpdateAPIView):
    """Employers update the status or notes of an application"""
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()
    lookup_url_kwarg = 'application_id'

    def perform_update(self, serializer):
        application = self.get_object()
        user = self.request.user
        if not hasattr(user, 'employer_profile') or application.job.employer != user.employer_profile:
            raise PermissionDenied("You can only update applications for your own job postings.")
        serializer.save()


class ApplicationDetailAPIView(generics.RetrieveAPIView):
    """Retrieve an application (student or employer)"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()
    lookup_url_kwarg = 'application_id'

    def get_object(self):
        application = super().get_object()
        user = self.request.user
        if hasattr(user, 'student_profile') and application.applicant == user.student_profile:
            return application
        if hasattr(user, 'employer_profile') and application.job.employer == user.employer_profile:
            return application
        raise PermissionDenied("You do not have permission to view this application.")

class JobStatsAPIView(generics.GenericAPIView):
    """Return stats for an employer's jobs"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view job stats.")
        jobs = Job.objects.filter(employer=user.employer_profile)
        total_jobs = jobs.count()
        active_jobs = jobs.filter(is_active=True).count()
        total_applications = Application.objects.filter(job__in=jobs).count()
        return Response({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
        })