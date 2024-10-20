import uuid
from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="group_members")
    admin = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="admin_groups")
    invite_code = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Add invite code

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = str(uuid.uuid4())[:10]  # Generate a 10-character invite code
        super().save(*args, **kwargs)

    def transfer_ownership(self):
        if self.members.exists():
            new_admin = self.members.first()
            self.admin = new_admin
            self.save()
        else:
            self.delete()

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, null=True)  # Make notification_type nullable
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="messages", on_delete=models.CASCADE, null=True)  # Make it nullable
    message = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    file_data = models.FileField(upload_to='uploads/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message or self.file.name}"

