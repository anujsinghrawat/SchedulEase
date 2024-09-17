from django.urls import path

from users.api.views import UsersViewSet, EventViewSet, SignupView, LoginView, RefreshTokenView

urlpatterns = [
    path('say_hi/', UsersViewSet.as_view({
        'get': 'say_hi',}), name='say_hi'),
    
    path('create_event_type/', EventViewSet.as_view({
        "post": "create_event_type"
    }), name='create_event_type'),

    path('create_event/', EventViewSet.as_view({
        "post": "create_event"
    }), name='create_event'),

    path('signup/', SignupView.as_view({
        "post": "sigup_user"
    }), name='sigup_user'),

    path('login/', LoginView.as_view({
        "post": "login_user"
    }), name='login_user'),

    path('get_user_events/', EventViewSet.as_view({
        "get": "get_user_events"
    }), name='get_user_events'),

]