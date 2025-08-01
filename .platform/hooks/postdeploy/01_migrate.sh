#!/usr/bin/env bash
set -e

# 1) 가상환경 활성화
source /var/app/venv/*/bin/activate

# 2) 환경 변수 로드 (EB가 설정한 envvars 파일이 없으면, 위에서 콘솔에 설정한 env가 반영됩니다)
#    만약 support/envvars 파일을 참조하고 있다면 주석 처리하거나 제거하세요.

# 3) 프로젝트 디렉토리로 이동
cd /var/app/current

# 4) 마이그레이션 수행
python manage.py migrate --noinput

# 5) (선택) static 파일 수집
python manage.py collectstatic --noinput