#!/usr/bin/env bash
set -e

# 1) 애플리케이션이 설치된 디렉터리로 이동
cd /var/app/current

# 2) EB가 만든 가상환경 활성화
source /var/app/venv/*/bin/activate

# 3) 마이그레이션 실행
python manage.py migrate --noinput
