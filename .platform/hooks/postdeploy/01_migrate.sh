#!/usr/bin/env bash
# EB 인스턴스 환경 변수를 로드
source /opt/elasticbeanstalk/support/envvars

# Django 마이그레이션 수행
python3 manage.py migrate --noinput