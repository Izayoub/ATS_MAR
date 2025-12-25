# ai_engine/__init__.py
import os
import django
from django.conf import settings

# Configure Django if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')
    django.setup()