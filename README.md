# SchedulEase

SchedulEase is a scheduling application designed to help users manage their availability and events efficiently. This application allows users to create, update, and delete availability slots, manage their events, and integrate with Google Calendar for seamless scheduling.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Technologies](#technologies)

## Features

- **User Management**
  - Create new users.
  - User login with Google authentication.
- **Availability Management**
  - Create, update, and delete availability slots.
  - View available slots for a user.
- **Event Management**
  - Create event types.
  - Schedule and manage events.
  - Integration with Google Calendar to create events and get calendar links.

## API Endpoints

### User API

1. **Create User**

   - **URL:** `/api/users/create/`
   - **Method:** `POST`
   - **Request Body:**
     ```json
     {
       "name": "John Doe",
       "password": "securepassword123",
       "email": "john.doe@example.com"
     }
     ```
   - **Response:**
     ```json
     {
       "message": "User 'John Doe' created successfully"
     }
     ```

2. **Login User**

   - **URL:** `/api/users/login/`
   - **Method:** `POST`
   - **Request Body:**
     ```json
     {
       "email": "john.doe@example.com",
       "password": "securepassword123"
     }
     ```
   - **Response:**
     ```json
     {
       "message": "User logged in successfully.",
       "data": {
         "user_id": 1,
         "name": "John Doe",
         "email": "john.doe@example.com"
       }
     }
     ```

### User Availability Slot API

1. **Create Availability Slot**

   - **URL:** `/api/availability/create/`
   - **Method:** `POST`
   - **Request Body:**
     ```json
     {
       "user_id": 1,
       "day_of_week": "Tuesday",
       "start_time": "09:00:00",
       "end_time": "17:00:00"
     }
     ```
   - **Response:**
     ```json
     {
       "message": "Availability slot created successfully"
     }
     ```

2. **Get Availability Slots**

   - **URL:** `/api/availability/get/`
   - **Method:** `GET`
   - **Request Body:**
     ```json
     {
       "user_id": 1
     }
     ```
   - **Response:**
     ```json
     {
       "message": "Availability slots retrieved successfully",
       "data": [
         {
           "day_of_week": "Tuesday",
           "start_time": "09:00:00",
           "end_time": "17:00:00"
         }
       ]
     }
     ```

### Event API

1. **Create Event Type**

   - **URL:** `/api/events/create-type/`
   - **Method:** `POST`
   - **Request Body:**
     ```json
     {
       "name": "Meeting",
       "duration": "01:00:00",
       "start_date": "2024-09-01",
       "end_date": "2024-12-31",
       "user_id": 1
     }
     ```
   - **Response:**
     ```json
     {
       "message": "EventType 'Meeting' created successfully"
     }
     ```

2. **Create Event**

   - **URL:** `/api/events/create/`
   - **Method:** `POST`
   - **Request Body:**
     ```json
     {
       "event_type_id": 1,
       "guest_email": "guest@example.com",
       "description": "Project discussion",
       "start_datetime": "2024-09-20T10:00:00Z",
       "end_datetime": "2024-09-20T11:00:00Z",
       "user_id": 1
     }
     ```
   - **Response:**
     ```json
     {
       "code": 0,
       "message": "Event created successfully for guest@example.com",
       "google_meet_link": "https://meet.google.com/xyz-abc",
       "calendar_event_link": "https://calendar.google.com/event?eid=abc123"
     }
     ```

3. **Get User Events**

   - **URL:** `/api/events/get/`
   - **Method:** `GET`
   - **Request Body:**
     ```json
     {
       "user_id": 1
     }
     ```
   - **Response:**
     ```json
     {
       "message": "Events retrieved successfully",
       "data": [
         {
           "summary": "Meeting",
           "description": "Project discussion",
           "start_time": "2024-09-20T10:00:00Z",
           "end_time": "2024-09-20T11:00:00Z",
           "hangout_link": "https://meet.google.com/xyz-abc",
           "attendees": ["guest@example.com"]
         }
       ]
     }
     ```

## Getting Started

1. **Clone the repository:**
   ```sh
   git clone https://github.com/anujsinghrawat/schedulEase.git
   ```
2. **Create a virtual environment:**

   ```sh
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   cd schedulEase
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```sh
   python manage.py runserver
   ```

## Technologies

- **Backend:**
  - Django
  - Django REST framework
  - PostgreSQL
  - Google Calendar API
