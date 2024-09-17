from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.conf import settings

from users.models import User

class UserHelper:

    def refresh_google_access_token(self, user_id):
        user = User.objects.get(id=user_id)
        if not user:
            return {"error": "User not found"}, False
        if not user.google_refresh_token:
            return {"error": "No Google refresh token available"}, False
        try:
            creds = Credentials(
                None, 
                refresh_token=user.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            User.objects.filter(id=user_id).update(google_access_token=creds.token)
            return {
                "message": "Google access token refreshed successfully",
                "data": {
                    "access_token": creds.token,
                    "expires_at": creds.expiry.isoformat(),
                }
            }, True
        except Exception as e:
            return {"error": f"Failed to refresh Google access token: {str(e)}"}, False