from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user

class AuditMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)   # Set once when created
    modified_at = models.DateTimeField(auto_now=True,null=True,blank=True)      # Updates on each save
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified_%(class)ss"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.modified_by = user
        super().save(*args, **kwargs)