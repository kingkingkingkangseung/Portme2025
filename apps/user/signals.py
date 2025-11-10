from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    비밀번호 재설정 토큰이 만들어졌을 때 실행됨
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_password_token.key}"
    
    # 이메일 전송 실패가 API 응답을 망치지 않도록 안전하게 처리
    try:
        send_mail(
            subject="비밀번호 재설정 안내",
            message=f"아래 링크를 눌러 새 비밀번호를 설정하세요:\n\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reset_password_token.user.email],
            fail_silently=True,  # SMTP 오류가 나도 요청은 성공시키기
        )
    except Exception:
        # 로깅 시스템이 있다면 여기서 기록하세요 (Sentry/로그 등)
        pass
