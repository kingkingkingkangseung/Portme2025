#!/usr/bin/env bash
set -e

# 1) EB 가상환경 활성화 (플랫폼에 따라 경로가 다를 수 있으니 와일드카드 사용)
source /var/app/venv/*/bin/activate

# 2) 코드 디렉터리로 이동
cd /var/app/current

# 3) 마이그레이션, static 파일 수집
python manage.py migrate --noinput
python manage.py collectstatic --noinput
