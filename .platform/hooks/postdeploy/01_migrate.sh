#!/usr/bin/env bash
source "${EB_VIRTUAL_ENV}/bin/activate"
cd "${EB_APP_CURRENT}"
python manage.py migrate --noinput