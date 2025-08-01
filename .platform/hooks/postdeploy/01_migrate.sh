#!/usr/bin/env bash
# elasticbeanstalk가 설치한 가상환경에 환경변수 로드
source /opt/elasticbeanstalk/.env
# (또는 /opt/elasticbeanstalk/support/envvars 가 존재하면 그걸로)

# 마이그레이션
/var/app/venv/*/bin/python manage.py migrate --noinput