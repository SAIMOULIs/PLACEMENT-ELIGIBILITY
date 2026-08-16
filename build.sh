#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py makemigrations placements --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
