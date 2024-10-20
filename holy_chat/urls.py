from django.urls import path
from .views import (
    homepage, register, user_login, dashboard, forbidden, 
    create_group, delete_group, group_detail, leave_group,
    notifications, accept_request, deny_request, join_by_invite,
    delete_message, send_message
)
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', homepage, name='homepage'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('forbidden/', forbidden, name='forbidden'),
    path('create-group/', create_group, name='create_group'),
    path('delete-group/<int:group_id>/', delete_group, name='delete_group'),
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('leave-group/<int:group_id>/', leave_group, name='leave_group'),
    path('notifications/', notifications, name='notifications'),
    path('accept_request/', accept_request, name='accept_request'),
    path('deny_request/', deny_request, name='deny_request'),
    path('join-by-invite/', join_by_invite, name='join_by_invite'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('send_message/<int:group_id>/', send_message, name='send_message'),
]