from users.models import EventType, Event, User, UserAvailabilitySlot

class EventDataUtils:
    @staticmethod
    def filter_event_types(**kwargs):
        return EventType.objects.filter(**kwargs)

    @staticmethod
    def create_event_type(**kwargs):
        return EventType.objects.create(**kwargs)

    @staticmethod
    def get_event_type(event_type_id):
        try:
            return EventType.objects.get(id=event_type_id)
        except EventType.DoesNotExist:
            return None

    @staticmethod
    def create_event(**kwargs):
        return Event.objects.create(**kwargs)

class UserDataUtils:
    @staticmethod
    def filter_users(**kwargs):
        return User.objects.filter(**kwargs)

    @staticmethod
    def create_user(**kwargs):
        user = User(**kwargs) 
        user.set_password(kwargs['password'])
        user.save()  
        return user 

    @staticmethod
    def get_user(**user_filter):
        try:
            return User.objects.get(**user_filter)
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_user(user_id, **kwargs):
        return User.objects.filter(id=user_id).update(**kwargs)
        
class UserAvailabilitySlotDataUtils:
    @staticmethod
    def filter_user_availability_slots(**kwargs):
        return UserAvailabilitySlot.objects.filter(**kwargs)

    @staticmethod
    def create_user_availability_slot(**kwargs):
        return UserAvailabilitySlot.objects.create(**kwargs)
    
    @staticmethod
    def get_user_availability_slot(user_availability_slot_id):
        try:
            return UserAvailabilitySlot.objects.get(id=user_availability_slot_id)
        except UserAvailabilitySlot.DoesNotExist:
            return None

    @staticmethod
    def update_user_availability_slot(user_availability_slot_id, **kwargs):
        return UserAvailabilitySlot.objects.filter(id=user_availability_slot_id).update(**kwargs)

    @staticmethod
    def delete_user_availability_slot(user_availability_slot_id):
        return UserAvailabilitySlot.objects.filter(id=user_availability_slot_id).delete()