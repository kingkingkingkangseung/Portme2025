#!/usr/bin/env bash

# RDS, EB 환경변수 로딩
source /opt/elasticbeanstalk/support/envvars

# 앱 코드가 체크아웃된 디렉터리로 이동
cd /var/app/current

# 가상환경 활성화
source /var/app/venv/*/bin/activate

# 마이그레이션 실행
python manage.py migrate --noinput

# 필요하다면 스태틱 수집
# python manage.py collectstatic --noinput