#!/usr/bin/env bash

# 코드 위치 이동
cd /var/app/current

# 가상환경 활성화
source /var/app/venv/*/bin/activate

# 마이그레이션
python manage.py migrate --noinput
# 정적파일 수집
python manage.py collectstatic --noinput