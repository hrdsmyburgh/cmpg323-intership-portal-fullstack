from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Employer

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_student():
            Student.objects.create(user=instance, student_id=f"STU{instance.pk:04d}")
        elif instance.is_employer():
            Employer.objects.create(user=instance, employer_id=f"EMP{instance.pk:04d}")
