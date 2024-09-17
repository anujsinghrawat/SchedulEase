from django.contrib.admin import ModelAdmin
from django.contrib import admin

# Register your models here.
from users.models import User, UserAvailabilitySlot, EventType, Event


class NoResultModelAdmin(ModelAdmin):
    show_full_result_count = False

@admin.register(User)
class UserAdmin(NoResultModelAdmin):
    list_display = [
        'name',
        'email',
        'country',
        'time_zone',
        'active',
        'created_at',
        'updated_at'
    ]
    search_fields = ['name', 'email']

@admin.register(UserAvailabilitySlot)
class UserAvailabilitySlotAdmin(NoResultModelAdmin):
    list_display = [
        'user',
        'day_of_week',
        'start_time',
        'end_time',
        'timezone'
    ]
    search_fields = ['user__name']

@admin.register(EventType)
class EventTypeAdmin(NoResultModelAdmin):
    list_display = [
        'name',
        'duration',
        'start_date',
        'end_date',
        'user'
    ]
    search_fields = ['name']

@admin.register(Event)
class EventAdmin(NoResultModelAdmin):
    list_display = [
        'event_type',
        'guest_email',
        'description',
        'user'
    ]
    search_fields = ['event_type__name', 'guest_email']
