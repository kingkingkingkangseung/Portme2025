#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────
# EB Python 3.13 on Amazon Linux 2023:
# 배포 후 자동으로 마이그레이션을 실행해 줍니다.
# ───────────────────────────────────────────────────────────────

# 앱 코드가 체크아웃된 디렉터리로 이동
cd /var/app/current

# 가상환경 활성화
source /var/app/venv/*/bin/activate

# 마이그레이션 실행
python manage.py migrate --noinput

# (필요시) static files collect
# python manage.py collectstatic --noinput