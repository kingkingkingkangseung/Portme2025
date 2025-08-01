#!/usr/bin/env bash
set -e

# EB_VIRTUAL_ENV는 EB가 자동으로 설정해 주는 환경변수입니다
source "${EB_VIRTUAL_ENV}/bin/activate"
cd "${EB_APP_CURRENT}"       # 앱 루트 디렉터리로 이동
python manage.py migrate --noinput