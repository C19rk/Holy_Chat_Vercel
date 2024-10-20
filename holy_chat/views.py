from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Item, Group, Notification, ChatMessage
import json

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

def homepage(request):
    return render(request, 'homepage.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation for password
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif len(password1) < 8:
            messages.error(request, "Password is too short. It must contain at least 8 characters.")
        elif password1 in ['password', '12345678', 'qwerty']:
            messages.error(request, "Password is too common.")
        else:
            # Check for existing username
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose another.")
            else:
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=password1
                    )
                    messages.success(request, "Registration successful. You can now log in.")
                    return redirect('login')  # Redirect to login after successful registration
                except ValidationError as e:
                    messages.error(request, str(e))

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def forbidden(request):
    return render(request, 'forbidden.html')

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        # Fetch the groups associated with the user
        groups = Group.objects.filter(members=request.user)

        # Fetch all groups
        all_groups = Group.objects.all()
        
        # Fetch all registered users except the current user
        registered_users = User.objects.exclude(id=request.user.id)

        # Get the count of unread notifications
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

        return render(request, 'dashboard.html', {
            'groups': groups,
            'all_groups': all_groups,  # Add this line
            'unread_notifications_count': unread_notifications_count,
            'registered_users': registered_users  # Pass registered users to the template
        })
    return redirect('login')

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        members_usernames = request.POST.get('members')  # Get members field

        # Check if group_name is provided
        if not group_name:
            messages.error(request, "Group name is required.")
            return redirect('dashboard')

        # Create the group and assign the creator as admin
        group = Group.objects.create(name=group_name, admin=request.user)  # Change 'creator' to 'admin'
        group.members.add(request.user)  # Add the creator as a member

        # Check if members_usernames is provided and split if it exists
        if members_usernames:
            # Split by commas and strip whitespace
            members_usernames = [username.strip() for username in members_usernames.split(',')]

            for username in members_usernames:
                try:
                    user = User.objects.get(username=username)
                    group.members.add(user)  # Add the specified user to the group
                except User.DoesNotExist:
                    messages.error(request, f"User with username '{username}' does not exist.")

        # Save the group, although not necessary since create() does this
        group.save()  
        messages.success(request, "Group created successfully!")  # Add a success message
        return redirect('dashboard')  # Redirect to the dashboard after creation

    return render(request, 'create_group.html')  # Render the group creation form

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if the logged-in user is the admin of the group
    if request.user == group.admin:  # Change 'creator' to 'admin'
        if request.method == 'POST':  # After confirmation modal
            group.delete()
            messages.success(request, 'Group deleted successfully!')
            return redirect('dashboard')
    else:
        messages.error(request, 'Only the group admin can delete the group.')
        return redirect('dashboard')

    return render(request, 'group_confirm_delete.html', {'group': group})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Group, ChatMessage

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages = ChatMessage.objects.filter(group=group)

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        file_data = request.FILES.get('file_data')  # Get the uploaded file

        try:
            if file_data:
                message_text = file_data.name
            
            message = ChatMessage(
                group=group,
                user=request.user,
                message=message_text if message_text else None,
                file_data=file_data  
            )
            message.save()

            response_data = {
                'status': 'Message saved successfully',
                'message': message_text,
                'file_url': message.file_data.url if file_data else None,  # Pass the file URL
                'username': request.user.username,
                'timestamp': message.timestamp.isoformat(),
                'message_id': message.id,  # Add message ID for deletion
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'group_detail.html', {'group': group, 'messages': messages})


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user == group.admin:
        # If the admin is leaving, transfer ownership or delete the group
        group.members.remove(request.user)
        if group.members.exists():
            group.transfer_ownership()
            messages.success(request, "You have left the group. Ownership has been transferred.")
        else:
            group.delete()  # Delete group if no members left
            messages.success(request, "You were the last member. The group has been deleted.")
    else:
        # If a non-admin member is leaving
        group.members.remove(request.user)
        messages.success(request, "You have left the group.")

    return redirect('dashboard')

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'notifications.html', {'notifications': user_notifications})

@login_required
def accept_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if request.user == notification.group.admin:
        group = notification.group
        group.members.add(notification.user)  # Add the user to the group
        notification.delete()  # Remove the notification
        messages.success(request, f"{notification.user.username} has been added to the group.")
        return redirect('notifications')  # Redirect to notifications or group detail

    messages.error(request, 'You do not have permission to accept this request.')
    return redirect('notifications')


@login_required
def deny_request(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if request.user == notification.group.admin:
        notification.delete()  # Remove the notification
        messages.success(request, f"The request from {notification.user.username} has been denied.")
        return redirect('notifications')  # Redirect to notifications or group detail

    messages.error(request, 'You do not have permission to deny this request.')
    return redirect('notifications')

@login_required
def join_by_invite(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        
        # Fetch the group using the invite code
        group = Group.objects.filter(invite_code=invite_code).first()

        if group:
            # Check if the user is already a member
            if request.user in group.members.all():
                messages.error(request, "You are already a member of this group.")
            else:
                group.members.add(request.user)  # Add the user to the group
                messages.success(request, f"You have successfully joined the group '{group.name}'!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid invite code. Please check the code and try again.")
            return redirect('join_by_invite')
    
    return render(request, 'join_by_invite.html')

def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        user = request.user
        image = request.FILES.get('image') if 'image' in request.FILES else None
        video = request.FILES.get('video') if 'video' in request.FILES else None
        file = request.FILES.get('file')
        
        message_instance = ChatMessage.objects.create(message=message_text, file=file)

        chat_message = ChatMessage.objects.create(user=user, message=message_text, image=image, video=video)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

@login_required
def get_messages(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages = ChatMessage.objects.filter(group=group).order_by('timestamp')
    message_list = [{'user': message.user.username, 'message': message.message} for message in messages]
    return JsonResponse({'messages': message_list})

@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        try:
            message = ChatMessage.objects.get(id=message_id, user=request.user)
            message.delete()
            return JsonResponse({'success': True})
        except ChatMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found or not authorized'})
        
        