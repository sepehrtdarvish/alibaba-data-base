from django.db import models
import uuid

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)