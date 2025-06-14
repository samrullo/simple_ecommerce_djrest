import os
import logging
import django

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

from django.core.mail import send_mail

send_mail(
    "Test Email",
    "This is a test.",
    "amrulloev.subhon@gmail.com",  # FROM
    ["nohbus.veollurma@gmail.com"],  # TO
    fail_silently=False,
)
