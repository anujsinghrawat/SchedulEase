import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

from users.app_settings import DaysOfWeek

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    name = models.CharField(max_length=100)
    profile_picture_url = models.URLField(null=True, blank=True)
    welcome_message = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=3, null=True, blank=True)
    time_zone = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, default=None)
    active = models.BooleanField(default=True)
    google_access_token = models.CharField(default=None, null=True, blank=True)
    google_refresh_token = models.CharField(default=None, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True


def validate_time_interval(start_time, end_time):
    if end_time <= start_time:
        raise ValidationError("End time must be after start time")
    
    duration = datetime.datetime.combine(datetime.date.today(), end_time) - \
            datetime.datetime.combine(datetime.date.today(), start_time)
    if duration.total_seconds() % 3600 != 0:
        raise ValidationError("Time duration must be in multiples of 1 hour")


def check_for_overlaps(user, day_of_week, start_time, end_time):
    overlapping_slots = UserAvailabilitySlot.objects.filter(
        user=user,
        day_of_week=day_of_week,
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    if overlapping_slots.exists():
        raise ValidationError("This availability slot overlaps with an existing one")

class UserAvailabilitySlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DaysOfWeek.choices)  # Day of the week
    start_time = models.TimeField()  # Start time for the slot
    end_time = models.TimeField()  # End time for the slot
    timezone = models.CharField(max_length=100, default="UTC")  # Store timezone, default to UTC

    class Meta:
        unique_together = ('user', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"

    def clean(self):
        validate_time_interval(self.start_time, self.end_time)
        check_for_overlaps(self.user, self.day_of_week, self.start_time, self.end_time)


class EventType(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField() 
    start_date = models.DateField()  
    end_date = models.DateField() 
    user = models.ForeignKey(User, on_delete=models.CASCADE) 

    def __str__(self):
        return self.name


class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE) 
    guest_email = models.EmailField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    meet_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Event for {self.guest_email} ({self.event_type.name})"
