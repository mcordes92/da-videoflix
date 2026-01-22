import uuid

from django.db import models
from django.contrib.auth.models import User

class UserTokenModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uidb64 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.user.email