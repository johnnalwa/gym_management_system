from django.db import models
from embed_video.fields import EmbedVideoField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_member = models.BooleanField(default=False)
    is_management = models.BooleanField(default=False)


class InstructorTable(models.Model):
    id = models.AutoField(primary_key=True, default=1)  # Provide a default value for the id field
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=255, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
   

    def __str__(self):
        return self.user.username



class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    physical_address = models.TextField(max_length=255, null=True, blank=True)
    primary_phone_number = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    profile_img = models.ImageField(upload_to='Profile', default='default.png', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class AttendanceTable(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    class_id = models.IntegerField()
    attendance_date = models.DateField()



class GymClass(models.Model):
    CLASS_CHOICES = [
        ('Yoga', 'Yoga'),
        ('Zumba', 'Zumba'),
        ('Pilates', 'Pilates'),
        ('Spin', 'Spin'),
        # Add more class choices as needed
    ]
    
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    class_name = models.CharField(max_length=50, choices=CLASS_CHOICES)
    instructor = models.CharField(max_length=100)
    description = models.TextField()
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time = models.TimeField()
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.class_name} - {self.day}"


class EquipmentTable(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)  # Added a name field for demonstration
    quantity = models.IntegerField()
    last_maintenance_date = models.DateField()

class LiveStreamSessionsTable(models.Model):
    session_id = models.AutoField(primary_key=True)
    # class_id = models.ForeignKey(ClassesTable, on_delete=models.CASCADE)
    youtube_video_id = models.CharField(max_length=20, default='1')
    start_time = models.TimeField()
    end_time = models.TimeField()

class OnDemandWorkoutTable(models.Model):
    workout_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = EmbedVideoField()  # Use EmbedVideoField for YouTube video URL
    duration = models.DurationField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)  # Change ForeignKey to User model

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If the instructor is not set and a user is logged in, set the currently logged-in user as the instructor
        if not self.instructor_id and hasattr(self, 'request') and self.request.user.is_authenticated:
            self.instructor = self.request.user
        super().save(*args, **kwargs)

        

class PaymentTable(models.Model):
    payment_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

class GymLocationTable(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

class MembershipTable(models.Model):
    membership_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    membership_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

class TrainerCertificationTable(models.Model):
    certification_id = models.AutoField(primary_key=True)
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    expiration_date = models.DateField()
    instructors = models.ManyToManyField(InstructorTable, blank=True)

class ScheduleTable(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(GymClass, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']



class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who added the appointment
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE)  # The gym class for which the appointment is scheduled
    day = models.CharField(max_length=20)
    time = models.TimeField()  # Time of the appointment

    # Additional fields as per your requirements

    def __str__(self):
        return f"{self.user.username}'s Appointment for {self.gym_class.class_name} on {self.day} at {self.time}"