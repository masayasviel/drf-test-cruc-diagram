import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.myproject.settings")

django.setup()
