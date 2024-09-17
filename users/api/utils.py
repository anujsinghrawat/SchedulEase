import pytz
import json
import os
import django

from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from users.api.data_utils import EventDataUtils, UserDataUtils, UserAvailabilitySlotDataUtils
from users.helpers.event_helper import EventHelper
from users.app_settings import DaysOfWeek

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

def get_credentials():
    creds = None
    if os.path.exists(settings.GOOGLE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_FILE)
            with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except json.JSONDecodeError:
            print("Token file is invalid. Regenerating token.")
            os.remove(settings.GOOGLE_TOKEN_FILE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', settings.GOOGLE_SCOPES)
            creds = flow.run_local_server(port=8000)
            with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
    print(creds.to_json())
    return creds

class UsersUtils:
    data_class = UserDataUtils()

    def create_user(self, **kwargs):
        """
        Create a new user
        :param name: Name of the user
        :param password: Password for the user
        :param email: Email of the user
        :return: Response message and status code
        """
        name = kwargs.get('name')
        password = kwargs.get('password')
        email = kwargs.get('email')
        if not all([name, password, email]):
            return {"error": "Missing required fields"}, 400
        if self.data_class.filter_users(email=email).exists():
            return {"error": "User with email already exists"}, 400
        user = self.data_class.create_user(name=name, email=email, password=password)
        return {"message": f"User '{user.name}' created successfully"}, 200


    def login_user(self, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        if not all([email, password]):
            return {"error": "Missing required fields"}, 400
        user = self.data_class.get_user(**{"email": email})
        if not user:
            return {"error": "User not found"}, 404
        if not user.check_password(password):
            return {"error": "Invalid credentials"}, 400
        if user.google_access_token and user.google_refresh_token:
            return {
                "message": "User logged in successfully with existing Google tokens.",
                "data": {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            }, status.HTTP_200_OK
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', setting.GOOGLE_SCOPES)
        creds = flow.run_local_server(port=8081)
        creds = creds.to_json()
        creds = json.loads(creds)
        self.data_class.update_user(user.id, **{
            "google_access_token": creds['token'],
            "google_refresh_token": creds['refresh_token']
        })
        return {
            "message": "User logged in successfully.",
            "data": {
                "user_id": user.id,
                "name": user.name,
                "email": user.email
            }
        }, status.HTTP_200_OK


class UserAvailabilitySlotUtils:
    data_class = UserAvailabilitySlotDataUtils()
    user_du = UserDataUtils()

    def create_availability_slot(self, **kwargs):
        user_id = kwargs.get('user_id')
        day_of_week = kwargs.get('day_of_week')
        if day_of_week_str not in DaysOfWeek.labels:
            return {"error": "Invalid day of week"}, 400
        day_of_week = DaysOfWeek[day_of_week_str.upper()].value
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        if start_time > end_time:
            return {"error": "Start time cannot be greater than end time"}, 400
        if not all([user_id, day_of_week, start_time, end_time]):
            return {"error": "Missing required fields"}, 400
        user = self.user_du.get_user(id=user_id)
        if not user:
            return {"error": f"User not found for the id: {user_id}"}, 404
        self.data_class.create_availability_slot(**{
            "user": user,
            "day_of_week": DayOfWeek[day_of_week].value,
            "start_time": start_time,
            "end_time": end_time
        })
        return {"message": "Availability slot created successfully"}, 200
    
    def get_availability_slots(self, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            return {"error": "Missing required fields"}, 400
        user = self.user_du.get_user(id=user_id)
        if not user:
            return {"error": f"User not found for the id: {user_id}"}, 404
        availability_slots = self.data_class.filter_availability_slots(user=user)
        if not availability_slots.exists():
            return {"message": "No availability slots found"}, 200
        slots = []
        for slot in availability_slots:
            slots.append({
                "day_of_week": slot.get_day_of_week_display(),
                "start_time": slot.start_time,
                "end_time": slot.end_time
            })
        return {"message": "Availability slots retrieved successfully", "data": slots}, 200



class EventUtils:
    data_class = EventDataUtils()
    event_helper = EventHelper()
    user_du = UserDataUtils()

    def get_user_events(self, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            return {"error": "Missing required fields"}, 400
        user = self.user_du.get_user(id=int(user_id[0]))
        if not user:
            return {"error": f"User not found for the id: {user_id}"}, 404
        credentials = Credentials(token=user.google_access_token, refresh_token=user.google_refresh_token)
        service = build('calendar', 'v3', credentials=credentials)
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            events = events_result.get('items', [])
            if not events:
                return {"message": "No upcoming events found"}, 200
            filtered_events = []
            for event in events:
                filtered_events.append({
                    "summary": event.get('summary'),
                    "description": event.get('description'),
                    "start_time": event['start'].get('dateTime', event['start'].get('date')),
                    "end_time": event['end'].get('dateTime', event['end'].get('date')),
                    "hangout_link": event.get('hangoutLink'),
                    "attendees": [attendee.get('email') for attendee in event.get('attendees', [])]
                })
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": "Failed to retrieve events"}, 500
        return {"message": "Events retrieved successfully", "data": filtered_events}, 200

    def create_event_type(self, user, **kwargs):
        name = kwargs.get('name')
        duration = kwargs.get('duration')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        if not all([name, duration, start_date, end_date]):
            return {"error": "Missing required fields"}, 400
        if self.data_class.filter_event_types(name=name, user=user).exists():
            return {"error": f"EventType with name {name} already exists"}, 400
        event_type = self.data_class.create_event_type(
            name=name, duration=duration, start_date=start_date, end_date=end_date, user=user
        )
        return {"message": f"EventType '{event_type.name}' created successfully"}, 200

    def create_event(self, **kwargs):
        event_type_id = kwargs.get('event_type_id')
        guest_email = kwargs.get('guest_email')
        description = kwargs.get('description')
        start_datetime = kwargs.get('start_datetime')
        end_datetime = kwargs.get('end_datetime')
        user_id = kwargs.get('user_id')
        if not all([event_type_id, guest_email, start_datetime, end_datetime]):
            return {"error": "Missing required fields"}, 400
        event_type = self.data_class.get_event_type(event_type_id)
        if not event_type:
            return {"error": "EventType not found"}, 404
        user = self.user_du.get_user(id=user_id)
        if not user:
            return {"error": f"User not found for the id: {user_id}"}, 404
        is_available = self.event_helper.check_user_availability(
            user, start_datetime, end_datetime)
        if not is_available:
            return {"error": "User is not available at this time"}, 400
        try:
            event_data = {
                'event_type': event_type.name,
                'guest_email': guest_email,
                'description': description,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'user': user,
                'timezone': 'Asia/Kolkata',
            }
            google_event_data, status = self.event_helper.create_google_event(event_data)
            if not status:
                return {
                    'code': 1,
                    'message': google_event_data['message']
                }, 400
            self.data_class.create_event(
                event_type=event_type,
                guest_email=guest_email,
                description=description,
                user=user,
                meet_link=google_event_data.get("google_meet_link")
            )
            return {
                'code': 0,
                "message": f"Event created successfully for {guest_email}",
                "google_meet_link": google_event_data.get("google_meet_link"),
                "calendar_event_link": google_event_data.get("calendar_event_link")
            }, 200
        except Exception as e:
            return {"error": f"An error occurred while creating the event: {e}"}, 400

