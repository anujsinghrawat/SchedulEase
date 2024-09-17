from datetime import datetime, timezone, timedelta
import pytz

from django.db.models import Q

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from users.models import UserAvailabilitySlot

class EventHelper:

    def check_user_availability(self, user, start_datetime, end_datetime):
        """
        Checks if the user is available during the provided time range.
        It checks both Google Calendar events and the user's defined availability in the database.
        :param user: User instance
        :param start_datetime: Start datetime of the event as a string
        :param end_datetime: End datetime of the event as a string
        :return: True if available, False if a conflict exists
        """
        ist_zone = pytz.timezone('Asia/Kolkata')
        start_datetime = datetime.fromisoformat(start_datetime.replace('Z', '+05:30')).astimezone(ist_zone)
        end_datetime = datetime.fromisoformat(end_datetime.replace('Z', '+05:30')).astimezone(ist_zone)
        start_datetime_utc = start_datetime.astimezone(pytz.UTC)
        end_datetime_utc = end_datetime.astimezone(pytz.UTC)
        try:
            credentials = Credentials(token=user.google_access_token, refresh_token=user.google_refresh_token)
            service = build('calendar', 'v3', credentials=credentials)
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_datetime.isoformat(),
                timeMax=end_datetime.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                event_start = datetime.fromisoformat(event_start.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                event_end = datetime.fromisoformat(event_end.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                if start_datetime_utc <= event_end and end_datetime_utc >= event_start:
                    print(f"Event conflict found: {event['summary']} at {event_start} - {event_end}")
                    return False  
        except Exception as e:
            print(f"Error fetching Google Calendar events: {e}")
            return False
        start_time = start_datetime.time()
        end_time = end_datetime.time()
        day_of_week = start_datetime.weekday() + 1
        availability_slots = UserAvailabilitySlot.objects.filter(
            user=user,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time
        )
        if not availability_slots.exists():
            print(f"No availability slot found for {user.email} on {start_datetime.date()} from {start_time} to {end_time}")
            return False 
        return True


    def create_google_event(self, user, event_type, guest_email, description, start_datetime, end_datetime):
        """
        Creates an event in the user's Google Calendar.
        :param user: User instance
        :param event_type: The type of the event
        :param guest_email: Email of the guest
        :param description: Event description
        :param start_datetime: Start datetime of the event
        :param end_datetime: End datetime of the event
        :return: Google Meet link and calendar event link
        """
        try:
            ist_zone = pytz.timezone('Asia/Kolkata')
            start_datetime = datetime.fromisoformat(start_datetime.replace('Z', '+05:30')).astimezone(ist_zone).isoformat()
            end_datetime = datetime.fromisoformat(end_datetime.replace('Z', '+05:30')).astimezone(ist_zone).isoformat()
            credentials = Credentials(token=user.google_access_token, refresh_token=user.google_refresh_token)
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': event_type.name,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [
                    {'email': guest_email, 'responseStatus': 'needsAction'},
                    {'email': user.email, 'responseStatus': 'accepted'},
                ],
                'conferenceData': {
                    'createRequest': {
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        },
                        'requestId': 'sample123'
                    }
                },
            }
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            google_meet_link = created_event['conferenceData']['entryPoints'][0]['uri']
            calendar_event_link = created_event.get('htmlLink')
            return {
                'google_meet_link': google_meet_link,
                'calendar_event_link': calendar_event_link
            }, True
        except Exception as e:
            return {
                'message' : F"An error occurred while creating the event: {e}"
            }, False