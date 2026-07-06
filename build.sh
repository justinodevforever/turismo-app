#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email, password)
    print("Superusuário criado.")
else:
    print("Superusuário já existe ou variáveis não configuradas.")
EOF